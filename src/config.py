from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    seed_urls: tuple[str, ...]
    max_pages: int
    openrouter_api_key: str
    openrouter_model: str


def get_settings() -> Settings:
    raw_urls = os.getenv(
        "DHBW_SEED_URLS",
        "https://www.heidenheim.dhbw.de/duales-studium-informatik,"
        "https://www.heidenheim.dhbw.de/studienangebot/bachelor#cat-3,"
        "https://www.heidenheim.dhbw.de/service-einrichtungen/dokumente-downloads,"
        "https://www.heidenheim.dhbw.de/startseite,"
        "https://www.heidenheim.dhbw.de/service-einrichtungen/"
        "dokumente-downloads/maschinenbau",
    )
    return Settings(
        seed_urls=tuple(url.strip() for url in raw_urls.split(",") if url.strip()),
        max_pages=max(1, min(int(os.getenv("MAX_PAGES", "12")), 50)),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "").strip(),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openrouter/free").strip(),
    )
