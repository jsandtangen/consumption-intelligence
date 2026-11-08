r"""Les originaldata uten å endre dem, og lag rapportgrunnlag på norsk.

Kjør: .\.venv\Scripts\python.exe analyze_consumption.py
Kun Python-standardbiblioteket brukes; hele CSV-filen leses radvis.
"""

import argparse
import csv
import hashlib
import heapq
import math
import platform
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COLUMNS = [
    "STARTTID", "SLUTTID", "KOMMUNE", "KOMMUNENUMMER",
    "FORBRUKSGRUPPE", "VOLUM_KWH", "ANTALL_MÅLEPUNKT",
]


@lru_cache(maxsize=150_000)
def timestamp(value):
    """Behold eksplisitte UTC-offsetter; naive/ugyldige tider godtas ikke."""
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def number(value):
    try:
        result = float(value.replace(",", "."))
        return result if math.isfinite(result) else None
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/consumption.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/consumption_original")
    args = parser.parse_args()
    source = args.input.resolve()
    output = args.output_dir.resolve()
    if source == output or source.is_relative_to(output):
        raise ValueError("Rapportmappen må ligge separat fra originalfilen.")
    before = source.stat()
    digest = hashlib.sha256()
    print("Beregner SHA-256 for originalfilen ...", flush=True)
    with source.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)

    missing = Counter()
    invalid = Counter()
    offsets = Counter()
    names = defaultdict(set)
    # Hver numerisk kolonne: antall, snitt, M2, minimum, maksimum, sum, null, negative.
    stats = {col: [0, 0.0, 0.0, math.inf, -math.inf, 0.0, 0, 0] for col in COLUMNS[-2:]}
    summaries = {name: defaultdict(lambda: [0, 0, 0.0, 0, 0.0])
                 for name in ("aar", "maaned", "forbruksgruppe", "kommune")}
    series = {}
    largest = []
    examples = []
    rows = malformed = duplicate_keys = bad_duration = unaligned = 0
    invalid_keys = 0
    first = last = previous = None
    out_of_order = 0
    durations = Counter()
    global_hours = set()

    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=";", strict=True)
        header = next(reader)
        if header != COLUMNS:
            raise ValueError(f"Uventet kolonnestruktur: {header!r}. Forventet: {COLUMNS!r}")
        for row in reader:
            rows += 1
            if len(row) != len(header):
                malformed += 1
                if len(examples) < 20:
                    examples.append([rows, "Feil antall felt", repr(row)])
                continue
            start_raw, end_raw, municipality, code, group, volume_raw, meters_raw = row
            for col, value in zip(header, row):
                if not value.strip():
                    missing[col] += 1
            start, end = timestamp(start_raw), timestamp(end_raw)
            for col, raw, parsed in (("STARTTID", start_raw, start), ("SLUTTID", end_raw, end)):
                if raw.strip() and parsed is None:
                    invalid[col] += 1
            if start is not None:
                first = start if first is None else min(first, start)
                last = start if last is None else max(last, start)
                if previous is not None and start < previous:
                    out_of_order += 1
                previous = start
                offsets[start_raw[-6:]] += 1
            if start is not None and end is not None:
                duration = (end - start).total_seconds()
                durations[duration] += 1
                bad_duration += duration != 3600
            volume, meters = number(volume_raw), number(meters_raw)
            for col, raw, value in (("VOLUM_KWH", volume_raw, volume),
                                    ("ANTALL_MÅLEPUNKT", meters_raw, meters)):
                if value is None:
                    if raw.strip():
                        invalid[col] += 1
                    continue
                item = stats[col]
                item[0] += 1
                delta = value - item[1]
                item[1] += delta / item[0]
                item[2] += delta * (value - item[1])
                item[3] = min(item[3], value)
                item[4] = max(item[4], value)
                item[5] += value
                item[6] += value == 0
                item[7] += value < 0
            if meters is not None and not meters.is_integer():
                invalid["ANTALL_MÅLEPUNKT: ikke heltall"] += 1
            names[code].add(municipality)
            if volume is not None:
                entry = (volume, rows, *row[:5], meters_raw)
                if len(largest) < 20:
                    heapq.heappush(largest, entry)
                elif entry > largest[0]:
                    heapq.heapreplace(largest, entry)
            # År og måned følger filens lokale tid, ikke UTC-datoen.
            labels = {"forbruksgruppe": group, "kommune": (code, municipality)}
            if start is not None:
                labels.update(aar=start_raw[:4], maaned=start_raw[:7])
            for kind, label in labels.items():
                item = summaries[kind][label]
                item[0] += 1
                if volume is not None:
                    item[1] += 1
                    item[2] += volume
                if meters is not None:
                    item[3] += 1
                    item[4] += meters

            # Én bit per UTC-time, serie og år gir eksakt nøkkelkontroll med lite minne.
            # Nøkkel: STARTTID (UTC), KOMMUNENUMMER, FORBRUKSGRUPPE.
            if start is None or not code.strip() or not group.strip():
                invalid_keys += 1
            elif start.minute or start.second or start.microsecond:
                unaligned += 1
            else:
                hour = int(start.timestamp()) // 3600
                global_hours.add(hour)
                key = (code, group)
                if key not in series:
                    series[key] = {"bits": {}, "rows": 0, "unique": 0,
                                   "first": hour, "last": hour, "duplicates": 0}
                item = series[key]
                item["rows"] += 1
                item["first"] = min(item["first"], hour)
                item["last"] = max(item["last"], hour)
                index = (start.timetuple().tm_yday - 1) * 24 + start.hour
                bits = item["bits"].get(start.year)
                if bits is None:
                    bits = item["bits"][start.year] = bytearray(1098)
                byte, bit = divmod(index, 8)
                mask = 1 << bit
                if bits[byte] & mask:
                    duplicate_keys += 1
                    item["duplicates"] += 1
                    if len(examples) < 20:
                        examples.append([rows, "Gjentatt tidsserienøkkel", repr(row)])
                else:
                    bits[byte] |= mask
                    item["unique"] += 1
            if rows % 1_000_000 == 0:
                print(f"Lest {rows:,} rader ...", flush=True)

    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError("Originalfilen ble endret under analysen. Kjør analysen på nytt.")
    output.mkdir(parents=True, exist_ok=True)

    def save_csv(name, columns, records):
        with (output / name).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(columns)
            writer.writerows(records)

    for kind, groups in summaries.items():
        label_columns = ["KOMMUNENUMMER", "KOMMUNE"] if kind == "kommune" else [kind]
        records = []
        for label, item in sorted(groups.items()):
            labels = list(label) if isinstance(label, tuple) else [label]
            n, nv, total, nm, meter_total = item
            records.append(labels + [n, nv, total, total / nv if nv else "", nm,
                                     meter_total / nm if nm else ""])
        save_csv(f"oversikt_{kind}.csv", label_columns + [
            "rader", "gyldige_volum", "sum_kwh", "snitt_kwh_per_rad",
            "gyldige_maalepunkt", "snitt_maalepunkt_per_rad"], records)

    def iso_hour(hour):
        return datetime.fromtimestamp(hour * 3600, timezone.utc).isoformat()

    coverage = []
    for (code, group), item in sorted(series.items()):
        expected = item["last"] - item["first"] + 1
        coverage.append([code, ", ".join(sorted(names[code])), group, item["rows"],
                         item["unique"], iso_hour(item["first"]), iso_hour(item["last"]),
                         expected, expected - item["unique"], item["duplicates"]])
    save_csv("tidsdekning_per_serie.csv", [
        "KOMMUNENUMMER", "kommunenavn", "FORBRUKSGRUPPE", "rader_paa_hel_time",
        "unike_timer", "foerste_start_utc", "siste_start_utc", "forventede_timer_mellom_endepunkter",
        "manglende_timer_mellom_endepunkter", "gjentatte_noekler"], coverage)
    save_csv("stoerste_forbruksverdier.csv", ["VOLUM_KWH", "datarad_1_basert",
             *COLUMNS[:5], "ANTALL_MÅLEPUNKT"], sorted(largest, reverse=True))
    save_csv("eksempler_kvalitetsavvik.csv", ["datarad_1_basert", "avvik", "originale_felt"], examples)

    lines = [
        "# Analyse av originalfilen consumption.csv", "",
        f"Generert: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Python: {platform.python_version()}. Skript: analyze_consumption.py (standardbiblioteket).", "",
        "## Fil og metode", "",
        f"- Kilde: `{source}`",
        f"- Filstørrelse: {before.st_size:,} byte ({before.st_size / 1e9:.3f} GB).",
        f"- SHA-256: `{digest.hexdigest()}`",
        "- Lest som UTF-8 (eventuell BOM fjernes), semikolon mellom felt og desimalkomma.",
        "- Hele filen er lest radvis. Originalen er ikke endret. Ingen rader er fjernet eller imputert.",
        "- Tomme felt og felt med bare mellomrom regnes som manglende. Teksten NA/NULL regnes ikke automatisk som tom.",
        "- Tall må være endelige. Tidsstempler må kunne tolkes og ha eksplisitt tidssoneoffset.",
        "- Statistikk bruker gyldige verdier per kolonne; ugyldige verdier telles separat.",
        "- Rader med feil antall felt inngår bare i totalt radantall og avvikstelling.", "",
        "## Omfang og tid", "",
        f"- Datarader: {rows:,}. Kolonner: {len(header)}. Rader med feil antall felt: {malformed:,}.",
        f"- Kommunenumre (inkludert eventuell tom verdi): {len(names):,}.",
        f"- Forbruksgrupper: {', '.join(repr(x) for x in sorted(summaries['forbruksgruppe']))}.",
        f"- Første STARTTID (UTC): {first}. Siste STARTTID (UTC): {last}.",
        f"- Unike hele UTC-starttimer på tvers av serier: {len(global_hours):,}.",
        f"- Overganger der STARTTID går bakover i filrekkefølgen: {out_of_order:,}.",
        f"- Rader med to gyldige tider og varighet ulik én time: {bad_duration:,}.",
        f"- Observerte UTC-offsetter i STARTTID (offset: rader): {dict(sorted(offsets.items()))}.",
        "- Års- og månedsoversikter bruker lokal dato slik den står i filen. Tidsintervaller sammenlignes i UTC, også ved sommertid.", "",
        "### Intervallvarigheter", "", "| Sekunder | Rader |", "| --- | ---: |",
    ]
    lines += [f"| {seconds:g} | {count} |" for seconds, count in sorted(durations.items())]
    lines += ["", "## Kolonner og datakvalitet", "",
              "| Kolonne | Tolking i analysen | Manglende | Ugyldige, ikke tomme |",
              "| --- | --- | ---: | ---: |"]
    for col in header:
        interpretation = ("Tid med UTC-offset" if col in COLUMNS[:2] else
                          "Desimaltall" if col in COLUMNS[-2:] else "Tekst / identifikator")
        lines.append(f"| {col} | {interpretation} | {missing[col]} | {invalid[col]} |")
    lines += ["", f"Ikke-heltall i ANTALL_MÅLEPUNKT: {invalid['ANTALL_MÅLEPUNKT: ikke heltall']}.",
              "", "## Numerisk statistikk", "",
              "| Kolonne | Gyldige | Snitt | Standardavvik (utvalg) | Min | Maks | Sum | Null | Negative |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for col, (n, mean, m2, low, high, total, zero, negative) in stats.items():
        values = [n, mean if n else None, math.sqrt(max(0, m2) / (n - 1)) if n > 1 else None,
                  low if n else None, high if n else None, total, zero, negative]
        lines.append(f"| {col} | " + " | ".join("–" if x is None else f"{x:.10g}" for x in values) + " |")
    gaps = sum(row[-2] for row in coverage)
    name_changes = {code: sorted(values) for code, values in names.items() if len(values) > 1}
    lines += ["", "## Tidsserier og gjentatte nøkler", "",
        "Nøkkelen er (STARTTID omregnet til UTC, KOMMUNENUMMER, FORBRUKSGRUPPE).",
        f"- Serier med gyldige hele starttimer: {len(series):,}.",
        f"- Gjentatte nøkler utover første forekomst: {duplicate_keys:,}.",
        f"- Rader utelatt fra nøkkelkontroll pga. ugyldig/manglende tid, kommunenummer eller gruppe: {invalid_keys:,}.",
        f"- Rader ellers med starttid utenfor hel UTC-time, utelatt fra nøkkelkontroll: {unaligned:,}.",
        f"- Manglende timer summert innenfor hver series egne endepunkter: {gaps:,}.",
        "Dette er hull i observerte serier, ikke bevis på feil. Start/slutt for ulike serier kan variere.",
        "Kontrollen gjelder tidsserienøkler, ikke identiske hele rader. Gjentatte nøkler kan ha forskjellige måleverdier.",
        "Summer og snitt inkluderer også rader med gjentatt nøkkel; dette er rådataoversikten.",
        "", "## Kommunenavn", "",
        f"Kommunenumre med flere observerte navn: {name_changes or 'Ingen'}.",
        "Navneendringer og kommunegrenser må avklares mot kilden før sammenslåing av serier.",
        "", "## Filer med detaljer", "",
        "- oversikt_aar.csv og oversikt_maaned.csv: radantall, forbrukssum og snitt.",
        "- oversikt_kommune.csv og oversikt_forbruksgruppe.csv: omfang og forbruk.",
        "- tidsdekning_per_serie.csv: endepunkter, unike timer, hull og gjentatte nøkler.",
        "- stoerste_forbruksverdier.csv: de 20 største gyldige forbruksverdiene med opprinnelige identifikatorer.",
        "- eksempler_kvalitetsavvik.csv: inntil 20 eksempler på feil feltantall / gjentatte nøkler.",
        "CSV-rapportene bruker UTF-8 med BOM, semikolon og desimalpunkt i beregnede tall.",
        "", "## Bruk i prosjektrapporten", "",
        "Bruk denne analysen som dokumentasjon av rådata før behandling. Oppgi filhash, radantall, periode, grupper, kommuner og kvalitetsfunn.",
        "Sammenlign deretter med behandlede data, og begrunn utvalg, fjerning av observasjoner og funksjonsbygging med prosjektets faktiske kode og resultater.",
        "VOLUM_KWH tolkes som kWh ut fra kolonnenavnet. Betydningen av forbruksgrupper, målepunkter, eventuelle skjermingsregler og null/negative verdier må bekreftes hos datakilden.",
        "Summen av ANTALL_MÅLEPUNKT på tvers av timer er ikke antall unike målepunkter. Snitt per rad er heller ikke et vektet snitt for en kommune.",
        "Store verdier er observasjoner som bør undersøkes, ikke automatisk feil. Rapporten bruker ingen automatisk grense for å fjerne uteliggere.",
        "Median og percentiler beregnes ikke. Snitt og standardavvik er beregnet over hele filen med flyttall, uten utvalg.",
        "Datakilde, nedlastingsdato, lisens, publiseringstidspunkt, årsaker til avvik og hvilke prosjektsteg som faktisk ble kjørt, kan ikke fastslås fra CSV-filen alene.",
        "Tidsdekning dokumenterer ikke når målingene var tilgjengelige for prognoser. Behold prosjektets eksplisitte tilgjengelighetsantakelse og kontroll av publiseringsforsinkelse.",
    ]
    report = output / "rapport.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Ferdig: {rows:,} rader. Rapport: {report}", flush=True)


if __name__ == "__main__":
    main()
