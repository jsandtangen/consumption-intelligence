# Arbeidsflyt og datagrunnlag

## 1. Datainnsamling, preprosessering og rensing

Originalen er en lokalt levert CSV med norske timeverdier per kommune og forbruksgruppe. Repositoryet inneholder ikke et nedlastingsskript eller en verifisert kilde-URL/lisens. Dette må suppleres dersom dataene skal distribueres videre.

| Fil | Ansvar og innhold | Produsent |
| --- | --- | --- |
| `data/raw/consumption.csv` | Uendret original, 7 kolonner | Ekstern fil, plasseres manuelt |
| `data/interim/consumption_preprocessed.csv` | Alle rader med lokal tid og kalenderkolonner, før rensing | `scripts/data/preprocess_consumption.py` |
| `data/processed/consumption_cleaned.csv` | Renset fullstendig datasett | `scripts/data/clean_consumption.py` |
| `data/processed/consumption_selected.csv` | Ti kommuner, alle tre forbruksgrupper | `scripts/data/select_municipalities.py` |
| `data/samples/consumption_raw_sample.csv` | Eksisterende inspeksjonsutvalg fra rådata | Historisk utvalg; uttrekksmetoden er ikke dokumentert |
| `data/samples/consumption_preprocessed_sample.csv` | De første 5 000 preprosesserte radene | Preprosesseringsskriptet |

Små utvalg egner seg til filinspeksjon. De erstatter ikke hele datasettet ved EDA eller modellutvikling.

CSV-ene bruker semikolon, desimalkomma og UTF-8, eventuelt med BOM. Originalkolonnene er `STARTTID`, `SLUTTID`, `KOMMUNE`, `KOMMUNENUMMER`, `FORBRUKSGRUPPE`, `VOLUM_KWH` og `ANTALL_MÅLEPUNKT`.

`profile_raw_data.py` leser hele originalen radvis med standardbiblioteket og skriver [kvalitetsrapport og CSV-sammendrag](../reports/raw_data/rapport.md). Rapportens duplikatnøkkel er UTC-starttid, kommunenummer og forbruksgruppe for hele timer. Notebook 02 inneholder også kontroller av fulle rader; disse kontrollene må ikke forveksles.

Preprosesseringen konverterer via UTC til Europe/Oslo og lager år, måned, dag, time og ukedag. Rensingen fjerner bare kombinasjonen **Orkland + Industri + `VOLUM_KWH > 10_000_000`**. Tidligere analyser identifiserte åtte slike observasjoner. Negative forbruksverdier beholdes. Rådata og mellomfil overskrives ikke av rensingen.

[Notebook 01](../notebooks/01_data_preparation.ipynb) viser datasettet og illustrerer døgnprofilen i Oslo Privat. De lineære og polynomiske kurvene er tilpasninger til 24 timegjennomsnitt; de er ikke prognoser evaluert på et separat testsett. [Notebook 02](../notebooks/02_data_quality.ipynb) dokumenterer rensebeslutninger, sommertid og kommuneendringer.

## 2. Utforskende dataanalyse

[Notebook 03](../notebooks/03_exploratory_analysis.ipynb) bruker det rensede datasettet og beskriver fordelinger, sesong, døgn, uke og geografiske forskjeller.

- Logaritmiske histogrammer inkluderer bare positive volum i selve figuren.
- Tidsprofilene viser gjennomsnitt per observasjon, ikke samlet norsk strømforbruk.
- Forbruk per målepunkt gjør kommuner med ulik størrelse lettere å sammenligne.
- Dekningsanalysen vurderer tolv kandidater; modellutvalget inneholder ti.

Det endelige utvalget er Oslo, Bergen, Stavanger, Trondheim, Kristiansand, Tromsø, Bodø, Alta, Sunndal og Årdal. Utvalget er et eksplisitt kommuneutvalg, ikke ti tilfeldige prøver.

Det supplerende skriptet `scripts/analysis/visualize_consumption.py` bevarer de tidlige nasjonale figurene. Dets døgninndeling bruker UTC; notebookenes kalenderanalyser bruker Europe/Oslo.

## 3. Feature engineering og dataklargjøring

[Notebook 04](../notebooks/04_forecasting.ipynb), seksjon 1–2:

- A bruker sykliske time-, uke- og månedsverdier, helgeindikator, kommune og forbruksgruppe.
- B bruker A samt `LAG_3D`, `LAG_7D` og `MEAN_3D`.
- Historikk kobles etter lokal kalenderdato og klokktime; sommertid behandles i den eksisterende koblingslogikken.
- Rader uten komplett historikk fjernes fra begge featuresettene.
- Trening er 2022–2024, validering 2025 og test januar–april 2026 i det foreliggende datasettet.

Prognosen for dag D lages kl. 00:00 på D−1. Tilgjengelighet av målinger er en eksplisitt forutsetning; notebooken kontrollerer historiske måleintervaller med én times antatt publiseringsforsinkelse.

## 4. Modellutvikling

Notebook 04, seksjon 3–5, sammenligner kalendergjennomsnitt og sesongnaiv `LAG_7D` med lineær regresjon, Ridge, Random Forest og Gradient Boosting. Pipeline-transformasjoner tilpasses ved trening. Fem Random Forest-oppsett og fem Gradient Boosting-oppsett vurderes på 2025.

Modellvalget bruker 2025-MAE. Kontrollert Gradient Boosting A/B bruker identiske modellparametere og samme rader. Gjeldende boostingmodeller bruker `early_stopping=False`; et tilfeldig internt valideringsutvalg brukes derfor ikke til tidlig stopping.

## 5. Evaluering og resultater

Notebook 04, seksjon 6–7, trener den valgte modellen på 2022–2025 og evaluerer på 2026. Resultatene omfatter MAE, RMSE, R², residualer, kommune- og grupperesultater, NMAE og månedlige sammenligninger mot baseline.

Les [resultatoversikten](../reports/forecasting/README.md) først og [full rapport](../reports/forecasting/methods_and_results.md) for tall, formler, forutsetninger og full cellegjengivelse. Testen inngår ikke i modellvalget.

## 6. Dokumentasjon og historikk

Dokumentasjonseksporten gjengir lagrede notebookresultater uten ny kjøring. Eksportens kildehash og celleposisjoner oppdateres sammen med figurene. Kjøringstellere er bevart som historiske metadata.

Eldre modellversjoner ligger i `notebooks/archive/`, tidligere notater i `docs/archive/`, og et ferdig brukt engangsskript i `scripts/archive/`. Arkivene inneholder faglig historikk som kan avvike fra gjeldende metode og tall.
