# Results notes

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
| Usable eyes-open | 679 | 766 |
| Usable in both conditions (the V1 sample) | 670 | 752 |
| R² ≥ 0.90 | TBD | TBD |

QC facts (results/qc_summary.csv, 2026-11-22; no spectra):
- Excluded for < 60 s clean eyes-closed data: India 14, Tanzania 46 (one Tanzanian file, sub-THMA2619, is 3 s long).
- Median clean eyes-closed data: India 176 s, Tanzania 166 s. Median share of epochs kept: 0.85 / 0.84.
- CQ at O1/O2 = 4 (maximum) in 89% (India) and 96% (Tanzania) of usable eyes-closed recordings.
- Sampling rate: 128 Hz, except 7 Indian participants at 256 Hz (sensitivity check in robustness.py).
- Median blink rate, usable recordings, eyes-closed / eyes-open: India 0.2 / 4.5 per min; Tanzania 0.0 / 5.3 per min (recomputed 2026-11-25; the earlier 4.6 / 6.0 could not be reproduced).
- Of the 60 analysable adults excluded for < 60 s clean data, 17 (India 3, Tanzania 14) have zero clean epochs.

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


---

# Number ledger for `paper/main.tex` (draft of 2026-11-25)

Every number in the draft, with its source. "Sim" = `notes/simulation_validation.md`, computed from `results/simulation/*.csv`. "CC" = `notes/citation_check.md` (verified quotes with URLs). Real-data outcome numbers do not exist yet; they are `\TBD{}` in the draft.

## Literature (Introduction, Data)
| Number or claim in the draft | Source |
|---|---|
| 402 adults, 48 settlements, Tamil Nadu, 14-channel Emotiv EPOC | Parameshwaran & Thiagarajan 2017 (v2, 2019), Methods/Results; CC item c |
| "largely undetected…" (quote); 20% no oscillation in any channel; 40% vs 93.3% above the noise level; "a very broad continuum…" (quote) | same; CC item c |
| Peaks located with the second derivative of the PSD | same, Methods; CC item c |
| 1,199 adults, rural Haryana; alpha peak in 71.3% of eyes-closed recordings; "above the background envelope" | Bhavnani et al. 2022, abstract, Table 3, Methods; CC item a. Note: the 71.3% is of N = 1,194 adult eyes-closed recordings |
| 61 of 63 healthy adults (97%) | Corcoran et al. 2018, abstract; CC item b (97% = 61/63 = 96.8%, our arithmetic) |
| IAF slower in older age | Klimesch 1999 (review); Cesnaite et al. 2023 abstract; Merkin et al. 2023 abstract; CC items e, f |
| Exponent lower (flatter) in older adults | Voytek et al. 2015 abstract; Donoghue et al. 2020 Results; CC item g |
| Merkin and Cesnaite: no age difference in adjusted alpha power; Tröndle: overestimated but still present | abstracts; CC items e, f |
| 7,933 participants; one headset model and protocol; non-specialist field researchers; 12 per country; 2 weeks of training | Vianney et al. 2025, abstract and Methods; CC item d |
| Emotiv FLEX 2 Gel, 16 of 32 electrodes, ear-clip reference; 3 min eyes closed, 3 min eyes open; paper states 256 Hz | Vianney et al. 2025, Methods; CC item d |
| Raw peak = maximum in 7–12 Hz; falls with age in both countries | Vianney et al. 2025, Methods/Results; CC item d |
| Written consent; ethics approvals in India and Tanzania | Vianney et al. 2025, Methods; CC item d |
| Dataset: v1.0.0, 4 Feb 2026, CC0, 2,000 participants, three conditions | OpenNeuro / DataCite; CC item h; `data/ds007358/dataset_description.json` |
| Multinational norms pool different recording systems (Li et al. 2022) | PROPOSAL.md states "nine countries, 12 devices"; these two counts were NOT re-verified, so the draft gives no counts. Verify before adding numbers |

## Sample and QC (Data, Methods)
| Number | Source |
|---|---|
| 1,000 / 1,000; adults 700 / 990; with O1+O2 694 / 832; usable 680 / 786; both conditions 670 / 752 | `results/participants_clean.csv`, `results/qc_summary.csv` (recomputed 2026-11-25) |
| 225 under 18, all Indian | `participants_clean.csv` (`age_group` "<18") |
| 60 excluded for < 60 s; 17 with no clean epoch | `qc_summary.csv` (ec, analysable, not usable: 14 + 46; `clean_sec` = 0: 3 + 14) |
| 128 Hz; 256 Hz for 7 Indian participants | `qc_summary.csv` (`sfreq`, usable ec) |
| India 10 layouts, 981 with the main one; Tanzania 136 layouts, 8–18 electrodes | `results/montage_census.csv` |
| 305 of 680 (45%) Indian and 151 of 786 (19%) Tanzanian usable participants aged 18–24; aged 65+: 1 and 62 | `qc_summary.csv` + `participants_clean.csv` (age groups of usable ec) |
| Income missing for 22 of 680; 436 of 658 in the two lowest of seven bins | same (usable Indian ec: `<1250` 140, `1250-3750` 296) |
| Median clean data 176 s / 166 s; median share of epochs kept 0.85 / 0.85 | `qc_summary.csv`, usable ec |
| CQ at maximum in 89% / 96% | `qc_summary.csv`, usable ec, `CQ_roi == 4` |
| Offset about 0.16 log10 lower with an uncorrected median | log10(ln 2) = −0.159 (property of the median of an exponential distribution) |

## Simulation (Methods 3.7, Results 4.1, Abstract, Discussion)
All from `results/simulation/exp_A.csv … exp_K.csv` via `summary.csv`; tables in Sim sections 2–6.
| Number | Source |
|---|---|
| Design: recordings per experiment (5,120; 800; 1,200; 720; 800; 1,600; 560; 480; 960; 960; 3,600) | `results/simulation/run.log`; exp_K has 36,000 fits = 3,600 recordings × 10 |
| False present 75 / 74 / 73 / 75% (30–180 s); range 65–88% over 16 cells | exp_A, true height 0; Sim section 2 |
| 83 / 78 / 74% in the independent set | exp_K, variant median, min height 0.1, threshold 2 |
| Detection table (heights 0.05–0.2) | exp_A; Sim section 2 |
| Median fit error 0.069 / 0.049 / 0.040 | exp_A and exp_K `fit_error` by length |
| 29 bins in 7–14 Hz | (14 − 7) / 0.25 + 1 |
| False peaks: median fitted height 0.13; 28% below 0.1 | exp_A, true height 0, detected |
| SG detector: 32 / 19 / 26% false; 98–99% at 0.2; 61–86% at 0.1 | exp_A |
| Rules table; chance-peak 95th percentiles 0.25 / 0.17 / 0.13 | exp_K; Sim section 3 |
| Exponent bias 0.014–0.028; SD 0.055 / 0.037 / 0.030 | exp_A; Sim section 4 |
| IAF errors (0.36 / 0.27 / 0.24 Hz at 0.3; 0.25 / 0.19 / 0.19 at 0.5; > 1 Hz rates) | exp_A; Sim section 4 |
| Height overestimate 0.02–0.08 | exp_A (`alpha_pw` − truth, heights 0.2–0.3, ≥ 60 s) |
| Cohort table; 1.1% false absent; 43% / 48% false present; income 0.72–1.55 with 20 of 400; adjusted p = 0.24 | `data/sim/cohort/results/recovery.csv` and `confirmatory.csv` (git-ignored; regenerate with `src/simulate.py cohort --root data/sim/cohort --n-per-site 400 --no-grid`, seed fixed) |
| R² < 0.90 in 94 / 58 / 4% for exponent 0.5 | exp_A |
| Noise floor: exponent −0.20 to −0.27 (40 Hz), −0.35 to −0.44 (25 Hz), about −0.6 (15 Hz), about −0.9 (8 Hz); 43% detection; false present 38 / 23 / 10 / 13% | exp_C |
| Low-pass: +0.22 (43 Hz), +0.78 (35 Hz) | exp_D |
| Window edges: 95% and 93% reported, about 30% wrong by > 1 Hz | exp_E |
| Intermittent alpha: 0.34 / 0.39 at 50%; 0.17 / 0.20 at 20% | exp_F (0.6 + `alpha_pw_bias`) |
| Artefacts: 10% fine; 30%: exponent −0.6 to −0.7, median R² 0.3 | exp_I |
| Line noise up to 200 µV: no effect | exp_B |
| Knee: exponent SD up to three times larger; 3–30 Hz: 91% false present | exp_J |

## Open points for the researcher
- The draft could not be compiled here (no LaTeX on this machine). Brace and environment counts are balanced; compile it once and fix any error.
- `[AUTHORS — TBD]` and `[AI-USE STATEMENT — TBD]` are placeholders. The text of the draft and all code were written by an AI assistant (Claude); the statement must say so.
- 22 `\TBD{}` markers remain; all but the placeholders above depend on the real analysis or on the final pre-registration.
