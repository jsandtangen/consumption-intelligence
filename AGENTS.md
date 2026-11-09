## Core principles

### 1. Keep the implementation as simple as possible

Simplicity is the highest priority.

Always prefer the smallest amount of code that solves the problem correctly, securely, and reliably.

- Do not over-engineer.
- Do not introduce abstractions, classes, layers, helper functions, dependencies, configuration, or architecture unless they provide a clear benefit.
- Prefer existing code and existing dependencies over creating new systems.
- Avoid premature optimization and unnecessary flexibility for hypothetical future requirements.
- If two solutions achieve roughly the same result, choose the simpler one with less code and fewer moving parts.
- Reduce duplication when it genuinely simplifies the code, but do not create abstractions only to avoid a few repeated lines.
- Code should be easy to understand, modify, test, and debug.
- Security, correctness, and reliability must not be sacrificed just to reduce line count.

The goal is not literally the fewest possible lines. The goal is the **least complexity necessary to achieve the required functionality safely and correctly**.

Before adding code, ask:
1. Is this actually necessary?
2. Can the same result be achieved with existing code?
3. Is there a simpler solution?
4. Am I solving a real requirement or a hypothetical future problem?

### 2. Keep this file up to date

Treat `AGENTS.md` as living project knowledge.

Whenever you discover important information that will affect future development, update this file.

Examples include:
- important architectural decisions
- project conventions
- recurring constraints
- important commands or workflows
- known pitfalls
- security requirements
- decisions about dependencies or technologies
- important lessons learned while implementing or debugging

Only store information that is likely to remain useful in future tasks.

Do not add:
- temporary debugging details
- one-off observations
- obvious information that can easily be inferred from the code
- long explanations when a short rule is enough

When new information conflicts with existing information in this file, update or replace the outdated information instead of simply appending another rule.

Keep `AGENTS.md` concise, current, and useful.

## Forecasting conventions

- Run `scripts/data/profile_raw_data.py` to profile `data/raw/consumption.csv` without modifying it. It uses only the Python standard library and writes `reports/raw_data/rapport.md` plus CSV summaries; its duplicate check uses `(STARTTID in UTC, KOMMUNENUMMER, FORBRUKSGRUPPE)` for whole-hour timestamps, not full-row equality.

- Run project Python commands with `.\.venv\Scripts\python.exe` on Windows; `python` and the `py` launcher may not resolve an installed interpreter.
- In `notebooks/04_forecasting.ipynb`, forecasts for day D are issued at 00:00 Europe/Oslo on D-1. Historical inputs are `LAG_3D`, `LAG_7D`, and `MEAN_3D` (the daily mean for D-3); shifts use local calendar days, not fixed 24-hour offsets.
- Measurement publication times are unverified. Keep the explicit availability assumption and the one-hour publication-delay check when changing historical features.
- Set `early_stopping=False` in every `HistGradientBoostingRegressor`, including tuning. Use chronological validation in 2025 and keep test results for January-April 2026 separate.
- `reports/forecasting/methods_and_results.md` records the notebook's saved methods and results, with a full cell appendix and figures in `reports/forecasting/figures/`. It is a dated snapshot; check the notebook before treating its results as current.
- Documentation cell references are one-based positions in the notebook, not execution counts. Refresh the source hash, full appendix and exported PNGs together; saved execution counts are not proof of a clean end-to-end run.
- `scripts/documentation/export_notebooks.py` regenerates the combined snapshot of notebooks 01–03 and the full appendix of notebook 04, including source hashes and PNGs, without executing cells. It preserves the forecasting report's narrative before `<!-- CELL_APPENDIX -->`; update that narrative and its cell references manually when methods or cell order change. Saved output truncation is preserved.
- Model selection in this notebook uses 2025 MAE. The selected Gradient Boosting model does not minimize every metric; distinguish the controlled A/B history comparison from the final model's test comparison against `LAG_7D`.

## Project structure

- Follow `docs/workflow.md` and `docs/reproduction.md`. Active notebooks are numbered 01–04; historical model versions and notes belong in explicit `archive/` directories and retain their original model logic.
- Data flow: `data/raw/consumption.csv` → `data/interim/consumption_preprocessed.csv` → `data/processed/consumption_cleaned.csv` → `data/processed/consumption_selected.csv`. Notebook 02 reads the pre-cleaning interim file; notebook 03 reads cleaned data. Data scripts refuse to overwrite existing outputs or `.partial` files.
- Scripts resolve the project root from `__file__`; notebooks locate the ancestor containing `AGENTS.md` and `data/`. Do not introduce machine-specific paths.
- Keep notebook code preceded by a short Markdown explanation of what, why and expected output; preserve saved results when only reorganizing content. Reports and figures belong under `reports/`, not alongside notebooks.
- Run `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` for the small data-pipeline integration test; it uses temporary fixtures, not the project's large CSV files.
