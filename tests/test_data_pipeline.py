"""Små integrasjonskontroller av dataflyten; bruker aldri prosjektets store CSV-er."""

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts/data" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DataPipelineTest(unittest.TestCase):
    def test_pipeline_preserves_raw_data_and_separates_outputs(self):
        preprocess = load_script("preprocess_consumption")
        clean = load_script("clean_consumption")
        select = load_script("select_municipalities")
        with tempfile.TemporaryDirectory(prefix="energy-test-") as directory:
            root = Path(directory)
            raw = root / "raw.csv"
            with raw.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle, delimiter=";")
                writer.writerow([
                    "STARTTID", "SLUTTID", "KOMMUNE", "KOMMUNENUMMER",
                    "FORBRUKSGRUPPE", "VOLUM_KWH", "ANTALL_MÅLEPUNKT",
                ])
                for start, end, town, code, group, volume in [
                    ("2026-03-29T00:00:00Z", "2026-03-29T01:00:00Z", "Oslo", "0301", "Privat", "-10,5"),
                    ("2026-03-29T01:00:00Z", "2026-03-29T02:00:00Z", "Tromsø", "5501", "Forretning", "30,1"),
                    ("2026-04-14T00:00:00Z", "2026-04-14T01:00:00Z", "Orkland", "5059", "Industri", "12560000,0"),
                    ("2026-04-14T01:00:00Z", "2026-04-14T02:00:00Z", "Orkland", "5059", "Industri", "100,5"),
                ]:
                    writer.writerow([start, end, town, code, group, volume, "12"])
            original = raw.read_bytes()
            preprocess.SOURCE = raw
            preprocess.DATA_DIR = root / "interim"
            preprocess.PROCESSED = preprocess.DATA_DIR / "preprocessed.csv"
            preprocess.SAMPLE = root / "samples/sample.csv"
            # Multiple chunks exercise headers and appending on a tiny fixture.
            preprocess.CHUNK_SIZE = 2
            preprocess.main()
            with preprocess.PROCESSED.open(encoding="utf-8-sig", newline="") as handle:
                prepared = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual(len(prepared), 4)
            self.assertEqual([int(r["HOUR"]) for r in prepared[:2]], [1, 3])
            self.assertEqual(prepared[0]["KOMMUNENUMMER"], "0301")
            self.assertEqual(raw.read_bytes(), original)

            clean.SOURCE = preprocess.PROCESSED
            clean.DESTINATION = root / "processed/cleaned.csv"
            before_cleaning = clean.SOURCE.read_bytes()
            clean.main()
            with clean.DESTINATION.open(encoding="utf-8-sig", newline="") as handle:
                cleaned = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual(len(cleaned), 3)
            self.assertEqual(clean.SOURCE.read_bytes(), before_cleaning)
            self.assertEqual(cleaned[0]["VOLUM_KWH"], "-10,5")
            self.assertEqual(cleaned[-1]["KOMMUNE"], "Orkland")

            select.SOURCE = clean.DESTINATION
            select.DESTINATION = root / "processed/selected.csv"
            select.main()
            with select.DESTINATION.open(encoding="utf-8-sig", newline="") as handle:
                selected = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual({r["KOMMUNE"] for r in selected}, {"Oslo", "Tromsø"})
            self.assertEqual(len(selected), 2)
            self.assertEqual(selected[0]["KOMMUNENUMMER"], "0301")

            for module, destination in [
                (preprocess, preprocess.PROCESSED),
                (clean, clean.DESTINATION),
                (select, select.DESTINATION),
            ]:
                saved = destination.read_bytes()
                with self.assertRaises(FileExistsError):
                    module.main()
                self.assertEqual(destination.read_bytes(), saved)
            self.assertEqual(raw.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
