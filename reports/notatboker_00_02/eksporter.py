r"""Eksporter all cellekode, tekst og lagrede resultater fra notatbøkene 00–02.

Kjør fra prosjektet: .\.venv\Scripts\python.exe reports/notatboker_00_02/eksporter.py
Notatbøkene leses som JSON og kjøres ikke. Kun standardbiblioteket brukes.
"""

import base64
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


DESTINATION = Path(__file__).resolve().parent
ROOT = DESTINATION.parent.parent
NAMES = ["00_pre_processed_data", "01_data_overview", "02_analysis"]


def text(value):
    return "".join(value) if isinstance(value, list) else value


def block(value, language="text"):
    value = text(value)
    longest = max((len(match) for match in re.findall(r"`+", value)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}{language}\n{value}\n{fence}\n"


def main():
    figures = DESTINATION / "figurer"
    figures.mkdir(parents=True, exist_ok=True)
    notebooks = []
    for name in NAMES:
        source = ROOT / "notebooks" / f"{name}.ipynb"
        raw = source.read_bytes()
        notebooks.append((name, source, hashlib.sha256(raw).hexdigest(), json.loads(raw)))

    lines = [
        "# Samlet dokumentasjon av notatbøkene 00–02", "",
        f"Eksportert: {datetime.now().astimezone().isoformat(timespec='seconds')}", "",
        "Dokumentet inneholder **all cellekode, all Markdown-tekst og alle lagrede resultater** fra de tre notatbøkene, i opprinnelig rekkefølge. Figurer er eksportert uten endring fra de lagrede PNG-dataene. HTML-tabeller og tekstvisninger er begge tatt med der begge finnes.", "",
        "**Avgrensning:** Ingen celler er kjørt på nytt. Resultatene er et øyeblikksbilde av det som ligger lagret i notatbøkene. Utskrifter med `...` er allerede forkortet i kilden; verdier som aldri ble skrevet ut eller lagret, kan ikke hentes ut her. Celler uten lagrede resultater er merket. Kjøringstellere dokumenterer ikke en sammenhengende kjøring fra start til slutt, og enkelte celler kan ha resultater selv om kjøringstelleren er tom.", "",
        "Cellenumrene nedenfor er **énbaserte posisjoner i notatboken**, inkludert tekstceller. Kjøringsteller er oppgitt separat. Resultatenes språk og tallformatering er beholdt fra kilden.", "",
        "## Innhold", "",
        "1. [00 – Originaldata, tidsbehandling og innledende modeller](#notatbok-00)",
        "2. [01 – Datakvalitet og behandling av avvik](#notatbok-01)",
        "3. [02 – Forbruksmønstre og geografisk analyse](#notatbok-02)", "",
        "## Leserveiledning til prosjektforløpet", "",
        "- **00_pre_processed_data:** Leser originalfilen, undersøker omfang og statistikk, konverterer tid til Europe/Oslo og lager kalenderkolonner. Deretter brukes Oslo/Privat som et mindre utvalg, med forbruk per målepunkt og tilpasning av lineær regresjon og polynomer til gjennomsnittlig døgnprofil. MSE-verdiene i celle 24 måler tilpasning til de samme 24 timegjennomsnittene som modellene trenes på; de er ikke mål på prognosefeil på et separat testsett.",
        "- **01_data_overview:** Leser consumption_processed.csv, undersøker manglende verdier, duplikater, negative verdier og ekstreme observasjoner. Celle 12 finner åtte Orkland/Industri-verdier over 10 millioner kWh, og celle 14 filtrerer dem fra variabelen df. Dette filtreringstrinnet skriver ikke i seg selv tilbake til CSV-filen. Teksten oppgir at negative forbruksverdier beholdes. Videre undersøkes sommertid og kommunenummer.",
        "- **02_analysis:** Leser consumption_processed.csv og undersøker fordelinger, sesong, timer, ukedager og geografiske forskjeller. Logaritmiske histogrammer bruker bare positivt volum. Gruppestatistikken har åtte færre industriobservasjoner enn rådataene i notatbok 00. De lagrede resultatene er derfor konsistente med at de åtte ekstreme verdiene var fjernet før denne analysen; selve filendringen dokumenteres ikke av lesecellen. Måneds-, time- og ukedagskurvene viser gjennomsnitt per observasjon, ikke samlet nasjonalt forbruk.",
        "- Kommuneutvalg og andre beslutninger gjengis slik de står i hver notatbok. Kontroller den faktiske utvalgskoden senere i prosjektet før du beskriver ett endelig kommuneutvalg.", "",
        "## Kildeoversikt", "",
        "| Notatbok | Celler | Kodeceller | Tekstceller | Lagrede resultatelementer | PNG-figurer |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, source, digest, notebook in notebooks:
        cells = notebook["cells"]
        outputs = [output for cell in cells for output in cell.get("outputs", [])]
        lines.append(f"| {name}.ipynb | {len(cells)} | {sum(c['cell_type'] == 'code' for c in cells)} | {sum(c['cell_type'] == 'markdown' for c in cells)} | {len(outputs)} | {sum('image/png' in o.get('data', {}) for o in outputs)} |")

    image_count = 0
    for name, source, digest, notebook in notebooks:
        lines += ["", f'<a id="notatbok-{name[:2]}"></a>', "", f"## {name}.ipynb", "",
                  f"Kilde: [åpne notatboken](../../notebooks/{source.name}).", "",
                  f"SHA-256 av kildefilen: `{digest}`.", ""]
        for index, cell in enumerate(notebook["cells"], 1):
            kind = cell["cell_type"]
            lines += [f"### Celle {index} – {kind}", ""]
            if kind == "code":
                execution = cell.get("execution_count")
                lines += [f"Kjøringsteller: `{execution if execution is not None else 'ikke angitt'}`.", "",
                          "**Kode:**", "", block(cell.get("source", ""), "python")]
            elif kind == "markdown":
                lines += [text(cell.get("source", "")), ""]
            else:
                lines += [block(cell.get("source", ""))]
            if cell.get("attachments"):
                raise ValueError("Cellevedlegg krever egen eksport; avbryter for å unngå utelatt innhold.")
            outputs = cell.get("outputs", [])
            if kind == "code" and not outputs:
                lines += ["*Ingen lagrede resultater i denne cellen.*", ""]
            for position, output in enumerate(outputs, 1):
                output_type = output["output_type"]
                lines += [f"**Lagret resultat {position} – {output_type}:**", ""]
                if output_type == "stream":
                    lines += [f"Strøm: `{output.get('name', 'ukjent')}`.", "", block(output["text"])]
                elif output_type == "error":
                    lines += [block(f"{output.get('ename', '')}: {output.get('evalue', '')}\n" + "\n".join(output.get("traceback", [])))]
                else:
                    for mime, value in output.get("data", {}).items():
                        if mime == "image/png":
                            filename = f"{name}_celle_{index:02d}_resultat_{position:02d}.png"
                            (figures / filename).write_bytes(base64.b64decode(text(value), validate=True))
                            lines += [f"![{name}, celle {index}, resultat {position}](figurer/{filename})", ""]
                            image_count += 1
                        elif mime == "text/html":
                            lines += ["**Lagret HTML-visning:**", "", text(value), ""]
                        elif mime == "text/plain":
                            lines += ["**Lagret tekstvisning:**", "", block(value)]
                        else:
                            raise ValueError(f"MIME-type krever egen eksport: {mime}")
            lines += ["---", ""]
    destination = DESTINATION / "notatboker_00_02_dokumentasjon.md"
    destination.write_text("\n".join(lines), encoding="utf-8")
    print(f"Lagret {destination}")
    print(f"Eksportert {sum(len(n['cells']) for _, _, _, n in notebooks)} celler og {image_count} PNG-figurer.")


if __name__ == "__main__":
    main()
