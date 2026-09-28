import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    "consumption_per_group_municipality_hour-all-no-0000-00-00.csv",
    sep=";",
    decimal=","
)

# Konverter eksplisitt til datetime, håndterer skifte mellom sommer/vintertid
df["STARTTID"] = pd.to_datetime(df["STARTTID"], utc=True)
df["SLUTTID"] = pd.to_datetime(df["SLUTTID"], utc=True)

# 1. Undersøk negative verdier
neg = df[df["VOLUM_KWH"] < 0]
print("Antall negative rader:", len(neg))
print("Andel negative:", len(neg) / len(df) * 100, "%")
print(neg["FORBRUKSGRUPPE"].value_counts())
print(neg[["STARTTID", "KOMMUNE", "FORBRUKSGRUPPE", "VOLUM_KWH"]].head(10))

# 2. Aggreger til daglig nivå på landsbasis, per forbruksgruppe
df["dato"] = df["STARTTID"].dt.date
daily = df.groupby(["dato", "FORBRUKSGRUPPE"])["VOLUM_KWH"].sum().reset_index()
daily["dato"] = pd.to_datetime(daily["dato"])

# 3. Plot: daglig forbruk over tid, per gruppe (for hele landet)
fig, ax = plt.subplots(figsize=(10, 5))
for gruppe in daily["FORBRUKSGRUPPE"].unique():
    subset = daily[daily["FORBRUKSGRUPPE"] == gruppe]
    ax.plot(subset["dato"], subset["VOLUM_KWH"], label=gruppe)
ax.set_title("Daglig strømforbruk i Norge, etter forbruksgruppe")
ax.set_xlabel("Dato")
ax.set_ylabel("Forbruk (kWh)")
ax.legend()
plt.tight_layout()
plt.savefig("daglig_forbruk.png", dpi=150)
plt.show()

# 4. Gjennomsnittlig forbruksprofil per time på døgnet
df["time"] = df["STARTTID"].dt.hour
hourly_profile = df.groupby(["time", "FORBRUKSGRUPPE"])["VOLUM_KWH"].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(8, 5))
for gruppe in hourly_profile["FORBRUKSGRUPPE"].unique():
    subset = hourly_profile[hourly_profile["FORBRUKSGRUPPE"] == gruppe]
    ax2.plot(subset["time"], subset["VOLUM_KWH"], marker="o", label=gruppe)
ax2.set_title("Gjennomsnittlig forbruk per time på døgnet")
ax2.set_xlabel("Time på døgnet")
ax2.set_ylabel("Gjennomsnittlig forbruk (kWh)")
ax2.legend()
plt.tight_layout()
plt.savefig("time_profil.png", dpi=150)
plt.show()

# 5. Generell oversikt til dokumentet
print("\nAntall rader:", len(df))
print("Antall kommuner:", df["KOMMUNE"].nunique())
print("Tidsperiode:", df["STARTTID"].min(), "til", df["STARTTID"].max())
print("Forbruksgrupper:", df["FORBRUKSGRUPPE"].unique())