# Prompt: Due Diligence Casa All'Asta

Usa questo prompt per analizzare in dettaglio una casa all'asta.
Allega anche la perizia come testo se disponibile.

---

```text
Agisci come consulente immobiliare + legale specializzato in aste giudiziarie italiane.

Analizza questa casa all'asta:

- Tribunale: {{tribunale}}
- Città/Zona: {{zona}}
- Prezzo base: {{prezzo_base}} €
- Offerta minima: {{offerta_minima}} €
- Data asta: {{data_asta}}
- Occupato: {{occupato}}
- Link perizia: {{link_perizia}}
- Testo perizia (se disponibile): {{testo_perizia}}

Task:

1. Il discount d'asta è reale o solo nominalmente alto?
2. Quali sono i principali rischi:
   - giuridici (ipoteche residue, contestazioni)
   - tecnici (abusi edilizi, difformità catastali)
   - commerciali (occupazione, costi di liberazione)
3. Calcola costo totale all-in stimato:
   - offerta
   - imposte (2% prima casa o 9% seconda)
   - spese procedura
   - eventuali sanatorie o regolarizzazioni
   - costi ristrutturazione
   - costi liberazione immobile se occupato
4. Stima il valore post-intervento o di mercato attuale.
5. Calcola margine di sicurezza.
6. Qual è l'offerta massima oltre cui non conviene andare?
7. Classifica il rischio:
   - basso / medio / alto / molto alto
8. Conclusione:
   - conviene
   - conviene solo a sconto forte
   - non conviene

Regole:
- Non inventare dati assenti: elencali.
- Sii conservativo nelle stime di costo.
- Differenzia dati certi, stime, ipotesi.

Output:
**A. Sintesi asta**
**B. Discount reale stimato**
**C. Rischi principali (giuridici / tecnici / commerciali)**
**D. Costo totale all-in**
**E. Valore stimato**
**F. Offerta massima consigliata**
**G. Livello di rischio**
**H. Conclusione**
```
