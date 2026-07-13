from src.crawler import Document
from src.knowledge import search


def test_search_returns_relevant_document():
    documents = [
        Document("1", "Prüfungsordnung", "https://example.test/po", "Die Klausur dauert 90 Minuten.", 3, "now", "a"),
        Document("2", "Kontakt", "https://example.test/kontakt", "Das Sekretariat ist montags geöffnet.", None, "now", "b"),
    ]
    hits = search("Wie lange dauert die Klausur?", documents)
    assert hits
    assert hits[0].document.title == "Prüfungsordnung"
