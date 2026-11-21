# TASKS: resting-eeg-india-tanzania

**Priority: HIGH (weeks 1–2).** Work top to bottom. Tick boxes as tasks complete. Read PROPOSAL.md and CLAUDE.md first.

## Phase 0: Setup
- [ ] **T0.1** Create `requirements.txt` (mne, specparam (or fooof), numpy, scipy, pandas, statsmodels, matplotlib, seaborn, openneuro-py, tqdm) and `src/config.py`.

## Phase 1: Data and pre-registration
- [ ] **T1.1** Write `src/download.py` to download ds007358 v1.0.0 to `data/ds007358/` (openneuro-py or `aws s3 sync --no-sign-request s3://openneuro.org/ds007358`).
  *Done when:* there are 2,000 subjects and `participants.tsv` loads.
- [ ] **T1.2** Write `notebooks/01_explore.ipynb` covering:
  - the participants.tsv summary (site × age_group × sex × income, missingness);
  - channel names in 5 EDFs;
  - the recording durations;
  - the subject-ID prefix → field-researcher mapping.

  **Do not compute any spectra yet.**
- [ ] **T1.3 PRE-REGISTRATION.** Finalise `preregistration/prereg.md` from PROPOSAL §4–6: hypotheses, exclusion rules, channel sets, specparam settings, models and alpha-presence criterion. **The student reviews it**, then it is committed and pushed **before T2.3**. Never edit it afterwards; add dated amendments as separate files.

## Phase 2: Preprocessing and features
- [ ] **T2.1** Write `src/preprocess.py`: load the EDF and pick the EEG channels, filter 1–40 Hz, cut 2 s epochs, reject artefacts and flag bad channels, and save the QC metrics. Run it on 10 subjects first.
- [ ] **T2.2** Write `src/psd.py` to compute Welch PSDs for the eyes-closed and eyes-open conditions (posterior channels and all channels).
- [ ] **T2.3** Write `src/fit_specparam.py` to fit every participant and condition. Output `results/features.csv`: alpha present, IAF, alpha power, exponent, offset, theta, R² and error.
  *Done when:* there is one row per participant × condition, and fit failures are logged.
- [ ] **T2.4** Write `notebooks/02_qc.ipynb`: QC dashboard with fit-quality distributions, example good and bad fits, and exclusions by site.

## Phase 3: Statistics
- [ ] **T3.1** Write `src/models.py` to fit the pre-registered mixed models (H1–H5) and save tables to `results/`.
- [ ] **T3.2** Write `src/robustness.py` covering alternative channels, frequency ranges, specparam modes, stricter QC, and the raw peak-pick comparison (Vianney-style).
- [ ] **T3.3** Figures:
  - (1) example spectra with the specparam fit;
  - (2) alpha-presence rate by site × age;
  - (3) IAF and exponent vs age by site;
  - (4) reactivity.

## Phase 4: Write-up
- [ ] **T4.1** Write `paper/notes.md` with bullet results, all numbers and the deviations from the pre-registration. **The student writes the manuscript personally.**
- [ ] **T4.2** Release the derived feature table and code (Zenodo DOI).
