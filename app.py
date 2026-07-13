from __future__ import annotations

import streamlit as st

from src.config import get_settings
from src.crawler import crawl
from src.knowledge import load_documents, save_documents, search
from src.rag import answer

st.set_page_config(page_title="DHBW Technik Studienassistent", page_icon="🎓", layout="wide")
settings = get_settings()

st.title("🎓 DHBW Technik Studienassistent")
st.caption("MVP für öffentliche Quellen der Fakultät Technik, DHBW Heidenheim")

with st.sidebar:
    st.header("Datenbasis")
    documents = load_documents()
    st.metric("Indexierte Abschnitte/Seiten", len(documents))
    mode = "OpenRouter" if settings.openrouter_api_key else "Lokaler Testmodus"
    st.write(f"Antwortmodus: **{mode}**")
    if st.button("Quellen jetzt aktualisieren", type="primary", use_container_width=True):
        with st.spinner("DHBW-Quellen werden eingelesen …"):
            new_documents, warnings = crawl(settings.seed_urls, settings.max_pages)
            if new_documents:
                save_documents(new_documents)
                documents = new_documents
                st.success(f"{len(documents)} Abschnitte/Seiten gespeichert.")
            else:
                st.error("Es konnten keine Inhalte geladen werden; der vorhandene Index bleibt erhalten.")
            for warning in warnings[:5]:
                st.warning(warning)
    st.divider()
    st.caption("Keine rechtsverbindliche Studienberatung. Antworten immer anhand der Originalquelle prüfen.")

if not documents:
    st.info("Die Datenbasis ist leer. Klicke links auf **Quellen jetzt aktualisieren**.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Frage zum Technikstudium in Heidenheim …", disabled=not documents)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Quellen werden durchsucht …"):
            try:
                response = answer(
                    question,
                    search(question, documents),
                    settings.openrouter_api_key,
                    settings.openrouter_model,
                )
            except Exception as exc:
                response = f"Die Antwort konnte nicht erzeugt werden: `{exc}`"
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
