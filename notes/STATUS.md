# STATUS (kept current by the pilot agent)

Last update: 2026-11-25, step 3 below in progress.

## Hard gate (unchanged)
`preregistration/prereg.md` is STATUS: DRAFT and is NOT committed. No spectrum or specparam fit of the real recordings has been computed, plotted or inspected. Only the researcher may approve and commit it.

## Done
1. Branch `research-plan` created and pushed; existing work committed in 5 pieces (docs, config+metadata, preprocessing, gated pipeline, paper notes). Roles policy updated in CLAUDE.md, TASKS.md, README.md, paper/outline.md (researcher pilots; Claude drafts; placeholders for authors and AI-use statement).
2. `bitwise_and` preprocessing error: already fixed in the working tree by the earlier session (`if roi:` guard in `accepted_epochs`). The recording was sub-KAGU1058 eyes-open, which has no O1/O2. Re-run confirms status ok, usable=False. `data/preprocess.log` is stale. Current `qc_summary.csv`: 3,052 ok, 0 errors.
3. Code fixes (no real spectra involved):
   - `FwBufferSize`/`FwClockTime` (firmware counters in 89 Indian files) were treated as EEG electrodes; now excluded. `metadata.py` re-run: India has 10 layouts (not 11); only India `montage_family` labels changed (not used in any model).
   - `config.py`: `ALPHA_SIM_ROOT` env variable redirects all data/result paths to a simulation folder outside the repo. The guard is unchanged.
   - `preprocess.py`: `prepare(raw)` split out so simulated recordings use the same code.
   - `psd.py`, `fit_specparam.py`, `models.py`, `robustness.py`, `figures.py`: logic moved into `run()` functions (guard stays in `main()`); restartable; failures logged instead of crashing.
   - `models.py`: failed fits now count as "no peak" consistently; Holm-adjusted decision column; Firth logistic sensitivity rows; separation handling; descriptives table.
   - `robustness.py`: added the pre-registered no-quality sensitivity (section 8.6), leave-one-researcher-out ranges, time-domain null calibration.

## In progress
- `src/simulate.py` (simulated recordings with known truth) and `tests/`.
- Two helper agents: novelty search -> `notes/novelty.md`; citation check -> `paper/references.bib`, `notes/citation_check.md`.

## To do
- Simulation validation run and report (`notes/simulation_validation.md`).
- `notes/prereg_review.md`.
- `paper/main.tex`.
- `run_all.sh` one-command runner.

## How to resume
Read this file, then `git log --oneline`. Long jobs write to the scratch simulation folder named in `notes/simulation_validation.md` and are resumable.
