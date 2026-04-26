# 🏠 AI Agente — Aste Immobiliari Italia

Agente IA per ricerca automatica, valutazione economica e due diligence di **case all'asta** in Italia, con focus su **Bari** e **Torino**.

---

## 📌 Cosa fa questo progetto

- Raccoglie annunci aste da PVP, PortaleAste, Idealista
- Normalizza i dati in un CSV unificato
- Calcola €/mq, sconto rispetto a comparabili di zona
- Assegna score su posizione, qualità, convenienza e rischio
- Genera prompt AI per valutazione LLM (ChatGPT/Claude/Copilot)
- Esporta report con verdetto: scarta / monitora / approfondisci / offerta

---

## 📁 Struttura progetto

```
ai-aste-immobiliari-agent/
├── README.md
├── requirements.txt
├── config/
│   └── criteri.yaml          # Criteri per Bari e Torino
├── data/
│   ├── raw/                  # CSV annunci grezzi
│   └── output/               # CSV elaborati e report
├── prompts/
│   ├── prompt_valutazione.md         # Prompt valutazione LLM
│   ├── prompt_asta_due_diligence.md  # Prompt due diligence asta
│   ├── prompt_bari.md                # Prompt specifico Bari
│   └── prompt_torino.md              # Prompt specifico Torino
├── scripts/
│   ├── 01_normalizza_dati.py         # Pulizia e normalizzazione CSV
│   ├── 02_calcola_score.py           # Scoring e comparabili
│   ├── 03_genera_report.py           # Export report finale
│   └── utils.py                      # Funzioni comuni
└── examples/
    ├── aste_bari_esempio.csv
    └── aste_torino_esempio.csv
```

---

## 🚀 Quick Start

### 1. Installa dipendenze

```bash
pip install -r requirements.txt
```

### 2. Inserisci dati grezzi

Crea file CSV nella cartella `data/raw/` con questi campi minimi:

```csv
city,zona,link,prezzo,mq,offerta_minima,astato,occupato,piano,ascensore,spese,classe_energetica,link_perizia,note
```

### 3. Esegui pipeline

```bash
python scripts/01_normalizza_dati.py
python scripts/02_calcola_score.py
python scripts/03_genera_report.py
```

### 4. Usa i prompt

Copia il prompt da `prompts/prompt_valutazione.md`, incolla in ChatGPT/Claude/Copilot sostituendo i `{{campi}}` con i dati del tuo CSV.

---

## 🔑 Fonti per raccolta aste

| Fonte | URL | Note |
|---|---|---|
| PVP Ministero Giustizia | https://pvp.giustizia.it/pvp | Fonte ufficiale obbligatoria |
| PortaleAste | https://www.portaleaste.com | Aste + documenti online |
| AsteGiudiziarie | https://www.astegiudiziarie.it | Ricerca per provincia |
| Idealista Aste | https://www.idealista.it | Filtro aste giudiziarie |
| AsteAnnunci | https://www.asteannunci.it | Aste Bari e provincia |

---

## 🧠 Crediti

Progetto sviluppato con AI-assisted development (Codex + ChatGPT + Claude).
