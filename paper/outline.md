# Paper outline

This is the skeleton for `paper/main.tex`. Per CLAUDE.md, Claude drafts the text and the researcher edits and approves it. Each bullet says what a part must do and where its numbers come from. Target: IMRaD, about 5,000 words, six figures; bioRxiv preprint, then *eNeuro* (alternatives: *Royal Society Open Science*, *PLOS ONE*; student route: *Journal of Emerging Investigators* with your mentor as last author).

## Title (draft options; pick or write your own)
- Is alpha really missing? Spectral parameterization of resting EEG in adults from India and Tanzania
- Alpha rhythms in field EEG from India and Tanzania: presence, ageing and data quality after modelling the 1/f background

## Abstract (≈250 words)
- One sentence each on: the claim being tested, why 1/f matters, the data, the method, the H1 rate per site, the H2 result, the age results, the one-line meaning.
- Numbers from `results/confirmatory.csv`.

## 1. Introduction (≈800 words), CARS structure
1. **Territory:** alpha is described as universal; IAF slows and the 1/f exponent flattens with age (Klimesch 1999; Voytek et al. 2015; Cesnaite et al. 2023).
2. **Niche:**
   - the 2017 preprint reported weak or undetected alpha in less "modern" Indian adults;
   - its method never modelled the 1/f background;
   - in European samples, age effects on alpha *power* largely vanish once 1/f is removed (Merkin et al. 2023; Tröndle et al. 2023);
   - almost all normative EEG is from WEIRD samples.
3. **Occupy:**
   - ds007358 (Vianney et al. 2025): same headset model and protocol in two countries;
   - our pre-registered questions and hypotheses H1–H5, stated plainly;
   - say what Vianney et al. already showed (raw IAF by age) and what is new here.

## 2. Methods (≈1,600 words)
- **2.1 Data and participants:**
  - dataset DOI, consent and ethics of the original study;
  - inclusion rules (`prereg.md` §4);
  - the flow numbers (Figure 1, `results/qc_summary.csv`).
- **2.2 Pre-registration:** link and commit hash; list any amendments.
- **2.3 Preprocessing and data quality:** `prereg.md` §5; explain the quality composite in one sentence.
- **2.4 Spectra and spectral parameterization:**
  - `prereg.md` §6;
  - one sentence on why specparam is used (Donoghue et al. 2020);
  - the settings table.
- **2.5 Statistics:**
  - `prereg.md` §7;
  - equivalence tests (Lakens 2017) and Holm correction.
- **2.6 Robustness:** `prereg.md` §8 (specification curve: Simonsohn et al. 2020).
- **2.7 Software and data availability:** versions from `requirements.txt`.

## 3. Results (≈1,400 words), in this order
1. Sample, exclusions by site, and quality (Figure 1; Table 1 = demographics and quality by site).
2. **H1:** presence rate per site with CI; the threshold curve (Figure 3).
3. **H2:** quality and income vs missing peaks (Figure 4).
4. **H3–H5:** age effects (Figure 5; Table 2 = model coefficients).
5. **V1:** reactivity.
6. **Robustness:**
   - the specification curve (Figure 6), leave-one-researcher-out, the raw peak-pick comparison, second-detector κ, null false-positive rate;
   - from `results/robustness_summary.csv`.
7. Descriptive between-site comparison, ages 18–64, labelled exploratory.

Report every confirmatory test, supported or not. Use "supported / not supported by the pre-registered rule", not "proves".

## 4. Discussion (≈1,100 words)
1. What the presence rate means for the 2017 claim. If weak alpha remains, say what quality explains and what it does not.
2. The ageing results versus the European studies.
3. **Why site differences are not population traits:** montage, operators, setting, season, age mix (CLAUDE.md framing rule).
4. **Limitations:**
   - consumer headset at 128 Hz;
   - montage mix;
   - age bins only;
   - undocumented selection of the 2,000;
   - the researcher-prefix assumption;
   - alpha power and IAF are only defined when a peak exists;
   - cross-sectional design.
5. What field EEG studies should do next.

## Required statements
- **Data availability:**
  - ds007358 (CC0, doi:10.18112/openneuro.ds007358.v1.0.0);
  - derived tables and code on Zenodo (DOI to add).
- **Ethics:**
  - secondary analysis of de-identified open data;
  - the original approvals are reported in Vianney et al. (2025).
- **Author contributions (CRediT):** list your roles and your mentor's.
- **Conflicts of interest:** none (check with your mentor).
- **Funding:** none (or state any).
- **AI-use statement:**
  - say which AI tools helped with the literature search, citation checking and analysis code;
  - placeholder `[AI-USE STATEMENT — TBD]` until the researcher writes it; it must describe the AI drafting of code and text truthfully.

## Figures
1. Participant flow by site
2. Example spectra with fits
3. Presence vs peak threshold, with benchmarks
4. Odds ratios for a missing peak
5. IAF, exponent and alpha power by age group
6. Specification curve

Files: `paper/figures/` (created by `src/figures.py`).
