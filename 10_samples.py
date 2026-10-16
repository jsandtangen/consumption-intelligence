
import pandas as pd
from pathlib import Path

data_dir = Path(
    r"C:\Users\jsand\OneDrive - OsloMet\NETTSKY\SKOLE\26-27\SEMESTER 1\ACIT4510\energy\data"
)

input_path = data_dir / "consumption_processed.csv"
output_path = data_dir / "consumption_selected.csv"

municipalities = [
    "Oslo", "Bergen", "Stavanger", "Trondheim",
    "Kristiansand", "Tromsø", "Bodø", "Alta",
    "Sunndal", "Årdal"
]

total_rows = 0
first_chunk = True

for chunk in pd.read_csv(
    input_path,
    sep=";",
    decimal=",",
    chunksize=500_000
):
    filtered = chunk[
        chunk["KOMMUNE"].isin(municipalities)
    ]

    if filtered.empty:
        continue

    filtered.to_csv(
        output_path,
        sep=";",
        decimal=",",
        mode="w" if first_chunk else "a",
        header=first_chunk,
        index=False
    )

    first_chunk = False
    total_rows += len(filtered)

print(f"Saved: {output_path}")
print(f"Total observations: {total_rows:,}")

# Verify
selected = pd.read_csv(
    output_path,
    sep=";",
    decimal=","
)

print("\nObservations by municipality:")
print(selected.groupby("KOMMUNE").size())

print("\nDataset shape:")
print(selected.shape)