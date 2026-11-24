# Citation check

Run on 2026-11-25. Web only. Sources: Crossref REST API (`api.crossref.org/works/{doi}` and
`query.bibliographic`), PubMed (NCBI E-utilities), Europe PMC REST, PMC full-text XML (NCBI efetch),
bioRxiv API and JATS XML, DataCite API, OpenNeuro GraphQL API and the public OpenNeuro S3 bucket,
OpenAlex (Holm 1979 only). No field in `paper/references.bib` was filled from memory.

## 1. Reference table

| key | verified against (date 2026-11-25) | status |
|---|---|---|
| vianney2025 | Crossref; Europe PMC (PMID 40691075, PMC12309446) | OK. 40 authors, eNeuro 12(7), article no. ENEURO.0006-25.2025 (no page range exists). Crossref links preprint 10.1101/2024.12.05.626951. |
| parameshwaran2017 | Crossref (posted-content); bioRxiv API; Europe PMC (PPR32081) | OK as a preprint. v1 2017-04-11, v2 2019-07-01. bioRxiv says "published: NA", so there is no journal version under this DOI. Full-text claims below were read from **v2 (2019)**. |
| parameshwaran2021 | Crossref; PubMed (PMID 33811239) | OK. Sci Rep 11(1), article 7439, 2021-04-02. Second author's given name is only "S." in both sources. |
| bhavnani2022 | Crossref; PubMed (PMID 35386581, PMC8978891) | OK. Front Hum Neurosci 16:802764. No issue number (journal has none). |
| li2022 | Crossref; PubMed (PMID 35398285) | OK. 39 authors, NeuroImage 256:119190. Crossref has accents on "César García"; PubMed strips them. |
| donoghue2020 | Crossref; PubMed (PMID 33230329, PMC8106550) | OK. Nat Neurosci 23(12):1655-1665. Online 2020-11-23, print Dec 2020. |
| voytek2015 | Crossref; PubMed (PMID 26400953, PMC4579381) | OK. J Neurosci 35(38):13257-13265. |
| corcoran2018 | Crossref; PubMed (PMID 29357113) | OK. Psychophysiology 55(7):e13064. Online 2018-01-21, print July 2018. |
| merkin2023 | Crossref; PubMed (PMID 36379095) | OK. Neurobiol Aging 121:78-87, Jan 2023 (Epub 2022-09-14). No issue number. |
| cesnaite2023 | Crossref; Europe PMC (PMID 36587708) | OK. NeuroImage 268:119810, Mar 2023 (Epub 2022-12-29). Crossref writes author 13 as "A．Veronica" with a full-width dot; normalised to "A. Veronica". |
| trondle2023 | Crossref; Europe PMC (PMID 36933455) | OK. Cortex 161:116-144, Apr 2023. |
| gerster2022 | Crossref; Europe PMC (PMID 35389160, PMC9588478) | OK. Neuroinformatics 20(4):991-1012. Online 2022-04-07, print Oct 2022. |
| simonsohn2020 | Crossref; Europe PMC (PMID 32719546) | OK. Nat Hum Behav 4(11):1208-1214. Online 2020-07-27. |
| lakens2017 | Crossref; Europe PMC (PMID 28736600, PMC5502906) | OK. SPPS 8(4):355-362. Crossref splits title/subtitle; full title is "Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses". |
| gramfort2013 | Crossref (incomplete); Europe PMC (PMID 24431986, PMC3872725) | DOI, title, journal, year, volume OK in Crossref. **Crossref lists only the first author and no article number**: authors 2-11 and article no. 267 are taken from PubMed/Europe PMC. |
| klimesch1999 | Crossref (bibliographic query, then by DOI); Europe PMC (PMID 10209231) | DOI found: 10.1016/S0165-0173(98)00056-3. Brain Res Rev 29(2-3):169-195, Apr 1999. |
| holm1979 | Crossref (two queries, no match); OpenAlex | **Not in Crossref; no registered DOI** (10.2307/4615733, reported by OpenAlex, returns 404 at doi.org and Crossref). Author Sture Holm, 1979, vol 6, pp 65-70 come from OpenAlex only. **Issue number unverified, left blank.** JSTOR page not fetched. |
| welch1967 | Crossref (bibliographic query) | DOI found: 10.1109/TAU.1967.1161901. IEEE Trans Audio Electroacoust 15(2):70-73, June 1967. Given name is only "P." in Crossref. Not in PubMed. |
| henrich2010 | Crossref (bibliographic query); Europe PMC (PMID 20550733) | DOI found: 10.1017/S0140525X0999152X. BBS 33(2-3):61-83 (PubMed adds "discussion 83-135"). |
| wilson1927 | Crossref (bibliographic query) | DOI found: 10.1080/01621459.1927.10502953. JASA 22(158):209-212, June 1927. Not in PubMed. |
| seabold2010 | Crossref (bibliographic query) | DOI found: 10.25080/Majora-92bf1922-011. Proc. 9th Python in Science Conf., pp 92-96, 2010. Not in PubMed. |
| virtanen2020 | Crossref (by DOI); Europe PMC (PMID 32015543, PMC7056644) | DOI found: 10.1038/s41592-019-0686-2. Nat Methods 17(3):261-272. The bibliographic query returned the *Author Correction* (10.1038/s41592-020-0772-5) first; that is not the article. Bib lists the 34 named authors + "SciPy 1.0 Contributors" (as PubMed); Crossref also lists the consortium members individually. |
| long2000 | Crossref (bibliographic query) | DOI found: 10.1080/00031305.2000.10474549. Am Stat 54(3):217-224, Aug 2000. Not in PubMed. |
| ostlund2022 | Crossref (bibliographic query); Europe PMC (PMID 35074579, PMC8792072) | DOI found: 10.1016/j.dcn.2022.101073. Dev Cogn Neurosci 54:101073, Apr 2022. |
| donoghue2022 | Crossref (bibliographic query, then by DOI); Europe PMC (PMID 34268825, PMC8761223) | DOI found: 10.1111/ejn.15361. EJN 55(11-12):3502-3527. **Year: online 2021-07-16, print issue June 2022**; Crossref "issued" says 2021, PubMed says 2022. Key and bib use 2022 (the volume year). |
| savitzky1964 | Crossref (bibliographic query) | DOI found: 10.1021/ac60214a047. Anal Chem 36(8):1627-1639, 1964-07-01. Not in PubMed. |
| openneuro_ds007358 | DataCite; OpenNeuro GraphQL; `dataset_description.json`, `CHANGES`, `participants.tsv` | OK. DOI registered 2026-02-04, publisher OpenNeuro, year 2026. DataCite has **no version and no rights field**; version 1.0.0, date 2026-02-04 and licence CC0 are from OpenNeuro. |

No DOI you supplied was wrong. All eleven missing DOIs were found except Holm 1979, which has none.

## 2. Claim checks

### a. Bhavnani 2022 — partly confirmed
- **1,199 adults: confirmed** (abstract): "977 children (Mean age = 38.8 months, SD = 0.9) and 1199 adults (Mean age = 27.0 years, SD = 4) provided resting-state data for this study."
- **Rural Haryana: confirmed** (Methods, Study Site and Ethics): "conducted in 120 villages in Rewari district in rural Haryana, India".
- **71.3%: confirmed, with a different denominator** (Table 3, "Presence of peak alpha (%)"): adults eyes closed 71.3, adults eyes open 57.1, children eyes closed 59.5, children eyes open 48.2. The adult eyes-closed sample size in that table is **N = 1194**, not 1199 (eyes open N = 1190).
- **How the peak was detected: not specified in detail.** Methods say PSD "using Welch method (Parameshwaran and Thiagarajan, 2019)" with no filtering "except centering using mean correction", and describe the peak only as "regular oscillatory activity in the Alpha band that appears as a peak above the background envelope of the PSD ... typically, though not always, observed at around ∼7–11 Hz in adults and 6–9 Hz in children". No threshold or algorithm is given in the text; the detail is deferred to the cited 2019 paper (not checked here). Peak frequency was "calculated individually for each channel" (Fig. 3 caption).
- Device: Emotiv EPOC, 14 channels, "maximum sampling rate of 128 Hz". Adult mean peak alpha 10.71 Hz (SD 3.96).
- Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC8978891/ (full text read via NCBI efetch XML).

### b. Corcoran 2018 — confirmed
- Abstract: "Applying the SGF technique to resting-state data from n = 63 healthy adults furnished 61 PAF and 62 CoG estimates."
- So 61/63 = 96.8% for peak alpha frequency (PAF) and 62/63 = 98.4% for centre of gravity (CoG). "About 97%" is the **PAF** estimator in the **empirical sample of 63 healthy adults**, using Savitzky-Golay-smoothed spectra. The percentages are my arithmetic; the abstract gives only the counts.
- Source: https://pubmed.ncbi.nlm.nih.gov/29357113/ (abstract only; full text not fetched).

### c. Parameshwaran & Thiagarajan 2017 — mostly confirmed (read from v2, 2019)
- **n = 402, Tamil Nadu: confirmed** (Methods): "Data was gathered from 402 people across 48 settlements in the State of Tamil Nadu, India". Introduction: "402 adults between the ages of 21 and 65".
- **Emotiv EPOC: confirmed** (Methods): "The EEG recordings were carried out using the Emotiv EPOC device." "14 channels" appears in Results ("any of the 14 channels recorded"). Three minutes, eyes closed.
- **"Largely undetected": confirmed** (abstract): "this feature is largely undetected in the EEG of adults without post-primary education and access to modern technologies."
- **Percentages** (Results):
  - "20% of the participants showed no evidence of an oscillation in any of the 14 channels recorded" (whole sample).
  - "Whereas a peak was always detected in at least one channel in ~97% of those in the modern group, it was entirely absent in ~20.17% of the pre-modern and transitioning groups."
  - "only 40% of the pre-modern and transitioning groups had Eα beyond the non-oscillatory residual alpha energy level (defined as 2SD from the mean, here 39) while this was so for 93.3% of the modern group".
- **Second-derivative method: confirmed** (Methods): "we first computed the discrete fourier transform of the autocorrelation using a 5 second Hann window to obtain the power spectral density (PSD). To then identify the peak frequency of the oscillation we computed the discrete approximation of the second order derivative of the PSD, and found the maximum between 7.5 and 15 Hz". The abstract defines the alpha range as 8-15 Hz.
- Note that the paper itself says the absence is not absolute: "our results suggest a very broad continuum rather than an absolute absence of the feature in some people."
- Source: https://www.biorxiv.org/content/10.1101/125898v2 (JATS XML `…/early/2019/07/01/125898.source.xml`). v1 full text was not compared; the abstract is identical in v1 and v2.

### d. Vianney 2025 — confirmed, with one conflict against the dataset
- **Headset: Emotiv FLEX 2 Gel** (Methods): "EEG was recorded with the wireless Emotiv FLEX 2 Gel headset using 16 out of 32 electrodes positioned according to the 10–20 international system and referenced to an ear clip sensor." Not EPOC X.
- **Sampling rate: 256 Hz** (Methods): "The internal sampling rate was 2,048 samples per second downsampled to 256 Hz." **This conflicts with the OpenNeuro files, which say 128 Hz (see h).**
- **Reference:** "an ear clip sensor" (side not stated).
- **Cohort size 7,933: confirmed** (abstract): "collecting data from a diverse sample of 7,933 participants ranging from Hadzabe hunter-gatherers to office workers." Quality analysis covers "the first 5,831 records" (India 3,413, Tanzania 2,418). The Discussion separately says "N = 5,500 and N = 6,200 for Tanzania and India" for the first 6 months.
- **Protocol: confirmed** (Methods): "eyes closed (EC) for 3 min and eyes open (EO) for 3 min", plus "a Raven's progressive matrix task (TASK)". In EO, participants were told "to look at their surroundings".
- **Alpha peak frequency by age: confirmed** (Results): "the peak alpha frequency declined with age from a mean of 9.5 ± 0.02 Hz to 8.6 ± 0.23 Hz from the age group 15–24 to 65–74 in India and from 9.6 ± 0.05 Hz to 9.0 ± 0.07 Hz in Tanzania (Fig. 5)". Also India age 13-15: 9.4 ± 0.07 Hz. Fig. 5: mean ± SEM, India N = 3,402, Tanzania N = 2,418.
- **Peak picking: confirmed 7-12 Hz** (Methods): "identifying the peak value within the alpha range (7–12 Hz) in the power spectral density, computed using the Pwelch function with a 2 s window and 50% overlap." This takes the maximum in the band; it does not test whether a peak exists.
- **Ethics and consent** (Methods): "All participants gave written informed consent and all procedures involving human subjects were approved by an ethical review board (India, IFMR Institutional Ethics Committee IFMR-IHEC/SL/0001/2023; National Ethics Committee Registry for Biomedical and Health Research, Department of Health Research; EC/NEW/INST/2023/3887; Tanzania, Kibong'oto Infectious Diseases Hospital–NM-AIST–Centre for Educational Development in health, Arusha–KNCHREC; KNCHREC00006/09/2023)." Thumbprint for those who could not write; script read aloud for those who could not read.
- **Field researchers:** "A total of 12 field researchers were recruited in each country", "EEG naive", trained 2 weeks, "93% met the standard and were retained", teams of two or three per device, plus a participant recruitment manager. Ages: "18+ in Tanzania and age 13+ in India". Sites: Tamil Nadu and the National Capital Region; Arusha and Manyara regions.
- **Subject IDs: the paper says nothing** about how participant IDs are built or about operator codes. It does say data quality was tracked "by the EEG device number". (My own observation from the dataset, not from the paper: participant IDs start with four letters, e.g. `sub-ADMU…`, `sub-ANAN…`, and many of these match the first two letters of the given and family names of field-researcher authors. This is an inference and is not documented anywhere I found.)
- **Hadzabe: one mention only**, in the abstract (quoted above). No sample size, location or method detail for Hadzabe participants anywhere in the body.
- Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12309446/ (full text read via NCBI efetch XML).

### e. Merkin 2023 and Tröndle 2023 — Merkin confirmed; Tröndle NOT confirmed as "absent"
- **Merkin 2023: confirmed** (abstract): "After correcting for aperiodic activity, peak alpha frequency remained slower in older adults; however, peak alpha power no longer differed statistically between age groups." Sample (abstract): "85 younger and 92 older adults". Ages are not in the published abstract; the bioRxiv preprint (10.1101/2021.08.31.458328, different title) gives younger mean 22.2 years (SD 3.9, range 18-35) and older mean 66.1 years (SD 8.2, range 50-86). **Ages are preprint-derived; published full text was not accessed.**
- **Tröndle 2023: "reduced" confirmed, "absent" not confirmed.** Abstract: "this general shift of the power spectrum leads to an overestimation of the true age effects in conventional analyses of total alpha power." But also: "However, also after accounting for these confounding factors, the sequential Bayesian updating analysis provided robust evidence that aging is associated with decreased aperiodic-adjusted alpha power." Sample (abstract): "a pilot and two additional independent samples (total N = 533)". Group ages are not in the abstract; the Stage-1 preprint (10.1101/2021.05.26.445765) describes young 18-35 / 20-35 and elderly roughly 59-80 across the three datasets, but those are planned or pre-existing sample descriptions and **the final per-group numbers were not verified**.
- Sources: https://pubmed.ncbi.nlm.nih.gov/36379095/ , https://pubmed.ncbi.nlm.nih.gov/36933455/

### f. Cesnaite 2023 — confirmed
- Abstract: "We used a large dataset (N = 1703, mean age 70)". "Critically, we did not detect a significant relationship between alpha power and age when controlling for the 1/f spectral slope, while the latter one showed age-related alterations." Also "strong evidence for an individual alpha peak frequency (IAF) decline in older age".
- **LIFE-Adult and age range are from the preprint only** (10.1101/2021.08.26.457768 v2): "a large elderly sample from a population-based study (LIFE-Adult)", and "a narrow age range between 60 and 80 years". The published abstract does not name the cohort or the range.
- Source: https://pubmed.ncbi.nlm.nih.gov/36587708/

### g. Voytek 2015 and Donoghue 2020 — confirmed
- **Voytek 2015** (abstract): "We observed, in both electrophysiological datasets, that aging is associated with a flatter (more noisy) 1/f power spectral density, even at rest". Samples (abstract): "intracranial electrocorticography from 15 participants over a 38 year age range (15-53 years) and scalp EEG data from healthy younger (20-30 years) and older (60-70 years) adults". EEG group sizes are not in the abstract; PMC full text could not be fetched through the API.
- **Donoghue 2020** (Results, PMC full text): "older adults had lower aperiodic offsets ... and lower (flatter) aperiodic exponents (younger=1.43 μV2/Hz, older=0.75 μV2/Hz; t28=7.19, p<0.0001; Cohen's d=2.63)". Sample: "younger (n=16; 20–30 years; 8 female) and older adults (n=14; 60–70 years; 7 female)". Also relevant: "though alpha power changes with age, the magnitude of this change is exaggerated by conflating age-related alpha changes with age-related aperiodic changes."
- Sources: https://pubmed.ncbi.nlm.nih.gov/26400953/ , https://pmc.ncbi.nlm.nih.gov/articles/PMC8106550/

### h. Dataset ds007358 v1.0.0 — confirmed, sampling rate differs from the paper
- Title: "A subset of large-scale EEG dataset (India + Tanzania)". 40 authors (same people as the eNeuro paper). Snapshot 1.0.0 created 2026-02-04; DataCite DOI registered 2026-02-04.
- **Participants: 2,000** (OpenNeuro summary; `participants.tsv` has 2,000 rows: India 1,000, Tanzania 1,000).
- **Tasks: eo, ec, pc** (OpenNeuro summary). Modality EEG, no sessions, 26,005 files, about 17.3 GB.
- **Licence: CC0** (`dataset_description.json`).
- **Sampling rate: 128 Hz** in all six `*_task-ec_eeg.json` sidecars I sampled (three India, three Tanzania), and in the eo and pc sidecars of one subject. Only 6 of 2,000 subjects were sampled. The eNeuro paper says 256 Hz.
- Other things seen in those six subjects, worth knowing before analysis:
  - Sidecars are sparse: Manufacturer, EEGReference and EEGPlacementScheme are "n/a"; PowerLineFrequency 50.
  - `EEGChannelCount` is 50-74 because Emotiv housekeeping channels (timestamps, counter, contact quality, battery, markers) are typed as EEG.
  - The scalp montage differs between subjects: 10, 12, 14 or 18 electrodes in the six sampled. One had frontal electrodes only and no occipital channel (`sub-ADMU025`: Fp1, AF3, F7, F5, FC3, FC2, F6, F8, AF4, Fp2). The two 14-channel India subjects had the Emotiv EPOC layout (AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4), not a 16-channel FLEX layout.
  - ec duration 181-238 s; pc 96 s in the one subject checked.
  - `participants.tsv` columns: participant_id, site, age, age_group, income_usd, mhq_score, sex. The first rows have `age` = n/a with only `age_group` filled. Age groups include "<18" (225 India rows), so the set is not all adults. `sex` has 35 n/a and 2 entries in Devanagari script.
- Sources: https://api.datacite.org/dois/10.18112/openneuro.ds007358.v1.0.0 , https://openneuro.org/datasets/ds007358/versions/1.0.0 , `https://s3.amazonaws.com/openneuro.org/ds007358/…`

## 3. Not reached or not verified
- **Europe PMC search** returned HTTP 503 repeatedly for refs 3-9 (parameshwaran2021, bhavnani2022, li2022, donoghue2020, voytek2015, corcoran2018, merkin2023). Those seven were checked against PubMed through NCBI E-utilities instead.
- **Holm 1979**: no Crossref record and no DOI. Volume and pages rest on OpenAlex alone; issue number not confirmed; JSTOR page not fetched.
- **Voytek 2015 full text**: PMC efetch returned no body text (publisher restriction). Abstract only.
- **Published full texts not accessed** for Corcoran 2018, Merkin 2023, Cesnaite 2023 and Tröndle 2023 (abstracts from PubMed; sample ages for Merkin and Cesnaite taken from bioRxiv preprints and flagged above).
- **Bhavnani 2022 peak-detection algorithm**: deferred by the paper to Parameshwaran & Thiagarajan 2019, "Characterizing Peaks in the EEG Power Spectrum", Biomed. Phys. Eng. Express (doi 10.1088/2057-1976/ab29d0 as listed in Bhavnani's reference list). That paper was not checked and is not in the bib.
- **Parameshwaran 2017 v1 full text** was not compared against v2.
- **Dataset sampling rate** was read from 6 of 2,000 subjects only; no EEG data file was opened.
- Not indexed in PubMed (Crossref only): welch1967, wilson1927, seabold2010, long2000, savitzky1964.
- Crossref's first listing of the S3 bucket returned nothing once (network); file paths were then obtained from the OpenNeuro GraphQL API.
