# Consumption Intelligence

Prognoser for timebasert strømforbruk i norske kommuner. Prosjektet undersøker hvor mye historisk forbruk forbedrer kalenderbaserte prognoser, og sammenligner lineær regresjon, Ridge, Random Forest og Gradient Boosting med enkle baselines.

Datagrunnlaget inneholder omtrent 40 millioner observasjoner fra februar 2022 til april 2026. Modelleringen bruker ti kommuner og tre forbruksgrupper: Forretning, Industri og Privat. Målet er `VOLUM_KWH` per kommune, forbruksgruppe og time.

## Start her

1. Les [arbeidsflyten og dataoversikten](docs/workflow.md).
2. Følg [notebook 01](notebooks/01_data_preparation.ipynb) → [02](notebooks/02_data_quality.ipynb) → [03](notebooks/03_exploratory_analysis.ipynb) → [04](notebooks/04_forecasting.ipynb).
3. Se [resultatoversikten](reports/forecasting/README.md) og [full metode- og resultatrapport](reports/forecasting/methods_and_results.md).

Notebookene har seksjonsoverskrifter, korte forklaringer før kode og oppsummeringer. Lagrede utdata kan leses uten å installere eller kjøre prosjektet. De er bevart fra tidligere kjøringer; de dokumenterer ikke en ny sammenhengende kjøring etter restruktureringen.

## Struktur

```text
data/                         Lokale CSV-filer; ikke versjonert
  raw/                        Uendret originalfil
  interim/                    Tidssonebehandling og kalenderkolonner
  processed/                  Renset datasett og endelig kommuneutvalg
  samples/                    Små inspeksjonsutvalg
notebooks/                    Nummerert hovedløp 01–04
  archive/                    To tidligere modellversjoner
scripts/
  data/                       Profilering → preprosessering → rensing → utvalg
  analysis/                   Innledende nasjonale visualiseringer
  documentation/              Eksport av notebooker og lagrede figurer
  archive/                    Historisk engangsskript
tests/                        Liten integrasjonstest av dataflyten
reports/
  raw_data/                   Kvalitetsrapport og CSV-sammendrag av originalen
  data_analysis/              EDA, notebookeksport og figurer
  forecasting/                Metode, modellresultater og resultatfigurer
docs/                         Arbeidsflyt, reproduksjon og endringskart
  archive/                    Historiske arbeids- og forelesningsnotater
```

Detaljert filoversikt og gamle → nye navn finnes i [strukturkartet](docs/structure.md).

## Fra rådata til resultater

| Steg | Kjørbar del | Utbytte |
| --- | --- | --- |
| 1. Datagrunnlag og rensing | `scripts/data/`, notebook 01–02 | Originalprofil, kalenderkolonner og dokumentert rensing |
| 2. EDA | Notebook 03 | Fordelinger, tidsmønstre og geografiske forskjeller |
| 3. Feature engineering | Notebook 04, seksjon 1–2 | Kalenderinput, historikk og kronologiske datasplitter |
| 4. Modellutvikling | Notebook 04, seksjon 3–5 | Baselines, modellforsøk, tuning og modellvalg |
| 5. Evaluering | Notebook 04, seksjon 6–7 | Uavhengig test, residualer, lokale feil og resultatfigurer |
| 6. Dokumentasjon | `docs/` og `reports/` | Metode, resultater og reproduksjonsgrunnlag |

Feature engineering, trening og evaluering beholdes samlet i notebook 04 fordi stegene deler data og modellobjekter i minnet. Tydelige seksjoner viser grensene mellom dem.

## Kjør prosjektet

Bruk Python 3.11 eller nyere. Åpne PowerShell i repositoryets rotmappe:

```powershell
# Bare ved førstegangsoppsett, med en tilgjengelig Python-installasjon:
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Plasser originalfilen som data/raw/consumption.csv, deretter:
.\.venv\Scripts\python.exe scripts/data/profile_raw_data.py
.\.venv\Scripts\python.exe scripts/data/preprocess_consumption.py
.\.venv\Scripts\python.exe scripts/data/clean_consumption.py
.\.venv\Scripts\python.exe scripts/data/select_municipalities.py

.\.venv\Scripts\python.exe -m jupyterlab
```

Velg kernel fra `.venv` og kjør notebookene fra topp til bunn i nummerrekkefølge. Notebook 02 leser mellomfilen **før rensing**; notebook 03 leser den rensede filen. Skriptene lager datafilene, mens notebookene undersøker og dokumenterer dem.

De store CSV-filene følger ikke med Git. Det finnes ingen automatisk nedlasting; originalfilen må skaffes separat. Datakilde, filformat, lokal datastatus, ressursbehov og framgangsmåte når utdata allerede finnes er beskrevet i [reproduksjonsveiledningen](docs/reproduction.md).

Oppdater dokumentasjonen etter notebookendringer:

```powershell
.\.venv\Scripts\python.exe scripts/documentation/export_notebooks.py
```

Denne kommandoen eksporterer kode, Markdown, lagrede utdata, PNG-er og kildehash uten å trene modellene på nytt.

## Resultater og metodiske forutsetninger

Den valgte Gradient Boosting B-modellen har lagret test-MAE **9 965,047 kWh**, RMSE **22 689,697 kWh** og R² **0,9854** for januar–april 2026. MAE er omtrent **21,04 % lavere** enn `LAG_7D`-baseline. Modellen forbedrer ikke alle perioder og kommune–gruppe-kombinasjoner; se [resultatoversikten](reports/forecasting/README.md).

- Modellvalg og hyperparametere vurderes med **MAE på 2025**. Trening bruker 2022–2024; sluttmodellen trenes på 2022–2025 før test.
- Prognoser for dag D utstedes kl. 00:00 Europe/Oslo på D−1. Historikken er `LAG_3D`, `LAG_7D` og døgnmiddelet `MEAN_3D`.
- Historikk kobles etter lokale kalenderdager. Faktiske publiseringstider er uverifisert; kontrollen forutsetter én times publiseringsforsinkelse.
- Gjeldende Gradient Boosting-oppsett bruker `early_stopping=False`. Arkiverte notebooker viser eldre metodevalg og resultater.
