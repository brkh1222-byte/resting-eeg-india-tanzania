# resting-eeg-india-tanzania

Is alpha really missing? This repo models the periodic and aperiodic components of resting EEG across age and income in 2,000 adults from India and Tanzania, all recorded on identical hardware (OpenNeuro ds007358).

📄 **Read the research proposal:** [PROPOSAL.md](PROPOSAL.md) · **Tasks:** [TASKS.md](TASKS.md)

## Plan

Download ds007358 → pre-register → MNE preprocessing → Welch PSD → specparam (alpha, aperiodic exponent) → mixed models → preprint

## Status

🟡 Pipeline written; pre-registration drafted and awaiting the researcher's review and commit (Nov 2026). Spectral analysis is locked until then (`src/prereg_guard.py`).

## Run order

```
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python src/download.py        # ~12.6 GB, eyes-closed + eyes-open only
.venv/bin/python src/metadata.py        # participants + montage census (no spectra)
.venv/bin/python src/preprocess.py      # epochs + quality metrics (no spectra)
# --- commit preregistration/prereg.md here ---
.venv/bin/python src/psd.py
.venv/bin/python src/fit_specparam.py
.venv/bin/python src/models.py
.venv/bin/python src/robustness.py
.venv/bin/python src/figures.py
```

## Data credit

Vianney et al. (2025), *eNeuro*, doi:10.1523/ENEURO.0006-25.2025; OpenNeuro ds007358 (CC0).
