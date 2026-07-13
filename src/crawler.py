from __future__ import annotations

import hashlib
import io
import re
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from urllib.parse import urldefrag, urljoin, urlparse

import fitz
import requests
from bs4 import BeautifulSoup

ALLOWED_HOSTS = {"www.heidenheim.dhbw.de", "heidenheim.dhbw.de", "www.dhbw.de", "dhbw.de"}
USER_AGENT = "DHBW-Technik-Studienassistent-MVP/0.1 (student project)"


@dataclass
class Document:
    source_id: str
    title: str
    url: str
    text: str
    page: int | None
    fetched_at: str
    content_hash: str

    def to_dict(self) -> dict:
        return asdict(self)


def _allowed(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.hostname in ALLOWED_HOSTS


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _document(title: str, url: str, text: str, page: int | None = None) -> Document:
    cleaned = _clean_text(text)
    identity = f"{url}#page={page or 0}"
    return Document(
        source_id=hashlib.sha256(identity.encode()).hexdigest()[:20],
        title=title or url,
        url=url,
        text=cleaned,
        page=page,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        content_hash=hashlib.sha256(cleaned.encode()).hexdigest(),
    )


def _parse_pdf(content: bytes, url: str) -> list[Document]:
    result: list[Document] = []
    with fitz.open(stream=io.BytesIO(content), filetype="pdf") as pdf:
        title = pdf.metadata.get("title") or url.rsplit("/", 1)[-1]
        for number, page in enumerate(pdf, start=1):
            text = page.get_text("text")
            if len(_clean_text(text)) >= 80:
                result.append(_document(title, url, text, number))
    return result


def _parse_html(content: bytes, url: str) -> tuple[Document | None, list[str]]:
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "form", "noscript"]):
        tag.decompose()
    title = _clean_text(soup.title.get_text(" ")) if soup.title else url
    main = soup.find("main") or soup.find(id="content") or soup.body or soup
    text = main.get_text(" ", strip=True)
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        target = urldefrag(urljoin(url, anchor["href"]))[0]
        if _allowed(target):
            links.append(target)
    doc = _document(title, url, text) if len(_clean_text(text)) >= 120 else None
    return doc, links


def crawl(seed_urls: tuple[str, ...], max_pages: int = 12) -> tuple[list[Document], list[str]]:
    """Crawl a small allow-listed DHBW source set and return documents and warnings."""
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    queue = deque(url for url in seed_urls if _allowed(url))
    visited: set[str] = set()
    documents: list[Document] = []
    warnings: list[str] = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            response = session.get(url, timeout=20)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").lower()
            if "pdf" in content_type or urlparse(url).path.lower().endswith(".pdf"):
                documents.extend(_parse_pdf(response.content, url))
            elif "html" in content_type:
                doc, links = _parse_html(response.content, url)
                if doc:
                    documents.append(doc)
                for link in links:
                    path = urlparse(link).path.lower()
                    if ("technik" in path or "dokument" in path or path.endswith(".pdf")) and link not in visited:
                        queue.append(link)
        except Exception as exc:  # The UI should continue when one source fails.
            warnings.append(f"{url}: {exc}")
    return documents, warnings

