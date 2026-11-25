# resting-eeg-india-tanzania

Is alpha really missing? This repo models the periodic and aperiodic components of resting EEG across age and income in 2,000 adults from India and Tanzania, all recorded on identical hardware (OpenNeuro ds007358).

📄 **Read the research proposal:** [PROPOSAL.md](PROPOSAL.md) · **Tasks:** [TASKS.md](TASKS.md)

## Plan

Download ds007358 → pre-register → MNE preprocessing → Welch PSD → specparam (alpha, aperiodic exponent) → mixed models → preprint

## Status

🟡 Nov 2026: pipeline written and tested on simulated data; paper drafted up to the real-data results. The pre-registration is a draft awaiting the researcher's review and commit, and the spectral analysis of the real recordings is locked until then (`src/prereg_guard.py`).

- Simulation validation: [notes/simulation_validation.md](notes/simulation_validation.md)
- Review of the draft pre-registration: [notes/prereg_review.md](notes/prereg_review.md)
- Novelty check: [notes/novelty.md](notes/novelty.md) · Status log: [notes/STATUS.md](notes/STATUS.md)
- Paper draft: [paper/main.tex](paper/main.tex)

## Run order

```
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python src/download.py        # ~12.6 GB, eyes-closed + eyes-open only
.venv/bin/python src/metadata.py        # participants + montage census (no spectra)
.venv/bin/python src/preprocess.py      # epochs + quality metrics (no spectra)
.venv/bin/python -m pytest tests -q     # tests on simulated data only
# --- the researcher approves and commits preregistration/prereg.md here ---
sh run_all.sh                           # psd -> fit_specparam -> models -> robustness -> figures
```

## Data credit

Vianney et al. (2025), *eNeuro*, doi:10.1523/ENEURO.0006-25.2025; OpenNeuro ds007358 (CC0).
