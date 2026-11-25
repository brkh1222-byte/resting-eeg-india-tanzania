# STATUS (kept current by the pilot agent)

Last update: 2026-11-25, about 10:30 local. All planned work of this session is done and pushed to branch `research-plan`.

## Hard gate (unchanged)
`preregistration/prereg.md` is STATUS: DRAFT and is NOT committed (it is the only untracked file). No spectrum or specparam fit of the real recordings has been computed, plotted or inspected. `src/prereg_guard.py` was not modified. Only the researcher may approve and commit the pre-registration.

## What exists now
| Item | Where |
|---|---|
| Novelty re-check: no overlapping work found (moderate to high confidence) | `notes/novelty.md` |
| 27 references verified against Crossref/PubMed/DataCite, plus claim checks | `paper/references.bib`, `notes/citation_check.md` |
| Simulation validation (11 experiments, 16,800 simulated recordings, and a simulated cohort) | `notes/simulation_validation.md`, `results/simulation/`, `paper/figures/figS*.{png,pdf}` |
| Review of the draft pre-registration, with proposed changes and reasons | `notes/prereg_review.md` |
| Paper draft (intro, data, methods, simulation results, discussion; real results are `\TBD{}`) | `paper/main.tex`; number ledger in `paper/notes.md` |
| Simulator, tests (15 fast + 1 end-to-end, passing), one-command runner | `src/simulate.py`, `tests/test_pipeline.py`, `run_all.sh` |

## The one finding to read first
With the drafted settings, specparam reports an alpha peak in **73–83% of simulated recordings that contain no alpha**. H1 cannot be tested with the drafted presence rule. A threshold of 0.25 on the fitted peak height brings this to 4% (60 s) and 0% (120–180 s). See `notes/prereg_review.md`, item A1.

## What the researcher must do to unlock the real analysis
1. Read `notes/prereg_review.md` (start with the summary and Part A) and decide on each item.
2. Edit `preregistration/prereg.md` accordingly. Make `src/config.py` match it. In particular, if you accept A1, set `PRESENCE_MIN_FITTED_HEIGHT = 0.25`. Items A2 (H2b), A3 (fit-quality rule) and A6 (mean-Welch robustness) need small code changes that were deliberately not made; ask Claude to implement the ones you accept **before** committing.
3. Run `.venv/bin/python -m pytest tests -q` (simulated data only) and check it passes.
4. Delete the `STATUS: DRAFT` line from `prereg.md`. Then:
   `git add preregistration/prereg.md src/config.py && git commit -m "Pre-registration v1" && git push && git tag prereg-v1 && git push --tags`
5. Run `sh run_all.sh` (use `JOBS=1 sh run_all.sh` on a busy machine). Expect several hours, mostly for the 324-version grid. It is restartable for the spectra; logs go to `results/run_logs/`.
6. Not needed for unlocking, but still open: T0.2 (confirm a mentor if wanted; email Sapien Labs about the subject-ID prefixes, the selection of the 2,000, the 128 vs 256 Hz question and the headset model).

## Bugs fixed in this session (none involved real spectra)
- `bitwise_and` error: already fixed in the working tree by the earlier session (recording sub-KAGU1058 eyes-open has no O1/O2). Confirmed by re-running that one recording; a regression test was added. `data/preprocess.log` is stale; the current QC table has 3,052 rows, all `ok`.
- Firmware counters `FwBufferSize`/`FwClockTime` were treated as electrodes in 89 Indian files. `results/qc_summary.csv` still has the old `n_eeg_channels` for those files (not used in any model); it will be corrected the next time `src/preprocess.py` is run.
- A failed specparam fit was counted as "alpha present" in the H2 model; the Holm-adjusted p-values were computed but not used in the decision; the pre-registered no-quality sensitivity analysis was missing; one failing recording would have crashed `psd.py` and lost the whole run.

## Known gaps and doubts
- `paper/main.tex` was not compiled (no LaTeX on this machine).
- The simulations assume Gaussian, stationary noise and specparam's own spectral model. Real false-positive rates may differ.
- Simulation cells have 40–200 repetitions (standard error up to about 5 percentage points).
- The full 324-version grid was only exercised in reduced form on simulated data.
- The Nature Neuroscience 2026 piece by the dataset authors (doi:10.1038/s41593-026-02215-1) has no abstract and was not read; read it before submission. Google Scholar, bioRxiv site search and Semantic Scholar keyword search could not be reached.
- PROPOSAL.md and the header of prereg.md still describe the author as a student with an adult mentor to be confirmed. CLAUDE.md, TASKS.md, README.md and paper/outline.md were updated to the new roles policy; PROPOSAL.md was left as written.
- Simulated-cohort outputs are under the git-ignored `data/sim/cohort/`; regenerate them with the command in `notes/simulation_validation.md`.

## How to resume
Read this file, then `git log --oneline`. Nothing is running in the background.
