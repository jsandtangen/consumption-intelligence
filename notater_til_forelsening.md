### 1. Data og preprocessing

- Jobbet med ca. 1,1 millioner observasjoner fra februar 2022 til april 2026.
- Gjennomført EDA for å undersøke forbruksmønstre, sesongvariasjoner, ekstremverdier og forskjeller mellom kommuner og forbruksgrupper.
- Gjennomført feature engineering med kalenderinformasjon (time, ukedag, måned, helg) og historisk strømforbruk (2 og 7 dager tilbake).
- Håndtert manglende verdier, kategoriske variabler og tidsstempler.

### 2. Maskinlæring

- Supervised learning (regresjon) for å predikere strømforbruk i kWh.
- Trent og sammenlignet fire ML-algoritmer:
  - Linear Regression
  - Ridge Regression
  - Random Forest
  - Gradient Boosting
- Sammenlignet to feature-sett:
  - A: Kun kalenderinformasjon.
  - B: Kalenderinformasjon + historisk strømforbruk.
- Brukt enkle baseline-metoder for å vurdere om ML gir bedre prediksjoner.

### 3. Modelltrening og evaluering

- Kronologisk datasplitt:
  - Training: 2022–2024
  - Validation: 2025
  - Test: januar–april 2026
- Gjennomført hyperparameter tuning av Random Forest og Gradient Boosting.
- Evaluert modellene med MAE, RMSE og R².
- Analysert residualer og prediksjonsfeil for ulike kommuner og forbruksgrupper.

### 4. Resultater

- Gradient Boosting med historiske data presterte best.
- Oppnådde R² = 0,989 og MAE ≈ 8 678 kWh på testdataene.
- Reduserte MAE med 31,2 % sammenlignet med baseline som bruker forbruket fra samme time forrige uke.
- Fant at historisk forbruk forbedret prediksjonene, men at modellfleksibilitet også hadde stor betydning.
- Store variasjoner i prediksjonskvalitet mellom kommuner og forbruksgrupper.

### 5. Videre arbeid

- Undersøke om separate modeller for kommuner eller forbruksgrupper gir bedre resultater.
- Vurdere flere forklaringsvariabler, særlig temperatur.
- Diskutere svakheter ved modellen, generalisering og risiko for overfitting.