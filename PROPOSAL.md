# Research Proposal

## Is Alpha Really Missing? Periodic and Aperiodic Resting EEG Across Age and Income in 2,000 Adults from India and Tanzania Recorded on Identical Hardware

**Author:** Berkh (independent student researcher)
**Adult mentor / senior author:** [to be confirmed; needed for JEI and any OSF/PsyArXiv submission]
**Field:** Cognitive and population neuroscience (≈75% neuroscience / 25% anthropology)
**Planned duration:** 3–4 weeks (priority project, weeks 1–2)
**Status:** Proposal, Nov 2026

---

## 1. Summary

The **alpha rhythm** (≈8–12 Hz, strongest with eyes closed) is the most prominent signal in human resting EEG. It is usually described as universal. Yet a research group has claimed that alpha is "largely undetected" in Indian adults without post-primary education or exposure to modern technology (Parameshwaran & Thiagarajan, bioRxiv 10.1101/125898). If that is true, a textbook "universal" brain rhythm would depend on lifestyle.

That claim rested on 402 participants from one country, on older hardware, using raw spectral power. Raw power mixes true oscillations with the broadband **1/f ("aperiodic") background**. Differences in that background, from age, hardware contact or noise, can make an alpha peak look absent even when it is not.

A new open dataset (OpenNeuro **ds007358**, CC0, released Feb 2026) contains **1,000 adults from India and 1,000 from Tanzania**. All were recorded with the **same headset and protocol** (eyes closed, eyes open, Raven's matrices task). This project separates periodic and aperiodic components with **specparam (FOOOF)** and tests:
1. whether alpha is present or absent once the background is modelled;
2. how alpha frequency, alpha power and the aperiodic exponent change with age in two countries;
3. whether income is associated with any of these within each country.

## 2. Background

- **Alpha peak frequency** falls with age in adulthood. Alpha power is suppressed when the eyes open ("alpha reactivity").
- The **aperiodic exponent** (slope of the 1/f background) flattens with age and has been linked to the balance of neural excitation and inhibition (Voytek et al. 2015, *J Neurosci*; Donoghue et al. 2020, *Nat Neurosci*).
- Almost all normative EEG comes from Western, Educated, Industrialised, Rich, Democratic (WEIRD) samples. Previous cross-country EEG comparisons, such as HarMNqEEG (Li et al. 2022, *NeuroImage*), are confounded because each country used different hardware. ds007358 removes that confound.

## 3. Prior work and the gap

| Work | What it did | Gap |
|---|---|---|
| Vianney et al. 2025, *eNeuro*, doi:10.1523/ENEURO.0006-25.2025 | Source paper for the dataset. Data-quality focus; one raw alpha-peak-by-age plot (India 9.5→8.6 Hz, Tanzania 9.6→9.0 Hz) | Simple 7–12 Hz peak pick; no 1/f separation; no statistical modelling |
| Parameshwaran & Thiagarajan, bioRxiv 10.1101/125898 | "Alpha largely undetected" in less-educated or low-technology adults (India, n = 402, Emotiv EPOC) | One country, older device, raw power |
| Parameshwaran & Thiagarajan 2021, *Sci Rep*, doi:10.1038/s41598-021-85236-z | EEG complexity vs income and stimulus exposure (India) | One country |
| HarMNqEEG, Li et al. 2022, *NeuroImage*, doi:10.1016/j.neuroimage.2022.119190 | Nine countries, cross-spectra | 12 different devices; only cross-spectra shared |

**Gap:** No study has reanalysed ds007358. No study has tested the "alpha absent" claim with periodic/aperiodic separation, across two countries, on identical hardware. (Literature search, Nov 2026.)

## 4. Hypotheses (to be pre-registered before analysis)

- **H1 (alpha presence):** after specparam modelling, a detectable alpha peak (8–13 Hz, eyes closed) will be present in a **large majority (>80%)** of usable recordings in *both* countries. This contradicts the "alpha absent" claim.
- **H2 (age):** alpha peak frequency will decline with age group in both countries. A site × age interaction will be tested, with no predicted direction.
- **H3 (aperiodic):** the aperiodic exponent will decrease (flatten) with age in both countries, replicating Western findings outside WEIRD samples.
- **H4 (income, exploratory):** within each country, income will show at most small associations with alpha presence or power once data quality is controlled.
- **H5 (reactivity):** alpha reactivity, defined as eyes-closed divided by eyes-open alpha power, will be > 1 in the large majority of participants in both countries.

## 5. Data

| Item | Details |
|---|---|
| Dataset | OpenNeuro **ds007358**, "A subset of large-scale EEG dataset (India + Tanzania)", v1.0.0 (2026-02-04), **CC0**, 17.3 GB |
| Participants | 1,000 India + 1,000 Tanzania. Variables: `site`, `age_group` (`age` mostly n/a), `income_usd` (bins), `mhq_score`, `sex` |
| Recordings | ~3 min each: eyes closed, eyes open, Raven's matrices task. EDF, **128 Hz** |
| Hardware | Emotiv FLEX 2 (16 channels used, ear-clip reference), the same in both countries |
| Note | Subject-ID prefixes appear to encode the field researcher or site, and will be used as a random effect |

Download: `openneuro-py` or `datalad`, or the AWS S3 bucket `s3://openneuro.org/ds007358`.

## 6. Method

1. **Preprocessing (MNE-Python):**
   - Drop non-EEG channels (COUNTER, INTERPOLATED, timestamps).
   - Filter 1–40 Hz and split into 2 s epochs.
   - Reject epochs by amplitude/variance thresholds (or autoreject) and mark bad channels.
   - Keep participants with ≥60 s of clean eyes-closed data.
   - Record data-quality metrics as covariates.
2. **Spectra:** Welch PSD per channel; average over posterior channels (O1, O2, P7, P8) and over all channels.
3. **specparam:** fit 1–40 Hz in "knee" and "fixed" modes; choose the mode by fit statistics. Extract per participant:
   - alpha peak present/absent;
   - individual alpha frequency (IAF);
   - alpha power above the aperiodic background;
   - aperiodic exponent and offset;
   - theta peak.

   Also report goodness of fit (R², error) for every fit.
4. **Statistics (statsmodels / pymer4):**
   - Model: `feature ~ age_group * site + sex + income_within_site + quality + (1 | field_researcher)`.
   - Logistic GLMM for alpha presence.
   - Report effect sizes with confidence intervals; correct multiple comparisons (FDR).
5. **Robustness:** different channel sets, frequency ranges, specparam settings, stricter quality thresholds, and a "raw peak-pick" comparison that reproduces Vianney et al.'s approach.
6. **Pre-registration:** commit `preregistration/prereg.md` (hypotheses, exclusions, models) to this public repo **before** computing any outcome statistics. The git timestamp on GitHub is the public record. (OSF requires users to be 18+; the adult mentor can mirror it there.)

**Compute:** laptop-scale (17 GB, CPU). No GPU needed.

## 7. Timeline

| Week | Tasks | Deliverable |
|---|---|---|
| 1 | Download; inspect participants.tsv and a sample of EDFs; write and commit the **pre-registration**; build the preprocessing pipeline | Pre-registration + clean epochs |
| 2 | PSDs, specparam on all participants, QC dashboard | Feature table (2,000 rows) |
| 3 | Mixed models, robustness, figures | Results |
| 4 | Write-up; mentor review; bioRxiv preprint | Preprint |

## 8. Ethics and framing

- The data are de-identified, CC0 and openly published; no new participants are involved.
- **Results will be framed as differences in environment, recording context and data quality, never as innate or "racial" traits of any population.** Country differences are confounded with field conditions, operators and age mix (India includes people under 18; Tanzania is 18+ only). This will be stated explicitly.

## 9. Venues

- **eNeuro:** the source dataset was published there; open access. Alternatives: **Royal Society Open Science** or **PLOS ONE**.
- **bioRxiv** preprint first, with the high school as affiliation.
- **Journal of Emerging Investigators** as a student alternative; needs an adult mentor as last author.

## 10. Risks

| Risk | Mitigation |
|---|---|
| 128 Hz and consumer hardware limit the analysis | Restrict to 1–40 Hz; report fit quality; treat findings as relative |
| Age is coarse (groups only) | Use ordinal age_group |
| Scoop by the data owners (Sapien Labs) | Pre-register and post the preprint quickly; cite them |
| specparam fails on noisy recordings | Fit-quality thresholds; sensitivity analysis |

## 11. Key references

- Vianney, J.-M. et al. (2025). *eNeuro*. doi:10.1523/ENEURO.0006-25.2025
- Parameshwaran, D. & Thiagarajan, T. C. bioRxiv doi:10.1101/125898
- Parameshwaran, D. & Thiagarajan, T. C. (2021). *Sci Rep*. doi:10.1038/s41598-021-85236-z
- Li, M. et al. (2022). HarMNqEEG. *NeuroImage*. doi:10.1016/j.neuroimage.2022.119190
- Donoghue, T. et al. (2020). Parameterizing neural power spectra. *Nat Neurosci* 23, 1655
- Voytek, B. et al. (2015). Age-related changes in 1/f neural electrophysiological noise. *J Neurosci* 35, 13257
- Gramfort, A. et al. (2013). MNE-Python. *Front Neurosci*

> ⚠️ These references were compiled by an AI research assistant. Verify every citation against the source before using it.
