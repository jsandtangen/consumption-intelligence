# Reproduser analyser og modeller

## Miljø

Bruk Python 3.11 eller nyere og installer [requirements.txt](../requirements.txt) i et virtuelt miljø. Scikit-learn 1.8.0 er dokumentert i de lagrede modellresultatene og er låst til den versjonen. Notebookmetadata viser også en eldre Python-kernel; dette er ikke en fullstendig låst original miljøbeskrivelse. Andre biblioteker har kompatibilitetsintervaller, så eksakt bitlik reproduksjon er ikke garantert.

På Windows brukes `.\.venv\Scripts\python.exe` til alle prosjektkommandoer. Hvis `python` ikke finnes ved førstegangsoppsett, opprett `.venv` med den absolutte stien til en installert Python. Prosjektkommandoene trenger ikke aktivering av PowerShell-miljøet.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name energy --display-name "Python (energy)"
```

Kernelregistrering er valgfritt dersom Jupyter allerede finner `.venv`. Velg riktig kernel før kjøring.

## Data og plassbehov

Plasser originalfilen i `data/raw/consumption.csv`. Dataene er utelatt fra Git og må skaffes separat; se [datagrunnlaget](workflow.md). Originalen er omtrent 3,54 GB. Mellomfil og renset fil er hver omtrent 4 GB; ha god plass til begge og midlertidige utdata. Notebook 01–03 leser hele datasettet i minnet og kan kreve betydelig RAM. Modellnotebooken bruker det mindre kommuneutvalget på omtrent 117 MB, men treningen, særlig Random Forest og tuning, kan fortsatt være ressurskrevende.

Ved restruktureringen ble den eksisterende `consumption_processed.csv` flyttet til `data/processed/consumption_cleaned.csv`, og kommuneutvalget ble flyttet uendret. De lagrede EDA-resultatene tilsvarer et datasett der åtte Orkland-avvik er fjernet. Filens faktiske innhold må kontrolleres ved ny dataleveranse; navnet alene dokumenterer ikke rensehistorikken. En separat mellomfil før rensing må genereres fra rådata for å kjøre notebook 02 på nytt. De eksisterende små utvalgene er også bevart uendret.

## Kjør dataflyten

Kjør fra repositoryets rotmappe:

```powershell
.\.venv\Scripts\python.exe scripts/data/profile_raw_data.py
.\.venv\Scripts\python.exe scripts/data/preprocess_consumption.py
.\.venv\Scripts\python.exe scripts/data/clean_consumption.py
.\.venv\Scripts\python.exe scripts/data/select_municipalities.py
```

Profileringen endrer ikke originalen. De tre påfølgende skriptene nekter å overskrive eksisterende utdata eller `.partial`-filer. For en full ny gjennomkjøring: flytt eksisterende genererte mål- og utvalgsfiler til et eget lokalt arkiv først. Behold rådata. Dersom ferdige data allerede finnes og bare modeller skal kjøres, kan de relevante datastegene hoppes over. Hvis bare mellomfilen mangler, må også det eksisterende preprosesserte 5 000-radersutvalget flyttes før preprosesseringen kjøres.

Ved avbrudd blir eventuelle `.partial`-filer liggende for inspeksjon. Undersøk årsaken og flytt eller fjern bare den aktuelle mellomfilen før ny kjøring.

Profileringen støtter også eksplisitte stier, for eksempel for en liten kontrollfil:

```powershell
.\.venv\Scripts\python.exe scripts/data/profile_raw_data.py --input data/samples/consumption_raw_sample.csv --output-dir reports/sample_check
```

Dette er en utvalgskontroll og erstatter ikke rapporten for hele originalfilen.

## Kjør notebookene

```powershell
.\.venv\Scripts\python.exe -m jupyterlab
```

Åpne notebook 01–04 i nummerrekkefølge. Velg **Restart Kernel and Run All Cells** for hver notebook. De fire notebookene bruker egne innlesinger og trenger ikke variabler fra andre notebooker. Inndata må være laget på forhånd. Filstiene finner prosjektroten fra både rotmappen, `notebooks/` og arkivmappen.

| Notebook | Forutsetning | Kontroller etter kjøring |
| --- | --- | --- |
| 01 | Original CSV | Lokal tid og kalender, Oslo Privat, profiltilpasning |
| 02 | Preprosessert mellomfil før rensing | Mangler, avvik, sommertid og kommunedekning |
| 03 | Renset fullstendig CSV | Fordelinger, profiler og geografiske tabeller |
| 04 | Endelig kommuneutvalg | Samme rader for A/B, validering 2025, separat test 2026 |

Ved uendret grunnlag viser de lagrede modellresultatene 1 115 970 utvalgsrader før historikkfiltrering og 1 110 630 komplette rader: 761 580 trening, 262 740 validering og 86 310 test. Bruk tallene som kontrollpunkter for dette datasettet, ikke som generelle krav til framtidige dataleveranser.

Arkiverte notebooker inngår ikke i reproduksjonen av sluttmodellen. De kan inneholde tidligere lagdefinisjoner og automatisk early stopping.

## Oppdater rapportene

Etter at notebookene er lagret:

```powershell
.\.venv\Scripts\python.exe scripts/documentation/export_notebooks.py
```

Eksporten oppdaterer begge fulle cellevedlegg, kildehash og PNG-er. Den kjører ingen analyser. Oppdater også den faglige hovedteksten, resultatoversikten og cellehenvisningene dersom beregninger eller celleorden endres. Skriptet bevarer den redigerte hovedteksten i modellrapporten før `<!-- CELL_APPENDIX -->`.

## Verifikasjon av restruktureringen

Den lille integrasjonstesten for preprosessering, rensing og kommuneutvalg kan kjøres uten de store CSV-filene:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Testen bruker midlertidige data og kontrollerer sommertid, negative verdier, Orkland-kriteriet, kommuneutvalg og beskyttelse mot overskriving.

Se [verifikasjonsrapporten](../reports/restructuring_validation.md) for kontroller som faktisk er utført. Lagrede resultater er bevart; restruktureringen innebærer ikke at modellene er trent på nytt.
