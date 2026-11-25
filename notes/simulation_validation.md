# Simulation validation of the pipeline (no real data)

Date: 2026-11-25. Code: `src/simulate.py`, `src/figures_sim.py`, `tests/test_pipeline.py`. Raw outputs: `results/simulation/exp_A.csv` … `exp_K.csv`, `summary.csv`. Figures: `paper/figures/figS1_detection`, `figS2_false_present`, `figS3_recovery`.

Reproduce:
```
.venv/bin/python src/simulate.py experiments --out results/simulation --n 40      # about 30 min on one core
.venv/bin/python src/figures_sim.py
.venv/bin/python src/simulate.py cohort --root data/sim/cohort --n-per-site 400 --no-grid
.venv/bin/python -m pytest tests -q            # 15 fast tests
.venv/bin/python -m pytest tests -q -m slow    # simulated end-to-end run, about 2.5 min
```

## 1. What was simulated

Each simulated recording is a Gaussian time series at 128 Hz with a known spectrum: `log10 P(f) = offset − exponent·log10(f) + height·Gaussian(f; IAF, width)`. "Height" is the alpha peak height in log10 units above the 1/f background, the same quantity that specparam reports and that the draft pre-registration thresholds at 0.1. Height 0 means no alpha. Two channels (O1, O2) share 70% of their variance. IAF is drawn from 8–12 Hz, the peak SD from 0.6–1.5 Hz, the offset from 0.5–1.5.

Each recording goes through the **same functions as the real data**: `preprocess.prepare` (1–45 Hz filter), `preprocess.accepted_epochs` (4 s epochs, 50% overlap, rejection), `psd.epoch_spectra` (median Welch), `fit_specparam.fit_one` / `features` / `sg_detect` with the primary settings in `src/config.py`.

"Recording length" below is the clean length (the `clean_sec` of the QC table). The real usable recordings have 60 s at least and a median of 166–176 s.

| Exp | Question | Cells × repetitions |
|---|---|---|
| A | exponent (0.5, 1, 1.5, 2) × alpha height (0–0.8) × length (30, 60, 120, 180 s) | 128 × 40 = 5,120 |
| B | 50 Hz line noise, amplitude 0–200 µV | 10 × 80 |
| C | white sensor-noise floor crossing the 1/f at 40, 25, 15, 8 Hz | 15 × 80 |
| D | hardware-like low-pass at 43 or 35 Hz | 9 × 80 |
| E | alpha centre at the edges of the 7–14 Hz window | 10 × 80 |
| F | intermittent alpha (on 100–20% of the time); median vs mean Welch | 20 × 80 |
| G | theta or beta peaks without alpha; very broad or narrow alpha | 7 × 80 |
| H | 128 Hz vs 256 Hz | 6 × 80 |
| I | artefact bursts and headset "interpolated" flags | 12 × 80 |
| J | fit ranges and aperiodic modes of the robustness grid | 12 × 80 |
| K | threshold calibration: 7 minimum peak heights, peak threshold 3 SD, mean Welch | 18 × 200 recordings, 10 fits each |

Precision: a proportion from 80 simulations has a standard error of up to 5.6 percentage points; from 160, up to 4; from 200, up to 3.5. Treat differences of a few points as noise.

## 2. Main result: the draft presence rule reports alpha in about three of four recordings that have none

Share of recordings in which the primary settings (minimum peak height 0.1, peak threshold 2 SD) return a peak in 7–14 Hz. Experiment A, pooled over the four exponents (160 simulations per cell):

| True alpha height | 30 s | 60 s | 120 s | 180 s |
|---|---|---|---|---|
| **0 (no alpha)** | **75%** | **74%** | **73%** | **75%** |
| 0.05 | 87% | 89% | 89% | 92% |
| 0.10 | 92% | 91% | 99% | 99% |
| 0.15 | 96% | 98% | 100% | 100% |
| ≥ 0.20 | 100% | 100% | 100% | 100% |

- **False "present" rate: 73–75%**, at every recording length and every exponent (range over the 16 exponent × length cells: 65–88%, n = 40 each). Experiment K, with other random draws, gives 83% (60 s), 78% (120 s), 74% (180 s), n = 200 each.
- **False "absent" rate** for a true peak of height ≥ 0.2: 0%. For height 0.1: 9% at 60 s, 1% at 120–180 s.
- Why: with 0.25 Hz bins and 1–3 minutes of data, each bin of the median spectrum has random scatter of about 0.04–0.07 log10 (the median fit error is 0.069 at 60 s, 0.049 at 120 s, 0.040 at 180 s). The 7–14 Hz window has 29 bins. A bump of 0.1 somewhere in it is common by chance, and the 2 SD peak threshold is measured against the same scatter.
- The false peaks are small and often narrow: median fitted height 0.13; 28% have a fitted height **below** 0.1 (the minimum height is applied during the search, not to the final fit); more than a quarter sit at the lower width limit (1.0 Hz; median width 1.1 Hz); 20% are 6–8 Hz wide.
- **Consequence for H1.** With this rule, a sample with no alpha at all would show about 75% "present", close to the 80% bar. The presence rate could not distinguish "nearly everyone has alpha" from "many do not". The earlier code-test figure of "about 10% at noise level 0.03" does not apply to recordings of this length.
- The simulated cohort (section 5) agrees: 43–48% of participants planted with no alpha were called "present" (lower than 75% because that cohort has a sensor-noise floor, see experiment C).

The second detector (Savitzky-Golay) is better but not good: false "present" 32% (60 s), 19% (120 s), 26% (180 s); it finds a height-0.2 peak in 98–99% of recordings and a height-0.1 peak in 61–86%.

## 3. Which rule would work (experiment K)

False "present" rate (true height 0) and detection rate by true height, for alternative rules. n = 200 per cell; exponent drawn from 0.5–2.

| Rule | False present 60 / 120 / 180 s | Detects height 0.2 | height 0.3 | height 0.4 | height 0.6 |
|---|---|---|---|---|---|
| Draft: min height 0.10, threshold 2 SD | 83 / 78 / 74% | 100% | 100% | 100% | 100% |
| Peak threshold 3 SD (min height 0.10) | 24 / 23 / 22% | 94% | 100% | 100% | 100% |
| specparam min height 0.20 | 82 / 29 / 3% | 100% | 100% | 100% | 100% |
| specparam min height 0.25 | 60 / 3 / 0% | 86% | 100% | 100% | 100% |
| specparam min height 0.30 | 22 / 0 / 0% | 54% | 98% | 100% | 100% |
| specparam min height 0.40 | 0 / 0 / 0% | 7% | 46% | 94% | 100% |
| **Fitted height ≥ 0.25** (fit as drafted, then threshold the fitted height) | **4 / 0 / 0%** | 69 / 52 / 34% | 98 / 100 / 99% | 100% | 100% |
| Fitted height ≥ 0.30 | 1 / 0 / 0% | 32 / 11 / 4% | 89 / 88 / 78% | 98–100% | 100% |
| Fitted height ≥ 0.20 | 21 / 0 / 0% | 88 / 90 / 86% | 99–100% | 100% | 100% |
| Mean Welch, min height 0.10 | 82 / 80 / 62% | 100% | 100% | 100% | 100% |

(Detection columns are pooled over lengths unless three values are given for 60 / 120 / 180 s. The "fitted height" rows were computed from fits with minimum height 0.05; for thresholds of 0.2 and above the result with the drafted 0.1 is expected to be the same, since both fits return the same large peaks.)

Size of the largest chance peak in 7–14 Hz on no-alpha recordings (fitted height): 95th percentile 0.25 at 60 s, 0.17 at 120 s, 0.13 at 180 s; 99th percentile 0.29, 0.20, 0.15.

Reading:
- A rule of **fitted height ≥ 0.25** keeps false "present" at about 4% for the shortest allowed recordings and near 0% for typical ones, and finds essentially every peak of true height ≥ 0.3 (a factor of 2 in power above the background).
- No rule can tell a peak of height 0.1–0.2 from chance in 1–3 minutes of data at 0.25 Hz resolution. "Weak alpha" in that range is below the resolution of this dataset. This is a limit of the data, and the paper should say so.
- Raising specparam's own `min_peak_height` works less cleanly than thresholding the fitted height, because the search threshold is applied to the raw residual and admits noise spikes at short lengths (22% false present at 0.30 for 60 s).
- A width rule (rejecting peaks at the width limits) removes true peaks too and is not recommended (detection of a height-0.6 peak fell to 78–96%).

`src/config.py` now has `PRESENCE_MIN_FITTED_HEIGHT = None`. `None` reproduces the draft rule. Setting it to 0.25 applies the rule above. The researcher decides (see `notes/prereg_review.md`, item A1).

## 4. Recovery accuracy (experiment A, primary settings)

| Quantity | Result |
|---|---|
| Exponent bias | +0.014 to +0.028 in every cell (truth 0.5–2.0); negligible |
| Exponent SD of error | 0.08 (30 s), 0.055 (60 s), 0.037 (120 s), 0.030 (180 s) |
| IAF mean absolute error, true height 0.3 | 0.36 Hz (60 s), 0.27 (120 s), 0.24 (180 s) |
| IAF mean absolute error, true height 0.5 | 0.25, 0.19, 0.19 Hz |
| IAF mean absolute error, true height 0.8 | 0.19, 0.15, 0.13 Hz |
| IAF error > 1 Hz, true height 0.2 | 8% (60 s), 8% (120 s), 3% (180 s) |
| IAF error > 1 Hz, true height ≥ 0.5 | ≤ 1% at ≥ 60 s |
| IAF mean absolute error, true height 0.1 | 0.98, 0.83, 0.59 Hz (the "peak" is often a chance peak elsewhere in the band) |
| Fitted height minus true height | +0.02 to +0.08 for true 0.2–0.3 at ≥ 60 s; within ±0.02 for 0.8 at ≥ 120 s (small peaks are overestimated: winner's curse) |
| Raw 7–12 Hz maximum (Vianney-style), mean absolute error | 0.2–0.7 Hz for height ≥ 0.4 inside 7–12 Hz; 5–6 Hz for a true peak at 13–13.75 Hz (outside its band); about 2.5 Hz when there is no alpha (it always returns a value) |

128 Hz vs 256 Hz (experiment H): no difference beyond noise (false present 80% vs 75%; exponent bias +0.01 to +0.03 in both).

## 5. End-to-end run on a simulated cohort

`src/simulate.py cohort` builds a two-site study (400 per site here) with planted effects, writes the same tables the real pipeline reads, and runs `fit_specparam.run`, `models.run`, and (in the slow test, with a reduced grid) `robustness.run` and `figures.run`. Draft presence rule.

| Quantity | Planted | India (sim) | Tanzania (sim) |
|---|---|---|---|
| IAF slope, Hz per decade (H3) | −0.12 | −0.144 [−0.213, −0.076] | −0.061 [−0.124, 0.002] |
| Exponent slope per decade (H4) | −0.06 | −0.062 [−0.081, −0.044] | −0.069 [−0.085, −0.053] |
| Alpha power slope, SD per decade (H5) | 0 | −0.039 [−0.099, 0.022] | 0.005 [−0.052, 0.062] |
| Share called present (H1); planted share in brackets | — | 95.0% (93.0%) | 95.0% (92.2%) |
| False "absent" among planted alpha | — | 1.1% | 1.1% |
| False "present" among no planted alpha | — | 43% | 48% |
| IAF mean absolute error | — | 0.24 Hz | 0.17 Hz |

All planted slopes lie inside their 95% (H3, H4) or 90% (H5) intervals. Note that H5 in simulated India was **not** declared equivalent although the planted effect is exactly zero (interval −0.099 to 0.022 passes, but its Holm-adjusted p is 0.24), and the H2b income interval was 0.72–1.55 with a planted effect of zero: see the power notes in `notes/prereg_review.md`.

## 6. Where the method breaks

| Condition | What happens | Experiment |
|---|---|---|
| No alpha, draft rule | 73–83% false "present" | A, K |
| Alpha height 0.1–0.2 | Cannot be separated from chance peaks at any threshold | K |
| Recording of 30 s | Exponent SD 0.08; IAF error > 1 Hz in 16% at height 0.3; R² < 0.90 for all spectra with exponent 0.5 | A |
| **R² ≥ 0.90 floor with flat spectra** | R² depends on the exponent, not only on fit quality. With exponent 0.5: 94% of fits fall below 0.90 at 60 s, 58% at 120 s, 4% at 180 s. With exponent 1.0: 74% at 30 s, 0% from 60 s. Exponent ≥ 1.5: 0%. The mean absolute fit error is the same for all exponents (0.069 / 0.049 / 0.039 at 60 / 120 / 180 s). So the floor removes flat-spectrum recordings selectively, which would bias H4 (and H3, H5). | A, K |
| Sensor-noise floor | A white noise floor as strong as the 1/f at 40 Hz lowers the fitted exponent by 0.2–0.27; at 25 Hz by 0.35–0.44; at 15 Hz by 0.6; at 8 Hz by 0.9, and then a height-0.2 peak is found in only 43% (specparam) or 1% (SG). The exponent of a noisy recording is therefore biased towards flat, which links the exponent to recording quality. | C |
| Hardware-like low-pass inside the fit range | A low-pass at 43 Hz raises the fitted exponent by 0.22; at 35 Hz by 0.78, and the SG detector then finds nothing (0–3%). The headset's real filter is not documented in the files, so the absolute exponent should be read with care; the 3–30 Hz grid version is the check. | D |
| Alpha centre at the window edge | Centre 7.0 Hz: 95% detected but IAF error > 1 Hz in 30%; 6.5 Hz: 65% "present" (all chance). Centre 14.0 Hz: 93%, error > 1 Hz in 31%. Inside 7.25–13.75 Hz detection is 100%. | E |
| Intermittent alpha | With the draft rule detection stays ≥ 94% even when alpha is on 20% of the time, but the fitted height drops (true 0.6 → about 0.17 with the median, 0.20 with the mean, at 20% on-time; 0.34 vs 0.39 at 50%). With a stricter height threshold, people with intermittent alpha would be counted "absent". The median loses a little more height than the mean and has larger IAF error (0.56 vs 0.28 Hz at 20% on-time). | F |
| Peaks next to the alpha window, no alpha | A 15 Hz peak: 80% "present" (not above the 74% chance level, but IAF is then meaningless); 6–6.5 Hz theta: 50–59%; 20 Hz beta: 44%. | G |
| Very broad alpha (SD 3 Hz) | Detected 100%, but IAF error > 1 Hz in 31% | G |
| 30% of the recording covered by large bursts | The within-person outlier rule stops working (the "typical" epoch is itself contaminated): no epochs are rejected, the exponent is off by −0.6 to −0.7 with SD 0.5, median R² 0.3. At 10% bursts the rule works and estimates are unaffected. | I |
| 50 Hz line noise | No effect on detection, IAF or exponent up to 200 µV amplitude (line-noise ratio 45,000), because 50 Hz is outside the 2–40 Hz fit range. | B |
| Knee mode on spectra without a knee | Exponent SD is up to three times larger (0.05–0.16 vs 0.04–0.05); false present 80–89%. | J |
| Fit range 3–30 Hz | False present 91% (shorter range, fewer points to anchor the background). | J |

Not a failure but worth knowing: headset "interpolated" flags at a rate of 0.05% of samples remove about 13% of epochs (180 s → 156 s clean), because any flagged sample rejects the whole epoch.

## 7. Limits of this validation

- Simulated noise is stationary and Gaussian, and the spectrum follows specparam's own model exactly. Real EEG has a non-Gaussian, non-stationary background, muscle activity, and possibly a spectral knee. Real false-positive rates may differ in either direction. The time-domain null calibration in `src/robustness.py` estimates them for the fitted parameters of each site, but under the same Gaussian assumption.
- The true spectral shape of this headset (built-in filters) is not known to us before the real spectra are seen.
- Cells have 40–200 repetitions; see the precision note in section 1.
- The full 324-version grid was not run on a simulated cohort (only a reduced grid, in the slow test). On this machine one specparam fit takes 0.05–0.15 s, and the full grid needs roughly 216–400 fits per participant, so the real grid run is expected to take **several hours** on two cores.
