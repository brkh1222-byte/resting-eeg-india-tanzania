# Review of the draft pre-registration (`preregistration/prereg.md`)

Reviewer: the pilot agent (Claude), 2026-11-25. `prereg.md` itself was **not edited**. Each item below is a proposed change with its reason. Mark each one **accept / reject / change** and edit `prereg.md` yourself. Items are ordered by importance within each part. "Sim" refers to `notes/simulation_validation.md`.

No spectrum of the real recordings was computed for this review. It uses the draft text, the code, the metadata tables, the time-domain QC table and simulated recordings only.

## Summary: what needs a decision before you approve

1. **A1. The presence rule does not work as drafted.** On simulated recordings with no alpha, it reports a peak in about 75% of cases. H1 cannot be tested with it.
2. **A2. H2b (income equivalence) cannot succeed with this sample**, even if the true effect is exactly zero.
3. **A3. The R² ≥ 0.90 floor removes flat-spectrum recordings selectively**, which can bias H4.
4. **C1. The Holm rule is ambiguous**; a concrete reading is implemented and needs your agreement.
5. Parts B and C list smaller corrections. Part D lists what I checked and found consistent.

## Part A. Problems that change what the study can conclude

### A1. "Alpha present" (sections 3, 6): the false-positive rate is about 75%

- **Draft:** alpha is present if specparam returns at least one peak centred in 7–14 Hz (settings: minimum height 0.1, peak threshold 2 SD).
- **Evidence (Sim, sections 2–3):** on simulated 128 Hz recordings with a pure 1/f spectrum and no alpha, this rule says "present" in 73–83% of recordings at every length from 30 to 180 s. The second (Savitzky-Golay) detector says "present" in 19–32%. The cause is the random scatter of a 0.25 Hz-resolution spectrum from 1–3 minutes of data (0.04–0.07 log10 per bin), against a height threshold of 0.1.
- **Why it matters:** H1 asks whether presence exceeds 80%. A sample with no alpha at all would score about 75%. H2 ("what predicts a missing peak") would be modelling mostly noise, since most real absences would be hidden.
- **Proposed change (recommended):** keep the fit settings, and define *present* as: **the tallest fitted peak in 7–14 Hz has a fitted height of at least 0.25 log10**. In simulation this gives false "present" of 4% at 60 s and about 0% at 120–180 s, and detects 98–100% of peaks whose true height is 0.3 or more. To switch it on, set `PRESENCE_MIN_FITTED_HEIGHT = 0.25` in `src/config.py` (it is `None` now, which reproduces the draft).
- **What you give up:** peaks of true height 0.1–0.2 cannot be separated from chance at any threshold with this much data (0.25: 34–69% detected at height 0.2). State in the pre-registration that "present" means "an alpha peak at least about twice the background power", and that weaker alpha is below the resolution of the data.
- **Alternatives:** (b) fitted height ≥ 0.30 (false present ≤ 1%, but only 78–89% of true 0.3 peaks found); (c) a length-dependent threshold equal to the 95th percentile of chance peaks (0.25 at 60 s, 0.17 at 120 s, 0.13 at 180 s; more sensitive but harder to explain); (d) keep the draft rule and reinterpret H1 as descriptive only (not recommended).
- **Also change:**
  - §8.1: add 0.25 to the grid of thresholds if not already there (it is: 0.05–0.30 in steps of 0.05). Say whether the grid varies specparam's search threshold (current code) or the fitted-height threshold. The two behave differently at 60 s (Sim, section 3).
  - §8.4: the SG detector's own false-positive rate (19–32%) should be stated next to κ.
  - §8.5: report the time-domain null rate for the rule actually used.
  - H1's 80% bar and the comparison values (71% in Bhavnani et al., 61 of 63 in Corcoran et al.) stay meaningful only with a rule whose false-positive rate is low.
  - V1 (reactivity) does not depend on the presence rule and needs no change.

### A2. H2b (income equivalence, India): no realistic chance of success

- **Draft:** H2b is supported if the 90% CI of the income odds ratio lies within 0.80–1.25.
- **Evidence:** the width of that interval depends on the number of missing peaks. With 658 Indian participants in the model and a true odds ratio of exactly 1, the approximate chance of the interval fitting inside 0.80–1.25 is: 0% if 5% or 10% of peaks are missing, 17% at 15%, 34% at 20%, 54% at 30%. (Normal approximation, SE of the log odds ratio ≈ 1.1/√(n·p·(1−p)); my calculation, in this review only.) In the simulated cohort with a planted effect of zero and 5% missing, the interval was 0.72–1.55.
- **Why it matters:** a hypothesis that cannot be supported even when true is not a test. A reader could take "H2b not supported" as evidence that income matters.
- **Proposed change (choose one):**
  - (a) Recommended: move the equivalence claim to a **continuous** outcome, which has far more power: "in India, the association between income rank and alpha power above the background (all usable recordings with a peak, or the 1/f-removed power at 7–14 Hz for everyone) lies within ±0.10 SD per SD of income rank". Keep the odds ratio for a missing peak as a reported estimate with its interval, without a pass/fail rule.
  - (b) Keep H2b, widen the bounds (for example 0.67–1.50), and state the power for the absence rate that is eventually observed.
  - (c) Keep H2b as drafted and add this sentence: "If fewer than 30% of peaks are missing, this test has less than about 50% power even under exact equivalence; a failure will be reported as inconclusive, not as evidence of an income effect."
- The Holm family size (11) changes only if H2b is removed.

### A3. R² ≥ 0.90 floor for H3–H5 (section 4.5): it selects on the exponent

- **Evidence (Sim, section 6):** R² measures how much of the spectrum's variance the model explains, and a flat spectrum has little variance to explain. In simulation, perfectly well-fitted spectra with exponent 0.5 fall below 0.90 in 94% of 60 s recordings, 58% of 120 s recordings and 4% of 180 s recordings; spectra with exponent ≥ 1.5 never do. The mean absolute fit error is identical for all exponents.
- **Why it matters:** H4 tests whether the exponent falls with age. A floor that removes low-exponent recordings (more often short ones) truncates the outcome variable and can weaken or distort the age slope. A sensor-noise floor also flattens the spectrum (Sim, experiment C), so low-quality recordings would be removed for the wrong reason.
- **Proposed change:** replace the floor with a rule on the **fit error**: "H3–H5 use fits with mean absolute error ≤ 0.10 log10" (in simulation the 99th percentile of the error for clean data is 0.08 at 60 s and 0.05 at 180 s, so 0.10 flags only genuinely poor fits). Keep R² ≥ 0.90 as a robustness version. Needs a small code change in `models.py::load` (`good_fit`), which I have **not** made because it changes a confirmatory rule.

### A4. Power of the other tests (for information)

Approximate, from the usable sample sizes and age spread (India: n = 680, SD of age 1.31 decades; Tanzania: n = 786, SD 1.54), assuming a between-person SD of 1 Hz for IAF and 0.3 for the exponent (assumptions, not data):

| Test | India | Tanzania |
|---|---|---|
| H1: power if true presence is 82% / 84% / 86% | 25% / 76% / 99% | 29% / 83% / 100% |
| H3: power for a true slope of −0.05 / −0.10 / −0.15 Hz per decade | 37% / 90% / 100% | 53% / 98% / 100% |
| H4: power for a true slope of −0.02 / −0.04 per decade | 62% / 100% | 82% / 100% |
| H5: chance of declaring equivalence if the true slope is 0 / 0.03 / 0.05 SD per decade | 89% / 73% / 49% | 99% / 89% / 66% |

- These figures are **before** Holm's correction, which lowers them.
- H3: Vianney et al. report a raw drop of about 0.9 Hz (India) and 0.6 Hz (Tanzania) across roughly five decades, i.e. −0.1 to −0.2 Hz per decade, so power is adequate.
- H5: the literature is not unanimous. Merkin et al. (2023) and Cesnaite et al. (2023) found no age effect on aperiodic-adjusted alpha power; Tröndle et al. (2023, N = 533) found that it is overestimated by conventional analyses but still present. The draft (and PROPOSAL.md) cites only the first two. Add Tröndle et al. and say that H5 may fail for a substantive reason.
- H5 is conditional on a peak being present. With a stricter presence rule (A1), people with weak alpha drop out of H5, and if weak alpha is more common in older people the slope is biased towards zero. Add a companion analysis that does not condition on a peak: the mean 1/f-removed power in 7–14 Hz for all usable recordings (the code already computes this quantity for reactivity).

### A5. The exponent depends on recording quality and on the headset's filters

- **Evidence (Sim, experiments C and D):** broadband sensor noise flattens the fitted exponent by 0.2–0.9 depending on its level; a low-pass filter inside the 2–40 Hz range steepens it by 0.2–0.8. Neither is known for this headset before the spectra are seen.
- **Proposed change:** (i) say in §6 that exponents are comparable within this dataset but not with laboratory values; (ii) make the 3–30 Hz fit range a named sensitivity analysis for H4, not only one cell of the grid; (iii) keep quality as a covariate in H4 (already there) and report the quality coefficient.

### A6. Median Welch and intermittent alpha

- **Evidence (Sim, experiment F):** if alpha is present only part of the time, its fitted height drops (true 0.6, on 50% of the time: 0.34 with the median, 0.39 with the mean). With a height threshold (A1), a person with intermittent alpha can be counted as "absent". The median is slightly worse than the mean here.
- **Proposed change:** state that "present" refers to alpha that is sustained over the recording, and add mean-Welch spectra as a robustness version (`psd.epoch_spectra(average="mean")` exists; saving a second set of spectra needs a small change in `psd.py`, not made).

### A7. Alpha window edges

- **Evidence (Sim, experiment E):** a true peak centred at exactly 7 or 14 Hz is found in 93–95% of cases, but its frequency is wrong by more than 1 Hz in about 30%. Peaks at 6.5 or 14.5 Hz are (correctly) not counted.
- **Proposed change:** none to the rule. Report how many IAF estimates fall within 0.5 Hz of either edge.


## Part B. Facts in the draft that do not match the data or the code

| # | Section | Draft says | What I found | Proposed text |
|---|---|---|---|---|
| B1 | §1 | "India 1 layout; Tanzania 136 layouts" | India has **10** layouts among its 1,000 participants; 981 share one 14-channel layout. (The earlier census said 11, because two firmware counters, `FwBufferSize` and `FwClockTime`, in 89 Indian files were counted as electrodes. Fixed in `src/config.py`.) Among the 680 usable Indian adults, 669 have the main layout. | "India: 10 layouts, one of which covers 981 of 1,000 participants; Tanzania: 136 layouts." |
| B2 | §5.2 and Data | Sampling rate 128 Hz (256 Hz for 7) | Correct for the files. But Vianney et al. (2025) state "downsampled to 256 Hz", and describe a 16-electrode Emotiv FLEX 2 Gel montage, while most Indian files have the 14-channel EPOC-style layout. | Add one sentence: "The public files are at 128 Hz, although the source paper states 256 Hz; the reason is unknown and is a question for the data owners." Avoid "identical hardware" until they confirm. |
| B3 | §7 | "researcher is a fixed effect because there are only 9–13 clusters per site" | In the usable sample: India **6** groups plus "other" (7 people); Tanzania **13**. | "6 groups plus a small 'other' group in India, 13 in Tanzania." |
| B4 | §6 | Montage family (Tanzania): "the three most common montages, plus 'other'" | The third most common Tanzanian montage has no O1/O2, so the analysable sample has only **Ta1 (491), Ta2 (120), other (175)**. | "The two most common montages among analysable participants, plus 'other'." |
| B5 | §1 | "median eyes-open blink rate is 4.6 (India) and 6.0 (Tanzania) per minute" | In the current `results/qc_summary.csv`, usable eyes-open recordings give **4.5 and 5.3**. I could not reproduce 4.6/6.0 (possibly a different subset). | Use 4.5 and 5.3, or state the subset. |
| B6 | §4.3 | Eyes-open recording "must meet the same 60 s rule" | The code also requires O1 and O2 in the eyes-open file (one Indian eyes-open file, sub-KAGU1058, lacks them). Participants usable in both conditions: India 670, Tanzania 752. | Add "and must contain O1 and O2". |
| B7 | §6 | "Alpha present: at least one fitted peak with centre frequency 7–14 Hz" (PROPOSAL adds "≥ 0.1 log10 above the 1/f fit") | In `fooof`, the minimum height is applied while searching for peaks. The **final fitted** height can be lower. See Sim for how often. | Say which is meant: "a peak returned by the fit" (current code) or "a returned peak whose fitted height is ≥ the threshold". |
| B8 | §6 | "the median across epochs" | The code does not rescale the median to the mean (factor about ln 2). The offset is therefore about 0.16 log10 lower than a mean-Welch offset. Exponent and peak heights are unaffected. | Add: "The median is not bias-corrected; offsets are not comparable with mean-Welch offsets." |
| B9 | §8.1 | "any single posterior channel" | The code's rule: present if **any** posterior channel has a peak; IAF and power from the channel with the tallest peak; exponent = mean over channels; R² = minimum over channels. With several channels this version has several chances to find a peak, so it has a higher false-positive rate by construction. | State the rule and the caveat. |
| B10 | §8.1 | R² floor is one of the grid factors | For presence, the primary analysis (H1) uses all recordings, i.e. the "no floor" version. In the grid, the floor also removes recordings from the presence rate. | State that the grid version matching H1 is "O1+O2, 2–40 Hz, fixed, 0.10, no floor". |
| B11 | §8.1 | Fit range 1–40 Hz | 1 Hz is the edge of the 1–45 Hz high-pass filter, so the lowest bins of this range are attenuated by the filter. | Keep as a robustness version, but say so; or use 1.5–40 Hz. |
| B12 | §8.5 | Null calibration: "noise level drawn from the observed fits"; "in code tests at noise level 0.03, the rate was about 10%" | (a) The fit error is a mean absolute error, about 0.8 × the noise SD, so this understates the noise. (b) White noise in log power is not what a median periodogram produces. (c) The "about 10%" figure does not hold at realistic recording lengths: see Sim. I added a **time-domain** null (aperiodic-only recordings of each participant's length, exponent and offset, through the whole pipeline) next to the drafted one in `src/robustness.py`. | Pre-register the time-domain version as the primary null calibration and delete the "about 10%" sentence. |
| B13 | §8.6 | "H2–H5 repeated without the quality covariate" | Was not implemented. Now implemented (`results/sensitivity_no_quality.csv`). H2a cannot be run without quality, so this applies to H2b and H3–H5. | "H2b and H3–H5 repeated…" |
| B14 | header | "Author: Berkh (student researcher). Adult mentor: [to be confirmed]"; "prepared with an AI assistant … for the student author" | Project policy changed (CLAUDE.md): authorship is undecided and the paper carries an AI-use disclosure. | Your decision. Suggested: say plainly that the draft and the code were written by an AI assistant (Claude) under your direction, and that you reviewed and approved every section. |

## Part C. Rules that are ambiguous or incomplete

| # | Topic | Problem | Proposed rule (already implemented in code unless stated) |
|---|---|---|---|
| C1 | Holm correction (§7) | The family mixes rules judged at different levels: one-sided .025 (H1 via the CI, H3, H4), two-sided .05 (H2a) and TOST at .05 (H2b, H5). "Supported only if its decision rule holds after correction" does not say which p-value is corrected or against what level. The old code computed Holm p-values but ignored them in the "supported" column. | For H1, H3 and H4, double the one-sided p. For H2a use the two-sided p. For H2b and H5 use the TOST p. Apply Holm to these 11 values. A hypothesis is supported if **its raw rule holds and its Holm-adjusted p < .05**. For H1 the p-value is the exact one-sided binomial test against 0.80. (`models.py::holm`, columns `p_family`, `p_holm`, `supported_raw`, `supported`.) |
| C2 | Failed or impossible models | No rule for a logistic model that cannot be estimated (perfect separation: for example a field-researcher group with no missing peaks) or for a specparam fit that fails. | (a) A failed specparam fit counts as "no peak" in H1, H2 and the grid, and is listed in `results/fit_failures.csv`. (b) A confirmatory model that cannot be fitted stays in the Holm family with p = 1 and is reported as "not supported: model not estimable". (c) Firth's penalised logistic regression is reported next to the ordinary fit as a sensitivity analysis (implemented; not confirmatory). Decide whether Firth should instead be the **primary** estimator for H2. I recommend that, because with few missing peaks and 8–17 covariates the ordinary fit is fragile. |
| C3 | H2 sample | With about 17 parameters in India (6 researcher dummies, sex, age, quality, income) and 17+ in Tanzania, the rule of thumb of 10 events per parameter needs about 170 missing peaks. | Pre-register a simpler fallback when there are fewer than 10 missing peaks per parameter: drop the field-researcher fixed effect from the H2 model (keep it in H3–H5) and report both. Not implemented; needs your decision. |
| C4 | Sex missing (§4.6) | 9 usable Indian participants have no sex and drop out of every model (all models include sex), but stay in H1. | Fine, but say so explicitly: "H1 n = 680; model n ≤ 671 in India". |
| C5 | Income (§3, H2b) | "per SD of within-site income rank": the rank is computed over the 694 analysable adults, not the 680 usable or the 658 in the model. 436 of 658 are in the two lowest bins, so the rank is close to a three-level variable. | State where the rank is computed. Consider the ordinal bin index (0–6) as a robustness version. |
| C6 | Quality composite (§5.7) | Missing values of a component are replaced by the site mean (code), which is not stated. CQ is at its maximum in 89–96% of recordings, so it carries almost no information. The line-noise ratio is computed on the whole unfiltered recording, including rejected epochs. | State these three facts. |
| C7 | Epoch rejection (§5.5) | "Any interpolated or saturated sample" rejects the epoch. 17 analysable adults (3 India, 14 Tanzania) have **zero** clean epochs although only 2–34% of the samples are flagged in recordings of this kind, because the flags are spread evenly. | Keep the rule (it is conservative), but report these 17 as a named exclusion category. Changing the rule now is allowed (no outcome has been seen) but would need a new QC run. |
| C8 | 256 Hz recordings | Analysed at native rate; sensitivity analysis without them is implemented. Sim shows no difference between 128 and 256 Hz. | No change. |
| C9 | Age (§6) | One usable Indian participant is 65–74; one Tanzanian is "85+" (coded 87). A linear slope gives such points high leverage in principle (HC3 errors help). | Add a sensitivity analysis that merges 65+ into one group at its midpoint, or state that none is planned. |
| C10 | V1 | Clear. Note that V1 uses participants with both conditions usable (670 and 752), not all usable participants. | State the n rule. |
| C11 | Figure 2 | The example fits are chosen as the largest peak, the smallest peak and the best-fitting no-peak recording. | Fine for illustration, but say in the caption that they are extremes; or pre-specify random picks with a fixed seed. |
| C12 | What "committed" means | The guard needs the file committed without the DRAFT line. A local commit has no public timestamp. | Add: "pushed to the public GitHub repository and tagged `prereg-v1` before `run_all.sh` is started; the tag's commit hash is quoted in the paper." |

## Part D. Checked and consistent (no change needed)

| Setting | prereg.md | `src/config.py` / code |
|---|---|---|
| Band-pass 1–45 Hz, FIR firwin | §5.3 | `L_FREQ, H_FREQ`; `preprocess.prepare` |
| Epochs 4 s, 50% overlap | §5.4 | `EPOCH_SEC`, `EPOCH_OVERLAP` |
| Rejection: flags, robust z > 3 on log-variance at O1/O2 | §5.5 | `REJECT_ROBUST_Z`; `accepted_epochs` |
| Usable: ≥ 60 s clean, O1/O2 not flat (SD ≥ 1 µV) | §4.1 | `MIN_CLEAN_SEC`; `_process_one` |
| Adult age groups, "21" → "21–24", midpoints 19 … 87 | §4.1, §6 | `ADULT_AGE_GROUPS`, `AGE_GROUP_FIXES`, `AGE_MIDPOINTS` |
| Fit 2–40 Hz, fixed mode, widths 1–8 Hz, ≤ 6 peaks, min height 0.1, threshold 2 SD | §6 | `FIT_RANGE` … `PEAK_THRESHOLD` |
| Alpha band 7–14 Hz (both ends included); tallest peak gives IAF, power, width | §6 | `ALPHA_BAND`; `features` |
| Reactivity: IAF ± 2 Hz, eyes-closed IAF, 10.5 Hz fallback, separate fits | §6 | `REACTIVITY_HALF_WIDTH`; `process_participant` |
| R² floor 0.90 for H3–H5 only | §4.5 | `R2_FLOOR`; `models.load`, `h3_h4_h5` |
| Bounds: OR 0.80–1.25; ±0.10 SD per decade; bar 0.80 | §3 | `EQUIV_OR_BOUNDS`, `EQUIV_STD_SLOPE`, `PRESENCE_BAR` |
| Researcher groups < 10 people → "other" | §6 | `MIN_CLUSTER_SIZE` |
| Grid 3 × 3 × 2 × 6 × 3 = 324 | §8.1 | `GRID` (the region name `best_channel` was renamed `any_posterior` to match the code) |
| H1 exact binomial vs 0.80 and Wilson CI; HC3 errors; TOST with 90% CI; 11-test Holm family; V1 outside the family | §3, §7 | `models.py` |
| Leave-one-researcher-out; raw 7–12 Hz peak; κ; 256 Hz sensitivity | §8, §5.2 | `robustness.py` |

Tested on simulated data: 15 fast tests and 1 end-to-end test pass (`tests/test_pipeline.py`). The guard was not changed; every `main()` still refuses to run (checked for all five scripts and for `run_all.sh`).

## Part E. Code changes I made that touch pre-registered behaviour (please confirm each)

1. A failed specparam fit counts as "no peak" everywhere (before: counted as absent in H1 but as *present* in the H2 model, by accident of how missing values were converted).
2. `supported` now requires the raw rule **and** Holm-adjusted p < .05 (C1). The raw decision is kept in `supported_raw`.
3. A confirmatory model that cannot be fitted enters the Holm family with p = 1 (C2).
4. Firth logistic rows are added as sensitivity output (C2). They are not in the Holm family.
5. A factor with a single level in the model sample is dropped from that model (otherwise the model cannot be fitted).
6. In the specification curve, the "no R² floor" versions keep failed fits as "no peak", as in H1.
7. Firmware counter channels are no longer treated as electrodes (B1).
8. `PRESENCE_MIN_FITTED_HEIGHT` exists and is `None` (A1): no behaviour change until you set it.
9. The null calibration reports the drafted method and a time-domain method side by side (B12).

