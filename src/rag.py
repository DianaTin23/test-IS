from __future__ import annotations

import requests

from .knowledge import Hit


def _source_label(hit: Hit, index: int) -> str:
    page = f", Seite {hit.document.page}" if hit.document.page else ""
    return f"[{index}] {hit.document.title}{page} – {hit.document.url}"


def answer(question: str, hits: list[Hit], api_key: str, model: str) -> str:
    if not hits:
        return "Dazu wurde in der aktuellen Datenbasis keine belastbare Information gefunden."

    if not api_key:
        best = hits[0].document.text
        excerpt = best[:900].rsplit(" ", 1)[0]
        return (
            "**Lokaler Testmodus (ohne Sprachmodell):**\n\n"
            f"{excerpt} …\n\n"
            f"**Fundstelle:** {_source_label(hits[0], 1)}"
        )

    context = "\n\n".join(
        f"QUELLE {index}: {_source_label(hit, index)}\n{hit.document.text[:3500]}"
        for index, hit in enumerate(hits, start=1)
    )
    prompt = f"""Beantworte die Frage ausschließlich anhand der Quellen.
Antworte auf Deutsch, knapp und sachlich. Belege jede wesentliche Aussage mit [1], [2] usw.
Wenn die Quellen nicht ausreichen oder sich widersprechen, sage das ausdrücklich.

Frage: {question}

{context}"""
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1},
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()["choices"][0]["message"]["content"]
    sources = "\n".join(f"- {_source_label(hit, i)}" for i, hit in enumerate(hits, start=1))
    return f"{body}\n\n**Verwendete Quellen**\n{sources}"

