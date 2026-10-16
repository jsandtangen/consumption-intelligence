import pandas as pd

path = r"C:\Users\jsand\OneDrive - OsloMet\NETTSKY\SKOLE\26-27\SEMESTER 1\ACIT4510\energy\data\consumption_processed.csv"

# Les inn CSV med riktige skilletegn
df = pd.read_csv(path, sep=";", decimal=",")

# Finn feilverdiene
feil = (
    (df["KOMMUNE"] == "Orkland") &
    (df["FORBRUKSGRUPPE"] == "Industri") &
    (df["VOLUM_KWH"] > 10_000_000)
)

print(f"Fjerner {feil.sum()} rader")

# Fjern feilverdiene
df.drop(df[feil].index, inplace=True)

# Overskriv den eksisterende CSV-filen
df.to_csv(path, index=False, sep=";", decimal=",")