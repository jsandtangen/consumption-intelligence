# Analyse av originalfilen consumption.csv

Generert: 2026-11-08T17:35:15+01:00
Python: 3.12.11. Skript: scripts/data/profile_raw_data.py (standardbiblioteket).

> Filen er flyttet ved restrukturering 9. november 2026. Tall, filstørrelse og SHA-256 gjelder den opprinnelige analysen; rådata er ikke endret.

## Fil og metode

- Kilde: `data/raw/consumption.csv`
- Filstørrelse: 3,541,628,439 byte (3.542 GB).
- SHA-256: `813f35e83ed484a14eb33d3def0bb178e782c77385313924bcbc23e5c504bf70`
- Lest som UTF-8 (eventuell BOM fjernes), semikolon mellom felt og desimalkomma.
- Hele filen er lest radvis. Originalen er ikke endret. Ingen rader er fjernet eller imputert.
- Tomme felt og felt med bare mellomrom regnes som manglende. Teksten NA/NULL regnes ikke automatisk som tom.
- Tall må være endelige. Tidsstempler må kunne tolkes og ha eksplisitt tidssoneoffset.
- Statistikk bruker gyldige verdier per kolonne; ugyldige verdier telles separat.
- Rader med feil antall felt inngår bare i totalt radantall og avvikstelling.

## Omfang og tid

- Datarader: 39,951,726. Kolonner: 7. Rader med feil antall felt: 0.
- Kommunenumre (inkludert eventuell tom verdi): 358.
- Forbruksgrupper: 'Forretning', 'Industri', 'Privat'.
- Første STARTTID (UTC): 2022-01-31 23:00:00+00:00. Siste STARTTID (UTC): 2026-04-30 21:00:00+00:00.
- Unike hele UTC-starttimer på tvers av serier: 37,199.
- Overganger der STARTTID går bakover i filrekkefølgen: 0.
- Rader med to gyldige tider og varighet ulik én time: 0.
- Observerte UTC-offsetter i STARTTID (offset: rader): {'+01:00': 17091636, '+02:00': 22860090}.
- Års- og månedsoversikter bruker lokal dato slik den står i filen. Tidsintervaller sammenlignes i UTC, også ved sommertid.

### Intervallvarigheter

| Sekunder | Rader |
| --- | ---: |
| 3600 | 39951726 |

## Kolonner og datakvalitet

| Kolonne | Tolking i analysen | Manglende | Ugyldige, ikke tomme |
| --- | --- | ---: | ---: |
| STARTTID | Tid med UTC-offset | 0 | 0 |
| SLUTTID | Tid med UTC-offset | 0 | 0 |
| KOMMUNE | Tekst / identifikator | 0 | 0 |
| KOMMUNENUMMER | Tekst / identifikator | 0 | 0 |
| FORBRUKSGRUPPE | Tekst / identifikator | 0 | 0 |
| VOLUM_KWH | Desimaltall | 0 | 0 |
| ANTALL_MÅLEPUNKT | Desimaltall | 0 | 0 |

Ikke-heltall i ANTALL_MÅLEPUNKT: 0.

## Numerisk statistikk

| Kolonne | Gyldige | Snitt | Standardavvik (utvalg) | Min | Maks | Sum | Null | Negative |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| VOLUM_KWH | 39951726 | 13910.77779 | 46582.51962 | -2137.582 | 12560619.02 | 5.557595826e+11 | 17 | 3347 |
| ANTALL_MÅLEPUNKT | 39951726 | 3132.711388 | 13418.90865 | 5 | 357321 | 1.25157227e+11 | 0 | 0 |

## Tidsserier og gjentatte nøkler

Nøkkelen er (STARTTID omregnet til UTC, KOMMUNENUMMER, FORBRUKSGRUPPE).
- Serier med gyldige hele starttimer: 1,074.
- Gjentatte nøkler utover første forekomst: 0.
- Rader utelatt fra nøkkelkontroll pga. ugyldig/manglende tid, kommunenummer eller gruppe: 0.
- Rader ellers med starttid utenfor hel UTC-time, utelatt fra nøkkelkontroll: 0.
- Manglende timer summert innenfor hver series egne endepunkter: 0.
Dette er hull i observerte serier, ikke bevis på feil. Start/slutt for ulike serier kan variere.
Kontrollen gjelder tidsserienøkler, ikke identiske hele rader. Gjentatte nøkler kan ha forskjellige måleverdier.
Summer og snitt inkluderer også rader med gjentatt nøkkel; dette er rådataoversikten.

## Kommunenavn

Kommunenumre med flere observerte navn: Ingen.
Navneendringer og kommunegrenser må avklares mot kilden før sammenslåing av serier.

## Filer med detaljer

- oversikt_aar.csv og oversikt_maaned.csv: radantall, forbrukssum og snitt.
- oversikt_kommune.csv og oversikt_forbruksgruppe.csv: omfang og forbruk.
- tidsdekning_per_serie.csv: endepunkter, unike timer, hull og gjentatte nøkler.
- stoerste_forbruksverdier.csv: de 20 største gyldige forbruksverdiene med opprinnelige identifikatorer.
- eksempler_kvalitetsavvik.csv: inntil 20 eksempler på feil feltantall / gjentatte nøkler.
CSV-rapportene bruker UTF-8 med BOM, semikolon og desimalpunkt i beregnede tall.

## Bruk i prosjektrapporten

Bruk denne analysen som dokumentasjon av rådata før behandling. Oppgi filhash, radantall, periode, grupper, kommuner og kvalitetsfunn.
Sammenlign deretter med behandlede data, og begrunn utvalg, fjerning av observasjoner og funksjonsbygging med prosjektets faktiske kode og resultater.
VOLUM_KWH tolkes som kWh ut fra kolonnenavnet. Betydningen av forbruksgrupper, målepunkter, eventuelle skjermingsregler og null/negative verdier må bekreftes hos datakilden.
Summen av ANTALL_MÅLEPUNKT på tvers av timer er ikke antall unike målepunkter. Snitt per rad er heller ikke et vektet snitt for en kommune.
Store verdier er observasjoner som bør undersøkes, ikke automatisk feil. Rapporten bruker ingen automatisk grense for å fjerne uteliggere.
Median og percentiler beregnes ikke. Snitt og standardavvik er beregnet over hele filen med flyttall, uten utvalg.
Datakilde, nedlastingsdato, lisens, publiseringstidspunkt, årsaker til avvik og hvilke prosjektsteg som faktisk ble kjørt, kan ikke fastslås fra CSV-filen alene.
Tidsdekning dokumenterer ikke når målingene var tilgjengelige for prognoser. Behold prosjektets eksplisitte tilgjengelighetsantakelse og kontroll av publiseringsforsinkelse.
