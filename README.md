# TrumpPulse

Predict market impact of Donald Trump posts (Twitter era + Truth Social) by fine-tuning FinBERT with structured features and intraday market alignment.

## What’s here
- `trumppulse_timeline.md` — end-to-end project plan and checklist.
- `overview.ipynb` — detailed model training guide (FinBERT + features, labeling, evaluation).

## Data note
- Twitter corpus is intentionally limited to the in-office period (2017-01-20 to 2021-01-08); pre-office tweets are out of scope for this project.

## Quick start
1) Clone: `git clone git@github.com:Brinda301/trumppulse.git`
2) (Optional) Create a Python env: `python -m venv .venv && source .venv/bin/activate`
3) Open `overview.ipynb` in VS Code/ Jupyter to review the full training workflow.

## Project scope (high level)
- Collect and clean Trump tweets (2009–2021) and Truth Social posts (2022–present).
- Align posts to market data (SPY/QQQ/DIA, VIX; intraday and daily) and compute abnormal returns.
- Label market impact; engineer text, temporal, market, and behavioral features.
- Fine-tune FinBERT (with auxiliary features) and benchmark against baselines.
- Evaluate, backtest alert thresholds, and package for inference.

## Roadmap & tasks
See `trumppulse_timeline.md` for the full phased checklist (data, EDA, labeling, training, evaluation, packaging).

## Contributing
- Open a branch off `main` (or `master` if you keep it) and submit PRs.
- Keep notebooks clean (restart & run all before committing if possible).
- Document decisions and data sources in PR descriptions.
