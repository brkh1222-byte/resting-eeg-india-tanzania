# Research Proposal

## Is Alpha Really Missing? Periodic and Aperiodic Resting EEG Across Age and Income in Adults from India and Tanzania Recorded with the Same Headset Model and Protocol

**Author:** Berkh (independent student researcher)
**Adult mentor / senior author:** [to be confirmed; needed for JEI and any OSF/PsyArXiv submission]
**Field:** Cognitive and population neuroscience (≈75% neuroscience / 25% anthropology)
**Planned duration:** 3–4 weeks (priority project, weeks 1–2)
**Status:** Proposal, Nov 2026

---

## 1. Summary

The **alpha rhythm** (≈8–12 Hz, strongest with eyes closed) is the most prominent signal in human resting EEG. It is usually described as universal. Yet a 2017 preprint reported that alpha is "largely undetected" in Indian adults without post-primary education or access to modern technologies (Parameshwaran & Thiagarajan, 2017, bioRxiv 10.1101/125898). In practice the claim is about **weak or undetected** alpha: in the least "modern" groups about 20% showed no peak in any channel and only about 40% had alpha energy above a noise threshold, and the authors describe a broad continuum. If true, a textbook "universal" rhythm would depend on lifestyle.

That claim rested on 402 adults in Tamil Nadu, recorded with a 14-channel Emotiv EPOC. Alpha was found with a second-derivative method that tries to lift peaks above the background, but the **1/f ("aperiodic") background** was never modelled and its exponent never estimated. Differences in that background, from age, electrode contact or noise, can make an alpha peak look weak or absent even when it is not.

A new open dataset (OpenNeuro **ds007358**, CC0, released Feb 2026) contains **1,000 participants from India and 1,000 from Tanzania** (225 of the Indian participants are under 18). All were recorded with the **same headset model and protocol** (eyes closed, eyes open, Raven's matrices task), but electrode montages differ: one layout in India, 136 in Tanzania. About 1,500 adults have usable occipital channels. This project separates periodic and aperiodic components with **specparam (FOOOF)** and tests, within each country:
1. how often an alpha peak is present once the background is modelled, and whether missing peaks track data quality or income;
2. how alpha frequency, alpha power above the background and the aperiodic exponent change with age;
3. whether income (India only) is associated with alpha once data quality is controlled.

## 2. Background

- **Alpha peak frequency** falls with age in adulthood. Alpha power is suppressed when the eyes open ("alpha reactivity").
- The **aperiodic exponent** (slope of the 1/f background) flattens with age and has been linked to the balance of neural excitation and inhibition (Voytek et al. 2015, *J Neurosci*; Donoghue et al. 2020, *Nat Neurosci*).
- Almost all normative EEG comes from Western, Educated, Industrialised, Rich, Democratic (WEIRD) samples. Previous cross-country EEG comparisons, such as HarMNqEEG (Li et al. 2022, *NeuroImage*), are confounded because each country used different hardware. ds007358 removes that confound.

## 3. Prior work and the gap

| Work | What it did | Gap |
|---|---|---|
| Vianney et al. 2025, *eNeuro*, doi:10.1523/ENEURO.0006-25.2025 | Source paper for the dataset. Data-quality focus; raw alpha peak frequency by age (India 9.5→8.6 Hz, Tanzania 9.6→9.0 Hz). **Partial overlap: we extend, not replace, this age result** | Simple 7–12 Hz peak pick; no 1/f separation; no presence test; no statistical modelling |
| Parameshwaran & Thiagarajan 2017, bioRxiv 10.1101/125898 | Weak or undetected alpha in less "modern" adults (Tamil Nadu, n = 402, Emotiv EPOC); never published in a journal | One country; second-derivative method, no fitted 1/f model; no exponent |
| Parameshwaran, Sathishkumar & Thiagarajan 2021, *Sci Rep*, doi:10.1038/s41598-021-85236-z | Same 402 people: complexity and spectral "energy" rise with income and stimulus exposure | One country; no 1/f fit |
| Bhavnani et al. 2022, *Front Hum Neurosci*, doi:10.3389/fnhum.2022.802764 | 1,199 rural adults in Haryana: alpha peak in 71.3% of eyes-closed recordings | No 1/f fit |
| HarMNqEEG, Li et al. 2022, *NeuroImage*, doi:10.1016/j.neuroimage.2022.119190 | Nine countries, cross-spectra | 12 different devices; only cross-spectra shared |

**Gap:** No published study or preprint has run spectral parameterization on ds007358 or any Sapien Labs India/Tanzania EEG, tested the "weak alpha" claim with a fitted 1/f model, or reported aperiodic-exponent age trends in Indian or East African adults. (Search of OpenNeuro, bioRxiv/medRxiv, Europe PMC, OpenAlex and Semantic Scholar citation lists, Nov 2026; full record in the research-plan doc.)

## 4. Hypotheses (to be pre-registered before analysis)

Full wording and decision rules: `preregistration/prereg.md`. All models are fitted within each country.

- **H1 (presence):** an eyes-closed occipital alpha peak (7–14 Hz, ≥ 0.1 log10 above the 1/f fit) is present in **> 80%** of usable recordings in each country (95% CI lower bound > 80%). The bar sits between 71% in rural Indian adults without 1/f modelling (Bhavnani et al., 2022) and 97% in Western adults (Corcoran et al., 2018).
- **H2 (measurement vs income):** missing peaks are predicted by data quality in each country (H2a). In India, income has no meaningful association once quality is controlled: odds ratio within 0.80–1.25 by equivalence test (H2b).
- **H3 (IAF and age):** individual alpha frequency falls with age in each country.
- **H4 (exponent and age):** the aperiodic exponent falls (flattens) with age in each country, replicating Western findings outside WEIRD samples.
- **H5 (alpha power and age):** alpha power *above the background* shows no meaningful age change (equivalence within ±0.10 SD per decade), as found in European samples (Merkin et al., 2023; Cesnaite et al., 2023).
- **V1 (validity check):** alpha is stronger eyes-closed than eyes-open in > 80% of participants.

Between-country differences are exploratory and descriptive only, because montage, operators, setting and age mix differ between sites.

## 5. Data

| Item | Details |
|---|---|
| Dataset | OpenNeuro **ds007358**, "A subset of large-scale EEG dataset (India + Tanzania)", v1.0.0 (2026-02-04), **CC0**, 17.3 GB, doi:10.18112/openneuro.ds007358.v1.0.0 |
| Participants | 1,000 India + 1,000 Tanzania. 225 Indian participants are under 18; Tanzania is 18+. Variables: `site`, `age_group` (bins only; `age` is n/a for everyone), `income_usd` (bins differ by country), `mhq_score`, `sex`. **No education variable** |
| Analysable adults | Adults with a known age group and both O1 and O2: India 694, Tanzania 832 (before quality control) |
| Income | India: 7 bins, missing for 22 analysable adults. Tanzania: 431 of 832 in "<1000", 349 missing, so income is analysed in India only |
| Recordings | ~3 min each: eyes closed (`ec`), eyes open (`eo`), Raven's matrices task (`pc`). EDF, **128 Hz** |
| Hardware | Emotiv FLEX 2 Gel per Vianney et al., ear-clip reference. **Montages differ:** India one 14-channel layout; Tanzania 136 layouts with 8–18 channels, 83 recordings with no posterior channel |
| Quality channels | Per-electrode Emotiv contact quality (CQ_) and signal quality (EQ_) in every file, used as data-quality covariates |
| Selection | How the 2,000 were drawn from the 7,933-person cohort is not documented; to ask the data owners |
| Note | Subject-ID prefixes appear to encode the field researcher (9 clusters in India, 13 in Tanzania); this is an assumption to confirm with the data owners |

Download: `openneuro-py` or `datalad`, or the AWS S3 bucket `s3://openneuro.org/ds007358`.

## 6. Method

Exact settings live in `src/config.py` and `preregistration/prereg.md`.

1. **Preprocessing (MNE-Python):**
   - Keep EEG channels; store the CQ_/EQ_ quality channels separately; drop timestamps, counters and markers.
   - Band-pass 1–45 Hz; cut **4 s epochs with 50% overlap** (0.25 Hz resolution for IAF).
   - Reject epochs with Emotiv interpolated/saturated samples or with outlier variance on O1/O2 (within-person robust z > 3).
   - Keep adults with O1 and O2 and ≥ 60 s of clean eyes-closed data.
   - Quality metrics: EQ/CQ at O1/O2, share of epochs kept, interpolated share, 50 Hz line-noise ratio, frontal blink rate. Quality composite = first principal component, within site.
2. **Spectra:** median-Welch PSD per channel; **primary region O1 + O2** (the only posterior pair present in nearly everyone).
3. **specparam:** one primary setting for everyone: fixed aperiodic mode, 2–40 Hz, peak widths 1–8 Hz, up to 6 peaks, minimum height 0.1 log10. No per-person mode selection, so exponents stay comparable. Extract alpha presence (peak in 7–14 Hz), IAF, alpha power above the 1/f fit, exponent, offset, theta peak, R² and error. A Savitzky-Golay detector adapted from restingIAF (Corcoran et al., 2018) is a second opinion on presence.
4. **Statistics (statsmodels):**
   - Within each site: logistic regression for a missing peak; OLS with HC3 errors for IAF, exponent and alpha power.
   - Covariates: age (bin midpoint, per decade), sex, quality composite, field researcher as a **fixed effect** (too few clusters for random effects), montage family in Tanzania; income rank in India.
   - Equivalence tests (TOST) for the "no meaningful effect" hypotheses; **Holm correction** across the 11 confirmatory tests.
5. **Robustness:** a 324-version **specification curve** (region × fit range × aperiodic mode × peak threshold × R² floor), leave-one-researcher-out, the raw 7–12 Hz peak pick that reproduces Vianney et al., second-detector agreement, and a null calibration of specparam's false-positive rate on simulated aperiodic-only spectra.
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
| specparam fails on noisy recordings | Fit-quality thresholds; sensitivity analysis; null calibration |
| Montages differ (136 in Tanzania) | O1 + O2 primary region; montage family as covariate; within-country analysis |
| Selection of the 2,000 undocumented | Ask the data owners; state as a limitation |
| ID prefix may not be the field researcher | Confirm with the data owners; fall back to site-level models |

## 11. Key references

Checked against Crossref and PubMed/Europe PMC on 2026-11-22 (details in the research-plan doc, section A6). Author lists of 20+ are shortened here; use full APA 7 form in the paper.

- Vianney, J.-M., Swaminathan, S., Newson, J. J., Parameshwaran, D., … Thiagarajan, T. C. (2025). EEG data quality in large-scale field studies in India and Tanzania. *eNeuro, 12*(7), ENEURO.0006-25.2025. https://doi.org/10.1523/ENEURO.0006-25.2025
- Parameshwaran, D., & Thiagarajan, T. C. (2017). *Modernization, wealth and the emergence of strong alpha oscillations in the human EEG* [Preprint]. bioRxiv. https://doi.org/10.1101/125898
- Parameshwaran, D., Sathishkumar, S., & Thiagarajan, T. C. (2021). The impact of socioeconomic and stimulus inequality on human brain physiology. *Scientific Reports, 11*, 7439. https://doi.org/10.1038/s41598-021-85236-z
- Bhavnani, S., Parameshwaran, D., Sharma, K. K., Mukherjee, D., Divan, G., Patel, V., & Thiagarajan, T. C. (2022). The acceptability, feasibility, and utility of portable electroencephalography to study resting-state neurophysiology in rural communities. *Frontiers in Human Neuroscience, 16*. https://doi.org/10.3389/fnhum.2022.802764
- Li, M., Wang, Y., Lopez-Naranjo, C., … Valdes-Sosa, P. A. (2022). Harmonized-Multinational qEEG norms (HarMNqEEG). *NeuroImage, 256*, 119190. https://doi.org/10.1016/j.neuroimage.2022.119190
- Donoghue, T., Haller, M., Peterson, E. J., … Voytek, B. (2020). Parameterizing neural power spectra into periodic and aperiodic components. *Nature Neuroscience, 23*(12), 1655–1665. https://doi.org/10.1038/s41593-020-00744-x
- Voytek, B., Kramer, M. A., Case, J., Lepage, K. Q., Tempesta, Z. R., Knight, R. T., & Gazzaley, A. (2015). Age-related changes in 1/f neural electrophysiological noise. *Journal of Neuroscience, 35*(38), 13257–13265. https://doi.org/10.1523/JNEUROSCI.2332-14.2015
- Corcoran, A. W., Alday, P. M., Schlesewsky, M., & Bornkessel-Schlesewsky, I. (2018). Toward a reliable, automated method of individual alpha frequency (IAF) quantification. *Psychophysiology, 55*(7), e13064. https://doi.org/10.1111/psyp.13064
- Merkin, A., et al. (2023). Do age-related differences in aperiodic neural activity explain differences in resting EEG alpha? *Neurobiology of Aging, 121*, 78–87. https://doi.org/10.1016/j.neurobiolaging.2022.09.003
- Cesnaite, E., et al. (2023). Alterations in rhythmic and non-rhythmic resting-state EEG activity and their link to cognition in older age. *NeuroImage, 268*, 119810. https://doi.org/10.1016/j.neuroimage.2022.119810
- Tröndle, M., et al. (2023). Decomposing age effects in EEG alpha power. *Cortex, 161*, 116–144. https://doi.org/10.1016/j.cortex.2023.02.002
- Gerster, M., et al. (2022). Separating neural oscillations from aperiodic 1/f activity: Challenges and recommendations. *Neuroinformatics, 20*(4), 991–1012. https://doi.org/10.1007/s12021-022-09581-8
- Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. *Nature Human Behaviour, 4*(11), 1208–1214. https://doi.org/10.1038/s41562-020-0912-z
- Lakens, D. (2017). Equivalence tests: A practical primer for t tests, correlations, and meta-analyses. *Social Psychological and Personality Science, 8*(4), 355–362. https://doi.org/10.1177/1948550617697177
- Gramfort, A., Luessi, M., Larson, E., Engemann, D. A., Strohmeier, D., Brodbeck, C., Goj, R., Jas, M., Brooks, T., Parkkonen, L., & Hämäläinen, M. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience, 7*, 267. https://doi.org/10.3389/fnins.2013.00267

> These references were compiled and checked with an AI research assistant. Open each one yourself before citing it in the paper.
