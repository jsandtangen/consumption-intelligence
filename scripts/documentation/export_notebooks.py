r"""Eksporter kode, tekst, lagrede resultater og PNG-er fra notebookene 01–04.

Kjør fra prosjektet: .\.venv\Scripts\python.exe scripts/documentation/export_notebooks.py
Notatbøkene leses som JSON og kjøres ikke. Kun standardbiblioteket brukes.
"""

import base64
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / "reports/data_analysis"
NAMES = ["01_data_preparation", "02_data_quality", "03_exploratory_analysis"]


def text(value):
    return "".join(value) if isinstance(value, list) else value


def block(value, language="text"):
    value = text(value)
    longest = max((len(match) for match in re.findall(r"`+", value)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}{language}\n{value}\n{fence}\n"


def main():
    figures = DESTINATION / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    notebooks = []
    for name in NAMES:
        source = ROOT / "notebooks" / f"{name}.ipynb"
        raw = source.read_bytes()
        notebooks.append((name, source, hashlib.sha256(raw).hexdigest(), json.loads(raw)))

    lines = [
        "# Samlet dokumentasjon av notatbøkene 01–03", "",
        f"Eksportert: {datetime.now().astimezone().isoformat(timespec='seconds')}", "",
        "Dokumentet inneholder **all cellekode, all Markdown-tekst og alle lagrede resultater** fra de tre notatbøkene, i opprinnelig rekkefølge. Figurer er eksportert uten endring fra de lagrede PNG-dataene. HTML-tabeller og tekstvisninger er begge tatt med der begge finnes.", "",
        "**Avgrensning:** Ingen celler er kjørt på nytt. Resultatene er et øyeblikksbilde av det som ligger lagret i notatbøkene. Utskrifter med `...` er allerede forkortet i kilden; verdier som aldri ble skrevet ut eller lagret, kan ikke hentes ut her. Celler uten lagrede resultater er merket. Kjøringstellere dokumenterer ikke en sammenhengende kjøring fra start til slutt, og enkelte celler kan ha resultater selv om kjøringstelleren er tom.", "",
        "Cellenumrene nedenfor er **énbaserte posisjoner i notatboken**, inkludert tekstceller. Kjøringsteller er oppgitt separat. Resultatenes språk og tallformatering er beholdt fra kilden.", "",
        "## Innhold", "",
        "1. [01 – Datagrunnlag og preprosessering](#notatbok-01)",
        "2. [02 – Datakvalitet og rensebeslutninger](#notatbok-02)",
        "3. [03 – Utforskende dataanalyse](#notatbok-03)", "",
        "## Leserveiledning til prosjektforløpet", "",
        "- **01_data_preparation:** Leser originalfilen og kontrollerer tid, kalender og døgnprofil. Kurvetilpasningene evalueres på de samme 24 timegjennomsnittene som de trenes på. MSE her måler tilpasning, ikke uavhengig prognosefeil.",
        "- **02_data_quality:** Leser data/interim/consumption_preprocessed.csv før rensing. Undersøker mangler, duplikater, negative verdier, Orkland-avvik, sommertid og kommuneendringer. Notebooken filtrerer bare i minnet. scripts/data/clean_consumption.py skriver et separat renset datasett. Negative verdier beholdes.",
        "- **03_exploratory_analysis:** Leser data/processed/consumption_cleaned.csv. Åtte Orkland/Industri-observasjoner er utelatt i de lagrede resultatene. Logaritmiske histogrammer bruker bare positivt volum. Måned-, time- og ukedagskurver viser gjennomsnitt per observasjon, ikke nasjonale totaler.",
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
                            lines += [f"![{name}, celle {index}, resultat {position}](figures/{filename})", ""]
                            image_count += 1
                        elif mime == "text/html":
                            lines += ["**Lagret HTML-visning:**", "", text(value), ""]
                        elif mime == "text/plain":
                            lines += ["**Lagret tekstvisning:**", "", block(value)]
                        else:
                            raise ValueError(f"MIME-type krever egen eksport: {mime}")
            lines += ["---", ""]
    destination = DESTINATION / "notebooks_01_03.md"
    destination.write_text("\n".join(lines), encoding="utf-8")
    print(f"Lagret {destination}")
    print(f"Eksportert {sum(len(n['cells']) for _, _, _, n in notebooks)} celler og {image_count} PNG-figurer.")



def export_forecasting():
    destination = ROOT / "reports/forecasting"
    source = ROOT / "notebooks/04_forecasting.ipynb"
    notebook = json.loads(source.read_bytes())
    report = destination / "methods_and_results.md"
    narrative = report.read_text(encoding="utf-8").split("<!-- CELL_APPENDIX -->")[0]
    lines = [narrative, "<!-- CELL_APPENDIX -->", '<a id="cellevedlegg"></a>',
             "## Vedlegg: Full cellevis gjengivelse", "",
             "Eksporten bevarer kode, Markdown og alle lagrede utdata. Ingen celler er kjørt på nytt.", "",
             f"Kildens SHA-256: `{hashlib.sha256(source.read_bytes()).hexdigest()}`.", "",
             f"Notebookformat: {notebook['nbformat']}.{notebook['nbformat_minor']}. Antall celler: {len(notebook['cells'])}.", ""]
    for index, cell in enumerate(notebook["cells"], 1):
        lines += [f'<a id="celle-{index}"></a>', f"### Celle {index} — {cell['cell_type']}", "",
                  f"Celle-ID: `{cell.get('id', 'ikke angitt')}`.", "",
                  block(cell.get("source", ""), "python" if cell["cell_type"] == "code" else "markdown")]
        if cell.get("attachments"):
            raise ValueError("Cellevedlegg krever egen eksport")
        if cell["cell_type"] == "code":
            lines += [f"Lagret kjøringsnummer: `{cell.get('execution_count')}`.", ""]
            if not cell.get("outputs"):
                lines += ["Ingen lagrede utdata.", ""]
        for position, output in enumerate(cell.get("outputs", []), 1):
            if output["output_type"] == "stream":
                lines += [block(output["text"])]
            elif output["output_type"] == "error":
                lines += [block("\n".join(output.get("traceback", [])))]
            else:
                for mime, value in output.get("data", {}).items():
                    if mime == "image/png":
                        filename = f"celle_{index}_utdata_{position:02d}.png"
                        (destination / "figures" / filename).write_bytes(base64.b64decode(text(value), validate=True))
                        lines += [f"![Celle {index}, resultat {position}](figures/{filename})", ""]
                    elif mime == "text/html":
                        lines += [text(value), ""]
                    elif mime == "text/plain":
                        lines += [block(value)]
                    else:
                        raise ValueError(f"MIME-type krever egen eksport: {mime}")
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Lagret {report}")


if __name__ == "__main__":
    main()
    export_forecasting()
