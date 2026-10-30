1. Kontrollere prognoseoppsett og data leakage

Bekreft at alle inputvariabler faktisk er tilgjengelige når prognosen lages kl. 00 dagen før måldagen. Kontroller særlig LAG_2D, LAG_7D og PREV_DAY_MEAN. Dokumenter at tilgjengeligheten av målinger er en forutsetning dersom faktisk publiseringstid ikke kan bekreftes.

2. Undersøke early stopping i Gradient Boosting

Sjekk om scikit-learn automatisk bruker et tilfeldig internt valideringsutvalg for early stopping. Finn ut hvor mange iterasjoner modellen faktisk gjennomførte, og vurder om innstillingen bør endres eller bare dokumenteres som en metodisk begrensning.

3. Residualanalyse av sluttmodellen

Tidligere residualanalyse ble gjort på Random Forest. Gjennomfør tilsvarende analyse på den endelige Gradient Boosting-modellen. Undersøk om den systematisk over- eller underpredikerer, og om feilene blir større ved høyt strømforbruk.

4. Sammenligne Gradient Boosting med baseline på detaljnivå

Beregn MAE og relativ forbedring mot LAG_7D-baseline for hver kommune og forbruksgruppe. Identifiser hvor modellen gir størst forbedring, og om enkelte grupper faktisk har dårligere resultater enn baseline.


5. Undersøke ytelse over tid

Beregn MAE og forbedring mot baseline for hver måned. Bruk valideringsåret 2025 og testmånedene januar–april 2026, men skill tydelig mellom validering og uavhengig test. Undersøk om modellen fungerer bedre i noen sesonger enn andre.

6. Sammenligne Gradient Boosting A og B

Middels

Tren en kalenderbasert Gradient Boosting A og sammenlign med B på de samme valideringsradene og med like hyperparametere. Målet er å isolere hvor mye historiske forbruksdata forbedrer akkurat den modelltypen du valgte.