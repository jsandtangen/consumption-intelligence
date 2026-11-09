# Verifikasjon av restruktureringen

Utført 9. november 2026 i den eksisterende branchen. Kontroller gjelder filorganisering, bevart faglig innhold, dataflyt og notebookenes inngangsdata. Modellresultatene er tidligere lagrede resultater.

## Bevaring

| Kontroll | Resultat |
| --- | --- |
| Seks notebooker sammenlignet med Git-versjonen før restrukturering | Alle 206 opprinnelige kodeceller bevart i samme innbyrdes rekkefølge |
| Vitenskapelig kode | Uendret, bortsett fra prosjektrotoppslag og nye innlesingsstier |
| Lagrede notebookresultater | Alle 194 utdataelementer og opprinnelige kjøringstellere identiske |
| Opprinnelig versjonerte PNG-er | Alle 23 bildefiler finnes med identisk SHA-256 under nye navn/stier |
| CSV-sammendrag av originalen | Alle sju bevart med identisk innhold; Git-normalisering av linjeskift er tatt hensyn til |
| Original råfil | SHA-256 samsvarer med den tidligere originalrapporten |

Råfilens kontrollerte SHA-256:

```text
813f35e83ed484a14eb33d3def0bb178e782c77385313924bcbc23e5c504bf70
```

Tretten gamle PNG-eksporter fra notebook 01–03 ble erstattet av identiske bilder med oppdaterte filnavn. Dette fjernet bare duplikater. De lokale CSV-filene er flyttet uten innholdsendringer.

## Kjørte kontroller

- Alle seks notebooker består `nbformat.validate`.
- Python-skriptene og alle notebookenes kodeceller er syntaktisk kontrollert.
- Alle kodeceller har en foranstilt Markdown-forklaring med hva, hvorfor og utbytte.
- De fire aktive notebookenes kildehash samsvarer med de oppdaterte dokumentasjonseksportene.
- Modellrapportens interne cellelenker peker til eksisterende celler i vedlegget.
- Lokale Markdown-lenker og bildereferanser er kontrollert mot den nye filstrukturen.
- Dokumentasjonseksporten er kjørt og har oppdatert cellevedlegg og PNG-er uten å kjøre analysene.
- Profileringen er kjørt på det eksisterende rådatautvalgets 5 000 rader og produserer rapport samt sju CSV-sammendrag i en midlertidig mappe.
- Integrasjonstesten i `tests/test_data_pipeline.py` består. Den kjører preprosessering over flere biter, kontrollerer sommertidsovergangen, bevarer negative verdier og ledende null i kommunenummer, fjerner bare den definerte Orkland-ekstremen, velger riktige kommuner og nekter overskriving. Rådata og mellomfil forblir uendret.
- Prosjektets avhengigheter er installert i `.venv`; `uv pip check` rapporterer kompatible pakker. NumPy, pandas, scikit-learn, Seaborn og notebookbibliotekene kan importeres.

## Kontroll på faktisk modellgrunnlag

Innlesing, feature engineering og dataklargjøring i notebook 04 er kjørt på den flyttede `consumption_selected.csv`, uten å endre notebookens lagrede utdata.

| Kontrollpunkt | Verifisert antall rader |
| --- | ---: |
| Kommuneutvalg før historikkfiltrering | 1 115 970 |
| Komplett modellgrunnlag | 1 110 630 |
| Trening 2022–2024 | 761 580 |
| Validering 2025 | 262 740 |
| Test januar–april 2026 | 86 310 |

Tallene samsvarer med de lagrede analysene. For hver av `LAG_3D`, `LAG_7D` og `MEAN_3D` er 1 000 valideringsrader kontrollert mot uavhengig aggregerte kildeverdier, uten avvik. Denne kontrollen bruker grupperte oppslag framfor notebookens langsommere radvise stikkprøveløkker.

Notebookens dato- og tilgjengelighetskontroller er kjørt på hele modellgrunnlaget. Begge lagdatoer har null tidsoverskridelser. For alle tre historiske variabler er det null manglende sluttider og null observasjoner tilgjengelige ved eller etter prognosetidspunktet, under den eksisterende antakelsen om én times publiseringsforsinkelse. Dette bekrefter ikke faktiske publiseringstider.

## Avgrensning

Full preprosessering av omtrent 40 millioner rader, komplett EDA og ny modelltrening med tuning er ikke kjørt under restruktureringen. Den separate mellomfilen før rensing må genereres før notebook 02 kjøres på nytt; se [reproduksjonsveiledningen](../docs/reproduction.md). Ingen nye modellresultater er utledet eller presentert som en ny uavhengig evaluering.

Det testede miljøet gir en NumPy-advarsel om eksisterende timedelta-operasjoner i historikkoden. Dette har ikke endret de kontrollerte radantallene; advarselen gjelder framtidig bibliotekkompatibilitet.
