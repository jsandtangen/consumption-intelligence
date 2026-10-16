from pathlib import Path
import pandas as pd

# Save this script inside the energy folder, next to the data folder.
DATA_DIR = Path(__file__).resolve().parent / "data"
SOURCE = DATA_DIR / "consumption.csv"
PROCESSED = DATA_DIR / "consumption_processed.csv"
SAMPLE = DATA_DIR / "consumption_processed_sample.csv"
CHUNK_SIZE = 100_000
SAMPLE_ROWS = 5_000


def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Finner ikke originalfilen: {SOURCE}")
    for destination in (PROCESSED, SAMPLE):
        if destination.exists():
            raise FileExistsError(
                f"Filen finnes allerede, og blir ikke overskrevet: {destination}\n"
                "Gi den eksisterende filen et annet navn eller flytt den først."
            )

    processed_tmp = DATA_DIR / "consumption_processed.csv.partial"
    sample_tmp = DATA_DIR / "consumption_processed_sample.csv.partial"
    for tmp in (processed_tmp, sample_tmp):
        if tmp.exists():
            raise FileExistsError(f"En tidligere midlertidig fil finnes: {tmp}")

    total_rows = 0
    sample_remaining = SAMPLE_ROWS
    try:
        for chunk_index, chunk in enumerate(
            pd.read_csv(SOURCE, sep=";", dtype=str, chunksize=CHUNK_SIZE, encoding="utf-8-sig")
        ):
            for column in ("STARTTID", "SLUTTID"):
                if column not in chunk.columns:
                    raise KeyError(f"Mangler kolonnen {column}. Kontroller skilletegnet i CSV-filen.")
                chunk[column] = (
                    pd.to_datetime(chunk[column], utc=True, errors="raise")
                    .dt.tz_convert("Europe/Oslo")
                )

            start = chunk["STARTTID"].dt
            chunk["YEAR"] = start.year
            chunk["MONTH"] = start.month
            chunk["DAY"] = start.day
            chunk["HOUR"] = start.hour
            chunk["DAY_OF_WEEK"] = start.dayofweek

            chunk.to_csv(
                processed_tmp, sep=";", index=False,
                mode="w" if chunk_index == 0 else "a",
                header=chunk_index == 0, encoding="utf-8-sig" if chunk_index == 0 else "utf-8"
            )
            if sample_remaining > 0:
                part = chunk.head(sample_remaining)
                part.to_csv(
                    sample_tmp, sep=";", index=False,
                    mode="w" if sample_remaining == SAMPLE_ROWS else "a",
                    header=sample_remaining == SAMPLE_ROWS,
                    encoding="utf-8-sig" if sample_remaining == SAMPLE_ROWS else "utf-8"
                )
                sample_remaining -= len(part)

            total_rows += len(chunk)
            print(f"Behandlet {total_rows:,} rader", flush=True)

        if total_rows == 0:
            raise ValueError("Originalfilen inneholder ingen datarader.")
        processed_tmp.rename(PROCESSED)
        sample_tmp.rename(SAMPLE)
    except Exception:
        print("Prosessen ble avbrutt. Originalfilen er ikke endret.")
        print("Eventuelle .partial-filer kan fjernes etter at årsaken er undersøkt.")
        raise

    print(f"\nFerdig! Hele datasettet ({total_rows:,} rader): {PROCESSED}")
    print(f"Utvalg ({min(total_rows, SAMPLE_ROWS):,} rader): {SAMPLE}")


if __name__ == "__main__":
    main()
