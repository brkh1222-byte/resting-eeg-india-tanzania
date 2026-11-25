# TASKS: resting-eeg-india-tanzania

**Priority: HIGH (weeks 1–2).** Work top to bottom. Tick boxes as tasks complete. Read PROPOSAL.md and CLAUDE.md first. All analysis settings live in `src/config.py` and must match `preregistration/prereg.md`.

## Phase 0: Setup
- [x] **T0.1** `requirements.txt` (pinned; Python 3.12 venv in `.venv/`) and `src/config.py`.
- [ ] **T0.2** Confirm the adult mentor. With them, email the data owners (Sapien Labs) to ask: (a) do subject-ID prefixes identify the field researcher? (b) how were the 2,000 drawn from the full cohort? (c) does the release include Hadzabe participants?

## Phase 1: Data and pre-registration
- [x] **T1.1** `src/download.py` fetches `participants.tsv` plus the `ec` and `eo` files only (~12.6 GB) from the public S3 bucket into `data/ds007358/`. Re-runnable.
- [x] **T1.2** `src/metadata.py` → `results/participants_clean.csv`, `results/montage_census.csv` (sex/age recoding, montage families, researcher clusters, within-India income rank). Re-run once the download is complete. **No spectra.**
- [x] **T1.2b** Novelty re-check (`notes/novelty.md`, 2026-11-25: no overlapping work found) and verified bibliography (`paper/references.bib`, `notes/citation_check.md`).
- [x] **T1.2c** Simulation validation of the whole pipeline (`src/simulate.py`, `tests/`, `notes/simulation_validation.md`) and critical review of the draft pre-registration (`notes/prereg_review.md`). **Read the review before approving: the drafted presence rule has a false-positive rate of about 75% in simulation.**
- [ ] **T1.3 PRE-REGISTRATION.** `preregistration/prereg.md` is drafted (STATUS: DRAFT). **The researcher reads every section (and `notes/prereg_review.md`), edits, removes the DRAFT line, then commits and pushes** before T2.2. Only the researcher may do this. The spectral scripts refuse to run until then (`src/prereg_guard.py`). Never edit it afterwards; add dated amendments in `preregistration/amendments/`.

## Phase 2: Preprocessing and features
- [x] **T2.1** `src/preprocess.py` (written): 1–45 Hz filter, 4 s epochs with 50% overlap, robust-z and Emotiv-flag epoch rejection, EQ/CQ, interpolated share and blink-rate metrics. Run on 10 subjects first (`--limit 10`), then all. Output `results/qc_summary.csv`. Done 2026-11-22: usable eyes-closed India 680, Tanzania 786.
After T1.3, one command runs T2.2–T3.3: `sh run_all.sh` (it stops at the gate until then).

- [ ] **T2.2** `src/psd.py` (written; gated): median-Welch spectra for usable `ec`/`eo` recordings; 50 Hz line-noise ratio.
- [ ] **T2.3** `src/fit_specparam.py` (written; gated; tested on simulated spectra): primary O1+O2 features, second (Savitzky-Golay) detector, reactivity, and the 324-version robustness grid. Output `results/features.csv`, `results/features_grid.csv`, `results/fit_failures.csv`.
- [ ] **T2.4** QC review: fit-quality distributions, example good and bad fits, and exclusions by site (figure 2 plus a short `paper/notes.md` section).

## Phase 3: Statistics
- [ ] **T3.1** `src/models.py` (written; gated; tested on simulated tables): H1–H5 and V1, Holm correction → `results/confirmatory.csv`, `results/model_tables.txt`.
- [ ] **T3.2** `src/robustness.py` (written; gated): specification curve, leave-one-researcher-out, raw peak-pick comparison, second-detector κ, null calibration → `results/spec_curve.csv`, `results/loro.csv`, `results/robustness_summary.csv`.
- [ ] **T3.3** `src/figures.py` (written; gated): figure 1 participant flow, 2 example fits, 3 presence vs threshold, 4 absence odds ratios, 5 age trends, 6 specification curve → `paper/figures/`.

## Phase 4: Write-up
- [x] **T4.0** Draft `paper/main.tex`: introduction, data, methods, simulation results and discussion written; real-data results are `\TBD{}` placeholders.
- [ ] **T4.1** Fill `paper/notes.md` with every result number and every deviation from the pre-registration. Claude drafts the manuscript in `paper/main.tex` (outline: `paper/outline.md`); the researcher edits and approves it. Authorship and the AI-use statement are placeholders until the researcher decides.
- [ ] **T4.2** Release the derived feature tables and code (Zenodo DOI).
