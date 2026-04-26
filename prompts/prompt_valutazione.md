# Prompt: Valutazione Immobile (Generico)

Usa questo prompt in ChatGPT / Claude / Copilot per valutare un singolo immobile.
Sostituisci i campi `{{...}}` con i dati reali.

---

```text
Agisci come analista immobiliare senior specializzato nel mercato italiano.

Analizza questa proprietà:

- Città: {{city}}
- Zona: {{zona}}
- Link: {{link}}
- Prezzo: {{prezzo}} €
- Prezzo €/mq: {{prezzo_mq}} €/mq
- Mq: {{mq}}
- Piano: {{piano}}
- Ascensore: {{ascensore}}
- Spese condominiali: {{spese}} €/mese
- Classe energetica: {{classe_energetica}}
- Stato immobile: {{stato}}
- Occupato: {{occupato}}
- Comparabile medio zona: {{comparabile_avg}} €/mq
- Sconto stimato rispetto mercato: {{discount}}
- Note aggiuntive: {{note}}

Task:
1. Valuta se il prezzo €/mq è coerente con la zona.
2. Identifica punti di forza e criticità.
3. Assegna punteggio 0-100 a:
   - posizione
   - qualità immobile
   - convenienza economica
   - liquidabilità/rivendibilità
   - rischio complessivo
4. Calcola score finale pesato (0-100).
5. Fornisci range di valore stimato min/max.
6. Fornisci range di offerta:
   - aggressiva
   - realistica
   - massima oltre cui non andare
7. Verdetto: scarta / monitora / approfondisci / fai offerta.

Regole:
- Non inventare dati mancanti: elencali.
- Sii preciso e numerico, non generico.
- Evidenzia red flag in modo chiaro.

Output:
**A. Sintesi** (4 righe)
**B. Punteggi**
**C. Red flag**
**D. Range valore stimato**
**E. Range offerta consigliata**
**F. Verdetto finale**
**G. Confidenza analisi: bassa / media / alta**
```
