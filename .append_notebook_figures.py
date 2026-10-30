import ast
import base64
import contextlib
import io
import json
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

path = Path("notebooks/03_Feature_engineering.ipynb").resolve()
original = json.loads(path.read_text(encoding="utf-8"))
nb = json.loads(json.dumps(original))

sections = [
    (
        "Actual vs. Predicted – Gradient Boosting B",
        "Sluttmodellen, trent på 2022–2025, evalueres på testdata. "
        "Grafen viser Oslo Privat 12.–18. januar 2026 (lokal tid), en fast valgt uke. "
        "Endre kommune, forbruksgruppe og datogrenser i cellen for andre utsnitt.",
        '''import matplotlib.pyplot as plt
import matplotlib.dates as mdates

gb_time_series = test_eval.loc[
    (test_eval["KOMMUNE"] == "Oslo")
    & (test_eval["FORBRUKSGRUPPE"] == "Privat")
    & (test_eval["DATE_KEY"] >= "2026-01-12")
    & (test_eval["DATE_KEY"] < "2026-01-19")
].sort_values("TIMESTAMP")

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(gb_time_series["TIMESTAMP"], gb_time_series["VOLUM_KWH"],
        label="Actual consumption", linewidth=2)
ax.plot(gb_time_series["TIMESTAMP"], gb_time_series["PREDICTED"],
        label="Gradient Boosting B prediction", linewidth=2, linestyle="--")
ax.set(title="Actual vs. Predicted – Gradient Boosting B\\nOslo, Privat | 12–18 January 2026 (test)",
       xlabel="Date (Europe/Oslo)", ylabel="Electricity consumption (kWh)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b", tz=gb_time_series["TIMESTAMP"].dt.tz))
ax.legend()
ax.grid(alpha=0.3)
fig.autofmt_xdate()
fig.tight_layout()
plt.show()
''',
    ),
    (
        "NMAE per kommune og forbruksgruppe (Heatmap)",
        "Testperiode: januar–april 2026. NMAE = 100 × MAE / gjennomsnittlig absolutt faktisk forbruk "
        "innen hver kommune–gruppe-kombinasjon. Lavere verdi er bedre; dette er ikke MAPE.",
        '''nmae_heatmap = (
    detailed_results.pivot(index="Kommune", columns="Forbruksgruppe", values="NMAE_%")
    .sort_index()
    .reindex(columns=["Forretning", "Industri", "Privat"])
)

fig, ax = plt.subplots(figsize=(8, 8))
heatmap = ax.imshow(nmae_heatmap.to_numpy(), cmap="YlOrRd", vmin=0, aspect="auto")
ax.set_xticks(range(len(nmae_heatmap.columns)), labels=nmae_heatmap.columns)
ax.set_yticks(range(len(nmae_heatmap.index)), labels=nmae_heatmap.index)
ax.set(title="NMAE – Gradient Boosting B\\nJanuary–April 2026 (test)",
       xlabel="Consumption group", ylabel="Municipality")
for row in range(len(nmae_heatmap.index)):
    for col in range(len(nmae_heatmap.columns)):
        value = nmae_heatmap.iloc[row, col]
        ax.text(col, row, f"{value:.2f}%", ha="center", va="center",
                color="white" if heatmap.norm(value) > 0.6 else "black")
fig.colorbar(heatmap, ax=ax, label="NMAE (%) – lower is better")
fig.tight_layout()
plt.show()
''',
    ),
    (
        "Monthly MAE – Gradient Boosting vs. Baseline",
        "Testresultatene holdes atskilt fra validering. Stolpene viser sluttmodellen mot "
        "sesongnaiv baseline (`LAG_7D`) for hver av de fire testmånedene.",
        '''test_monthly_mae = (
    monthly_results.loc[monthly_results["Periode"] == "Uavhengig test"]
    .sort_values("Måned")
    .set_index("Måned")[["MAE_modell", "MAE_baseline"]]
    .rename(columns={"MAE_modell": "Gradient Boosting B", "MAE_baseline": "Baseline (LAG_7D)"})
)

ax = test_monthly_mae.plot.bar(figsize=(11, 5), color=["#2878B5", "#999999"], rot=0)
for container in ax.containers:
    ax.bar_label(container, fmt="{:,.0f}", padding=3, fontsize=9)
ax.set(title="Monthly MAE – Gradient Boosting vs. Baseline\\nJanuary–April 2026 (test)",
       xlabel="Month", ylabel="MAE (kWh)")
ax.set_ylim(0, test_monthly_mae.to_numpy().max() * 1.18)
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)
ax.legend()
ax.figure.tight_layout()
plt.show()
''',
    ),
    (
        "Model Comparison – Validation MAE",
        "Alle modellene trenes på 2022–2024 og evalueres på 2025. A bruker kalender, kommune og "
        "forbruksgruppe; B bruker også historisk forbruk. Random Forest B og Gradient Boosting B "
        "vises med de beste undersøkte innstillingene. Sluttmodellens testresultater inngår ikke her.",
        '''validation_mae_plot = pd.Series({
    "Baseline A (calendar mean)": mean_absolute_error(y_val, val_baseline_A["PREDICTION"]),
    "Baseline B (LAG_7D)": mean_absolute_error(y_val, validation["LAG_7D"]),
    "Linear Regression A": mean_absolute_error(y_val, pred_A),
    "Linear Regression B": mean_absolute_error(y_val, pred_B),
    "Random Forest A": mean_absolute_error(y_val, pred_rf_A),
    "Random Forest B (tuned)": mean_absolute_error(y_val, pred_best_rf),
    "Gradient Boosting B (tuned)": mean_absolute_error(y_val, pred_best_gb),
}, name="MAE").sort_values()

ax = validation_mae_plot.plot.barh(figsize=(12, 6), color=[
    "#2878B5" if name == "Gradient Boosting B (tuned)" else "#999999"
    for name in validation_mae_plot.index
])
ax.invert_yaxis()
for container in ax.containers:
    ax.bar_label(container, fmt="{:,.2f}", padding=5)
ax.set(title="Model Comparison – Validation MAE\\nTrain: 2022–2024 | Validation: 2025",
       xlabel="MAE (kWh) – lower is better", ylabel="")
ax.set_xlim(0, validation_mae_plot.max() * 1.18)
ax.grid(axis="x", alpha=0.3)
ax.set_axisbelow(True)
ax.figure.tight_layout()
plt.show()
''',
    ),
]

for number, (title, description, source) in enumerate(sections, 1):
    nb["cells"].append({
        "cell_type": "markdown", "id": f"summary-figure-{number}-text", "metadata": {},
        "source": f"## {title}\n\n{description}".splitlines(keepends=True),
    })
    ast.parse(source)
    nb["cells"].append({
        "cell_type": "code", "id": f"summary-figure-{number}-code", "metadata": {},
        "execution_count": None, "outputs": [], "source": source.splitlines(keepends=True),
    })

assert nb["cells"][:len(original["cells"])] == original["cells"]
path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("Appended four figure sections; existing cells unchanged.", flush=True)

# Execute only the existing data/model cells needed by the new figures.
# Capture new outputs without rewriting any of the original outputs.
os.chdir(path.parent)
namespace = {"__name__": "__main__"}
for number in [2, 4, 7, 10, 15, 17, 18, 20, 22, 25, 27, 29, 31, 33,
               41, 47, 49, 53, 77, 80, 83, 86, 94, 96]:
    print(f"Running original cell {number}", flush=True)
    source = "".join(original["cells"][number - 1]["source"])
    if number == 49:
        # Cell 43 only adds the initial RF B fit; the comparison below needs it.
        exec("".join(original["cells"][42]["source"]), namespace)
    exec(compile(source, f"original-cell-{number}", "exec"), namespace)

assert len(namespace["test"]) == 86310
assert abs(namespace["test_mae"] - 9965.047) < 0.01
assert namespace["final_model"].named_steps["regression"].early_stopping is False

preview_dir = path.parent.parent / "figures" / "feature_engineering_summary"
preview_dir.mkdir(exist_ok=True)
for number in range(1, 5):
    cell = nb["cells"][len(original["cells"]) + 2 * number - 1]
    plt.close("all")
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile("".join(cell["source"]), f"new-figure-{number}", "exec"), namespace)
    assert len(plt.get_fignums()) == 1
    fig = plt.gcf()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight")
    (preview_dir / f"figure_{number}.png").write_bytes(buffer.getvalue())
    cell["outputs"] = [{
        "output_type": "display_data", "metadata": {},
        "data": {"image/png": base64.b64encode(buffer.getvalue()).decode("ascii"),
                 "text/plain": [f"<Figure: {sections[number - 1][0]}>"]},
    }]
    if output.getvalue():
        cell["outputs"].insert(0, {"output_type": "stream", "name": "stdout",
                                  "text": output.getvalue().splitlines(keepends=True)})
    # Independent execution: do not imply these ran in the original kernel sequence.
    cell["execution_count"] = None
    plt.close(fig)

assert len(namespace["gb_time_series"]) == 168
assert namespace["nmae_heatmap"].shape == (10, 3)
assert namespace["test_monthly_mae"].shape == (4, 2)
assert len(namespace["validation_mae_plot"]) == 7
assert nb["cells"][:len(original["cells"])] == original["cells"]
path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("All four figures executed and embedded; predictions match saved test MAE.", flush=True)
