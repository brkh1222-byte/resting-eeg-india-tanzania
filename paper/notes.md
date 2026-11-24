# Results notes (fill in after the pre-registered analysis runs)

Every number used in the paper goes here first, with the file it came from. Leave a cell as TBD until the script has produced it.

## Pre-registration
- Commit hash and date: TBD (printed by `src/psd.py`)
- Amendments: none yet

## Sample (results/qc_summary.csv, participants_clean.csv)
| | India | Tanzania |
|---|---|---|
| All participants | 1,000 | 1,000 |
| Adults, known age group | 700 | 990 |
| + O1 and O2 | 694 | 832 |
| + ≥ 60 s clean eyes-closed data (usable) | 680 | 786 |
| Usable eyes-open (for V1) | 679 | 766 |
| R² ≥ 0.90 | TBD | TBD |

QC facts (results/qc_summary.csv, 2026-11-22; no spectra):
- Excluded for < 60 s clean eyes-closed data: India 14, Tanzania 46 (one Tanzanian file, sub-THMA2619, is 3 s long).
- Median clean eyes-closed data: India 176 s, Tanzania 166 s. Median share of epochs kept: 0.85 / 0.84.
- CQ at O1/O2 = 4 (maximum) in 89% (India) and 96% (Tanzania) of usable eyes-closed recordings.
- Sampling rate: 128 Hz, except 7 Indian participants at 256 Hz (sensitivity check in robustness.py).
- Median blink rate eyes-closed / eyes-open: India 0.2 / 4.6 per min; Tanzania 0.0 / 6.0 per min.

## Confirmatory tests (results/confirmatory.csv)
| Test | India | Tanzania | Supported? |
|---|---|---|---|
| H1 presence, % [95% CI] | TBD | TBD | TBD |
| H2a quality OR [95% CI] | TBD | TBD | TBD |
| H2b income OR [90% CI] | TBD | — | TBD |
| H3 IAF slope, Hz/decade | TBD | TBD | TBD |
| H4 exponent slope, /decade | TBD | TBD | TBD |
| H5 alpha power slope, SD/decade [90% CI] | TBD | TBD | TBD |
| V1 reactivity, % > 0 | TBD | TBD | TBD |

## Robustness (results/robustness_summary.csv)
- Presence range across 324 versions: TBD
- Leave-one-researcher-out range: TBD
- Raw peak-pick vs specparam IAF slope: TBD
- κ specparam vs SG detector: TBD
- Null false-positive rate: TBD

## Deviations from the pre-registration
- None yet
