# DHBW Technik Studienassistent – Streamlit MVP

Das MVP liest öffentliche HTML- und PDF-Quellen der Fakultät Technik der DHBW
Heidenheim ein, durchsucht sie lokal und beantwortet Fragen mit Fundstellen.
Die Aktualisierung kann jederzeit in der Streamlit-Oberfläche ausgelöst werden.

## Start unter Windows/PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

Ohne `OPENROUTER_API_KEY` zeigt das Projekt den relevantesten Quellenausschnitt.
Mit einem Schlüssel in `.env` erzeugt `openrouter/free` eine formulierte Antwort.

## MVP-Ablauf

1. In der Seitenleiste **Quellen jetzt aktualisieren** wählen.
2. Warten, bis HTML-Seiten und verlinkte PDFs verarbeitet wurden.
3. Im Chat beispielsweise nach Prüfungsleistungen oder Modulinhalten fragen.
4. Die angegebene Originalquelle kontrollieren.

## Grenzen

- Der lokale Retriever verwendet für das MVP TF-IDF statt Qdrant/Embeddings.
- Scan-PDFs werden nicht per OCR verarbeitet.
- Die manuelle Aktualisierung demonstriert die dynamische Pipeline; ein täglicher
  Scheduler kann anschließend dieselbe `crawl`-Funktion aufrufen.
- Es werden nur erlaubte DHBW-Domains und höchstens `MAX_PAGES` URLs verarbeitet.
