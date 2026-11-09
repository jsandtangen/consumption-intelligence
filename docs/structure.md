# Struktur og ansvar

## Hovedløpet

| Del | Filer og mapper |
| --- | --- |
| Datainnsamling og datarensing | `data/raw/`, `data/interim/`, `data/processed/`, `scripts/data/`, notebook 01–02 |
| Utforskende analyse | Notebook 03, `scripts/analysis/`, `reports/data_analysis/` |
| Feature engineering og dataklargjøring | Notebook 04, seksjon 1–2 |
| Modellutvikling | Notebook 04, seksjon 3–5 |
| Evaluering og resultater | Notebook 04, seksjon 6–7, `reports/forecasting/` |
| Dokumentasjon | Rotens README, `docs/`, rapporter og dokumentasjonseksport |

Filnavn bruker beskrivende engelske navn med små bokstaver og understrek. Forklaringene er hovedsakelig på norsk. Eksisterende faglig tekst, engelske figurtekster og originale utdata er bevart.

## Notebooker

| Tidligere fil | Nåværende fil | Ansvar |
| --- | --- | --- |
| `00_pre_processed_data.ipynb` | [01_data_preparation.ipynb](../notebooks/01_data_preparation.ipynb) | Originaldata, kalender og innledende døgnprofil |
| `01_data_overview.ipynb` | [02_data_quality.ipynb](../notebooks/02_data_quality.ipynb) | Datakvalitet og begrunnelse for rensing |
| `02_analysis.ipynb` | [03_exploratory_analysis.ipynb](../notebooks/03_exploratory_analysis.ipynb) | EDA og geografisk analyse |
| `03_Feature_engineering.ipynb` | [04_forecasting.ipynb](../notebooks/04_forecasting.ipynb) | Feature engineering, modeller og evaluering |
| `03_Feature_engineering_before_D3_and_no_early_stopping.ipynb` | [archive/forecasting_before_d3.ipynb](../notebooks/archive/forecasting_before_d3.ipynb) | Historisk prognoseoppsett før D−3 |
| `03_Feature_engineering_sikkerhetskopiering copy.ipynb` | [archive/forecasting_backup.ipynb](../notebooks/archive/forecasting_backup.ipynb) | Tidligere sikkerhetskopi med faglig historikk |

De to eldre modellfilene er ikke identiske kopier av dagens notebook. Derfor beholdes begge i arkivet. Alle seks har en introduksjon og korte forklaringer før kodecellene. Arkivnotebookene er merket som historiske, og modellkoden deres er bevart.

Notebook 04 er et sammenhengende eksperiment som deler features, datasplitter og modellobjekter. Å dele det i flere filer ville kreve et nytt system for mellomlagring av modelltilstand eller gjentatt trening. Seksjoner gir her et enklere og eksplisitt skille mellom ansvarsområdene.

## Skript

| Tidligere fil | Nåværende fil |
| --- | --- |
| `analyze_consumption.py` | `scripts/data/profile_raw_data.py` |
| `preprocessing_consumption.py` | `scripts/data/preprocess_consumption.py` |
| `removeing_orkland_values.py` | `scripts/data/clean_consumption.py` |
| `10_samples.py` | `scripts/data/select_municipalities.py` |
| `src/visualize.py` | `scripts/analysis/visualize_consumption.py` |
| `reports/notatboker_00_02/eksporter.py` | `scripts/documentation/export_notebooks.py` |
| `.append_notebook_figures.py` | `scripts/archive/append_forecasting_figures.py` |

Dataflyten ligger i selvstendige skript med hver sin input og output. Rensing og kommuneutvalg leser i biter, skriver først `.partial` og erstatter ikke eksisterende mål. Dette gjør det mulig å beholde både før- og ettergrunnlaget for kvalitetsanalysen.

Det arkiverte figurskriptet er et ferdig brukt engangsskript med gamle celleposisjoner. Kjøring stoppes med en forklaring for å unngå at det legger til de samme figurcellene på nytt. Den historiske koden er bevart for innsyn. Vanlige dokumentasjonseksporter bruker `export_notebooks.py`.

## Data, figurer og rapporter

| Tidligere plassering | Nåværende plassering |
| --- | --- |
| `data/consumption.csv` | `data/raw/consumption.csv` |
| `data/consumption_processed.csv` | `data/processed/consumption_cleaned.csv` |
| `data/consumption_selected.csv` | `data/processed/consumption_selected.csv` |
| `data/consumption_sample.csv` | `data/samples/consumption_raw_sample.csv` |
| `data/consumption_processed_sample.csv` | `data/samples/consumption_preprocessed_sample.csv` |
| `reports/consumption_original/` | `reports/raw_data/` |
| `reports/notatboker_00_02/` | `reports/data_analysis/` |
| `figures/*.png` | `reports/data_analysis/figures/` |
| Modellrapport og modellfigurer under `notebooks/` | `reports/forecasting/methods_and_results.md` og `figures/` |
| `forbedringer_29.10.md` | `docs/archive/improvement_notes_2026-10-29.md` |
| `notater_til_forelsening.md` | `docs/archive/lecture_notes.md` |

De lokale CSV-filene er flyttet uten innholdsendring. Mellomfilen `data/interim/consumption_preprocessed.csv` er et nytt, eksplisitt trinn som må lages fra rådata; den gamle preprosesserte fullfilen var brukt som renset analysegrunnlag. Se [reproduksjonsveiledningen](reproduction.md) før ny kjøring.

Notebookenes kildehash, cellevedlegg og eksporterte figurhenvisninger er oppdatert sammen. Utdaterte eksportbilder kan fjernes når identisk bildeinnhold er bevart under nytt navn. Vitenskapelige resultater hentes fra lagrede utdata; historiske notater er tydelig skilt fra gjeldende metode.
