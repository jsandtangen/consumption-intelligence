# Modellresultater

Start med [notebook 04](../../notebooks/04_forecasting.ipynb) for sammenhengen mellom features, modellvalg og test. [Den fullstendige rapporten](methods_and_results.md) har metode, alle lokale resultattabeller, begrensninger og full cellegjengivelse. Figurene ligger i [figures/](figures/).

## Validering og modellvalg

Trening: 2022–2024. Validering: 2025. Modellvalg bruker MAE.

| Modell, beste undersøkte oppsett | MAE (kWh) | RMSE (kWh) |
| --- | ---: | ---: |
| Random Forest B | 7 190,257 | 16 488,823 |
| Gradient Boosting B | 7 146,641 | 16 153,297 |

En separat kontrollert A/B-sammenligning av Gradient Boosting bruker identiske modellinnstillinger og samme rader. MAE går fra 9 122,75 for kalenderbasert A til 7 146,64 for B med historikk: **21,66 % reduksjon**. Dette måler historikkens bidrag på validering.

## Uavhengig test

Sluttmodellen trenes på 2022–2025. Test: januar–april 2026.

| Modell | MAE (kWh) | RMSE (kWh) | R² |
| --- | ---: | ---: | ---: |
| Ukesbaseline, `LAG_7D` | 12 620,646 | 28 642,545 | 0,977* |
| Gradient Boosting B | 9 965,047 | 22 689,697 | 0,9854 |

*Baseline-R² er vist med presisjonen i den lagrede sammenligningstabellen. Sluttmodellens R² er hentet fra den separate testutskriften.*

Test-MAE er omtrent **21,04 % lavere enn ukesbaseline**, beregnet fra de lagrede MAE-tallene. Dette er en annen sammenligning enn kontrollert A/B.

- Modellen forbedrer ikke alle feilmål, måneder eller lokale kombinasjoner.
- I februar 2026 er månedlig MAE **3,88 % høyere** enn baseline.
- Feil varierer mellom kommuner og forbruksgrupper; se detaljtabellene og NMAE-varmekartet i full rapport.
- Testen dekker fire måneder, ikke et helt år. Faktiske publiseringstider for målingene er uverifisert.

Tallene er hentet fra tidligere lagrede notebookutdata. Dokumentasjonseksporten og restruktureringen trener ingen modeller på nytt.
