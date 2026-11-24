# Novelty check: aperiodic-adjusted alpha analysis of OpenNeuro ds007358

Search date: 2026-11-25. Web/API searches only. "Confirmed" means the record was opened through an API or page and the stated fact was read there. "Inferred" is marked as such.

## 1. Verdict

No published or posted work was found that applies specparam/FOOOF/IRASA or any other aperiodic-adjusted analysis to ds007358, to other Sapien Labs India/Tanzania EEG data, or to the 2017 "alpha absent" Tamil Nadu data. The result of the 2026-11-22 search still holds. Confidence: moderate to high. Reasons for confidence: five independent citation indexes agree on a very short list of works citing Vianney et al. 2025 (two commentaries, one news item, two dataset mirrors); full-text searches for "ds007358" in Europe PMC, OpenAlex and PubMed return zero; OpenNeuro lists no derivatives. Reasons it is not higher: Google Scholar, the bioRxiv site search, Semantic Scholar keyword search and GitHub code search could not be reached; the dataset has 78 downloads, so unpublished work by others may exist; the Sapien Labs group itself now reports aperiodic slopes in a different dataset (2026 medRxiv preprint), so they have the method in hand and could apply it to these data.

## 2. Overlap candidates

| Work | DOI / URL | What it does (from abstract or record) | Overlap |
|---|---|---|---|
| Subramaniyam, Brown, Gibbens, Forche, Dirks, Newson, Thiagarajan. "Altered EEG patterns co-vary with specific improvements in mind health at summer camp". medRxiv, 2026-09-13 | 10.64898/2026.09.09.26362570 (Europe PMC PPR1318326) | Pre-post study of 30 adolescents at a three-week summer camp. Abstract: "participants exhibited steeper aperiodic slopes, increased DFA scaling exponents, reduced entropy and Lempel-Ziv complexity, and decreased alpha and beta power". Cites the 2017 alpha preprint (OpenAlex). | None on data or question. Method-level only: shows Sapien Labs now computes aperiodic slope. |
| Thiagarajan, Vianney, Swaminathan, Newson, Parameshwaran, Subramaniyam. "Building scalable neuroimaging programs across diverse human environments". Nat Neurosci 29(4):767-771, 2026 | 10.1038/s41593-026-02215-1 (PMID 41703301) | Five-page piece by the dataset authors. No abstract in PubMed or Europe PMC; full text not read. | None confirmed. Content not verified beyond title; should be read in full before submission. |
| Parameshwaran et al. "Resting state EEG classifies developmental status in three-year-old children". Dev Cogn Neurosci, 2025 | 10.1016/j.dcn.2025.101575 (PMID 40479750) | 70 children aged 33-40 months, 14-channel portable EEG "in low-resource households"; supervised models on "spectral features and novel time-domain features". No mention of aperiodic modelling in the abstract. | None (children, different data, different question). |
| NEMAR mirror of the dataset (UC San Diego), 2026-07-10 and 2026-09-30 | 10.82901/nemar.on007358, 10.82901/nemar.on007358.v1.0.0; github.com/nemarDatasets/on007358 | Copy of ds007358 with NEMAR metadata. The page title was confirmed; no analysis was seen. | None (data mirror). |
| GitHub: anitaavdiu/env-cognitive-dataset-eval | commit e18e560 | Commit message: "Add ds007358 (India/Tanzania field EEG dataset) to the registry". Only the commit message was seen. | None (dataset registry entry). |
| GitHub: brkh1222-byte/resting-eeg-india-tanzania (updated 2026-11-21) | github.com/brkh1222-byte/resting-eeg-india-tanzania | Description: "Is alpha really missing? Periodic & aperiodic resting EEG across age and income in 2,000 adults from India and Tanzania (OpenNeuro ds007358)". | Direct by description. Inferred to be this project's own public repository (same folder name). Not opened. Confirm it is yours. |

No other candidate with partial or direct overlap was found.

## 3. Papers citing Vianney et al. 2025 (eNeuro, 10.1523/ENEURO.0006-25.2025, PMID 40691075; preprint 10.1101/2024.12.05.626951)

Counts: OpenAlex 5 citing records; Crossref is-referenced-by 2 (journal version), 1 (preprint); Semantic Scholar 2; OpenCitations 2 (journal) + 1 (preprint); Europe PMC 1; PubMed cited-in 1. Union of all lists:

1. Mushtaq F, Ibanez A. "Electroencephalography (EEG) and the Quest for an Inclusive and Global Neuroscience". Eur J Neurosci 2025;61(6):e70078. 10.1111/ejn.70078, PMID 40103341. Perspective arguing that EEG can deliver "truly inclusive and global neuroscience"; no data analysis described in the abstract. Cites the preprint version.
2. Naddaf M. "Budget brainwaves: low-cost system collects brain data outside the lab". Nature, 2025-07-21. 10.1038/d41586-025-02303-5. News item (type "other" in OpenAlex). Not opened.
3. Thiagarajan TC et al. "Building scalable neuroimaging programs across diverse human environments". Nat Neurosci 2026;29(4):767-771. 10.1038/s41593-026-02215-1, PMID 41703301. By the dataset authors; no abstract available; full text not read.
4. NEMAR dataset record 10.82901/nemar.on007358.v1.0.0 (2026-07-10). Mirror of ds007358.
5. NEMAR dataset record 10.82901/nemar.on007358 (2026-09-30). Mirror of ds007358.

Possible mention, not a formal citation in any index: "Pandora's Box", BJPsych Int 2025;22(4):145-146, 10.1192/bji.2025.10071, PMID 41953794. It was returned by a Europe PMC full-text search for the paper's title. It has no listed authors and was not opened; inferred to be a news column.

Works citing the dataset DOI (10.18112/openneuro.ds007358.v1.0.0): OpenAlex 0; DataCite citationCount 0.

Works citing the 2017 preprint (10.1101/125898), OpenAlex 6, Crossref 4: Carhart-Harris & Friston 2019 (10.1124/pr.118.017160); Newson & Thiagarajan 2019 (10.3389/fnhum.2018.00521); Ouyang et al. 2020 (10.1016/j.neuroimage.2019.116304); van der Vinne et al. 2021 listing as eLife 10.7554/eLife.60595; PLoS One 2021 10.1371/journal.pone.0255771; and the 2026 summer camp preprint above. None is a reanalysis of the 2017 data, judging by title.

## 4. Related work worth citing

- Parameshwaran D, Thiagarajan TC. "Modernization, wealth and the emergence of strong alpha oscillations in the human EEG". bioRxiv 2017 (v2 2019-07-01), 10.1101/125898. The claim under test. Abstract: "this feature is largely undetected in the EEG of adults without post-primary education and access to modern technologies". bioRxiv lists no published version.
- Parameshwaran D, Thiagarajan TC. "Dynamical Features of Human EEG Scale Systematically with Life Context". bioRxiv 2017, 10.1101/125906. Companion preprint (title only seen).
- Del Bianco T et al. "The importance of decomposing periodic and aperiodic EEG signals for assessment of brain function in a global context". Dev Psychobiol 2024, 10.1002/dev.22484, PMID 38528816. 72 South African children aged 4-12; compares canonical band power with periodic and aperiodic features in a low-resource setting.
- Hernandez H et al. "Brain health in diverse settings: How age, demographics and cognition shape brain function". NeuroImage 2024, 10.1016/j.neuroimage.2024.120636, PMID 38777219. Power spectrum and "aperiodic (1/f slope, knee, offset) metrics" in "a diverse sample from the global south and north populations" (n = 1298); "Older age, poorer cognition, and being male were associated with reduced alpha power".
- van Bueren NER et al. "Comparing aperiodic activity in consumer-grade and research-grade EEG: Reliability and association with mathematical ability". Behav Res Methods 2026, 10.3758/s13428-025-02905-x, PMID 41493531. Aperiodic activity from an EMOTIV EPOC X headset compared with BioSemi in 93 children. Relevant for the validity of aperiodic estimates from Emotiv hardware.
- Ouyang G et al. "Decomposing alpha and 1/f brain activities reveals their differential associations with cognitive processing speed". NeuroImage 2020, 10.1016/j.neuroimage.2019.116304. Cites the 2017 preprint (title only seen).
- Mushtaq & Ibanez 2025 (10.1111/ejn.70078) and Thiagarajan et al. 2026 (10.1038/s41593-026-02215-1) for context on global and field EEG.
- Aggarwal S, Ray S. "Slope of the power spectral density flattens at low frequencies (<150 Hz) with healthy aging..." Cereb Cortex Commun 2023, 10.1093/texcom/tgad011; and "Changes in Higuchi Fractal Dimension Across Age in Healthy Human EEG Are Anticorrelated With Changes in Oscillatory Power and 1/f Slope", Eur J Neurosci 2025, 10.1111/ejn.70193. Returned by the India + aperiodic query; titles only seen. Age and 1/f slope in adult EEG.
- Subramaniyam NP, Thiagarajan TC. "A novel method for estimating functional connectivity from EEG coherence potentials". Sci Rep 2025, 10.1038/s41598-025-94076-0. Other 2025 Sapien Labs EEG paper (title only seen).

## 5. Search log (all 2026-11-25)

| Source | Exact query | Hits | Relevant hits |
|---|---|---|---|
| PubMed esearch | `10.1523/ENEURO.0006-25.2025[doi]` | 1 | PMID 40691075 |
| PubMed elink | `pubmed_pubmed_citedin`, id 40691075 | 1 | 40103341 |
| PubMed | `ds007358` | 0 | - |
| PubMed | `(Thiagarajan TC[au]) AND 2025:2026[dp]` | 8 | 41703301, 40479750, 40691075; the rest are not EEG |
| PubMed | `(Parameshwaran D[au]) AND 2025:2026[dp]` | 4 | same as above |
| PubMed | `(Newson JJ[au]) AND 2025:2026[dp]` | 8 | same as above |
| PubMed | `(Vianney JM[au]) AND 2025:2026[dp]` | 7 | 40691075 only; others toxicology/HIV |
| PubMed | `(Swaminathan S[au]) AND (EEG OR electroencephalography) AND 2025:2026[dp]` | 2 | 40691075 only |
| PubMed | `"Sapien Labs" AND (EEG OR electroencephalography)` | 8 | 40691075, 40479750, 40155425; older items |
| PubMed | `(aperiodic OR specparam OR FOOOF OR IRASA) AND (EEG) AND (India OR Tanzania)` | 15 | none on Sapien data; Aggarwal & Ray 2023, 2025 as related |
| PubMed | `(aperiodic OR specparam OR FOOOF OR "1/f") AND EEG AND (Africa OR "low-income" OR "low- and middle-income" OR LMIC OR rural OR "non-WEIRD")` | 4 | 38528816 |
| PubMed | `(alpha[ti] AND (absent OR absence OR presence)) AND EEG AND (India OR Tanzania OR Africa OR rural)` | 4 | none |
| PubMed | `"Human Brain Diversity Project"` | 942 | not usable (phrase not matched as a phrase) |
| PubMed | `(Emotiv) AND (aperiodic OR specparam OR FOOOF)` | 2 | 41493531 |
| Europe PMC | `DOI:10.1523/ENEURO.0006-25.2025` | 1 | 40691075 |
| Europe PMC citations | `MED/40691075/citations` | 1 | 40103341 |
| Europe PMC citations | `PPR/PPR951827/citations` | 0 | - |
| Europe PMC | `"ds007358"` | 0 (first try failed, retry OK) | - |
| Europe PMC | `"openneuro.ds007358"` | 0 | - |
| Europe PMC | `"Sapien Labs" AND (aperiodic OR specparam OR FOOOF OR IRASA OR "1/f") AND EEG AND FIRST_PDATE:[2025-01-01 TO 2026-12-31]` | 0 | - |
| Europe PMC | `("Vianney" AND "Tanzania" AND "India" AND EEG AND (aperiodic OR specparam OR FOOOF OR IRASA)) AND FIRST_PDATE:[2025-06-01 TO 2026-12-31]` | 0 | - |
| Europe PMC | `"EEG data quality in large-scale field studies"` | 3 | paper, preprint, "Pandora's Box" |
| Europe PMC | `"Modernization, wealth and the emergence of strong alpha"` | 1 | the preprint itself |
| Europe PMC | `AUTH:"Thiagarajan TC" AND FIRST_PDATE:[2025-01-01 TO 2026-12-31]` | 9 | adds preprint 10.64898/2026.09.09.26362570 |
| Europe PMC | `AUTH:"Parameshwaran D" AND FIRST_PDATE:[2025-01-01 TO 2026-12-31]` | 4 | as PubMed |
| Europe PMC | `(TITLE_ABS:(aperiodic OR specparam OR FOOOF OR "spectral parameterization") AND TITLE_ABS:(EEG) AND TITLE_ABS:(Tanzania OR India OR "sub-Saharan" OR "low-income" OR "middle-income" OR LMIC OR "non-WEIRD" OR "global south" OR rural)) AND FIRST_PDATE:[2023-01-01 TO 2026-12-31]` | 2 | 38777219 |
| Europe PMC | `TITLE_ABS:("alpha" AND (absent OR absence OR "no alpha" OR "lack of alpha" OR "alpha peak")) AND TITLE_ABS:(EEG) AND TITLE_ABS:(Tanzania OR India OR Africa OR rural OR "low-income" OR "non-WEIRD" OR modernization OR "pre-modern")` | hit count lost (only the tail of the list was captured) | the two 2017 preprints; no new overlap in the part seen |
| Europe PMC | `"Human Brain Diversity Project" AND EEG` | 0 | - |
| Europe PMC | `"Emotiv" AND "Tanzania" AND EEG AND FIRST_PDATE:[2025-01-01 TO 2026-12-31]` | 1 | 40691075 |
| Europe PMC | `SRC:PPR AND (aperiodic OR specparam OR FOOOF OR IRASA) AND EEG AND Tanzania AND FIRST_PDATE:[2025-06-01 TO 2026-12-31]` | 0 | - |
| Europe PMC | `SRC:PPR AND "Sapien Labs" AND EEG AND FIRST_PDATE:[2025-06-01 TO 2026-12-31]` | 0 | - |
| Europe PMC | `(REF:"Vianney" AND REF:"EEG Data Quality") AND FIRST_PDATE:[2025-01-01 TO 2026-12-31]` | 1 | 40103341 |
| OpenAlex | `works/doi:10.1523/ENEURO.0006-25.2025` | cited_by_count 3 | W4412537799 |
| OpenAlex | `filter=cites:W4412537799` | 5 | section 3 |
| OpenAlex | `works/doi:10.18112/openneuro.ds007358.v1.0.0`; `filter=cites:W7127585896` | cited_by 0; 0 | - |
| OpenAlex | `filter=cites:W2606742314` (2017 preprint) | 6 | section 3 |
| OpenAlex | `filter=fulltext.search:ds007358`; `filter=default.search:ds007358` | 0; 0 | - |
| OpenAlex | `filter=fulltext.search:"Sapien Labs" aperiodic EEG,from_publication_date:2025-01-01` | 1 | Vianney et al. only |
| OpenAlex | `filter=title_and_abstract.search:(aperiodic OR specparam OR FOOOF) AND EEG AND (Tanzania OR India OR "low-income" OR "middle-income" OR "non-WEIRD" OR "Global South" OR Africa),from_publication_date:2024-01-01` | 6 | Del Bianco 2024, Hernandez 2024 |
| OpenAlex | `filter=title_and_abstract.search:EEG AND Tanzania,from_publication_date:2025-01-01` | 9 | dataset, 2 NEMAR mirrors, Vianney, Nature news, Nat Neurosci |
| OpenAlex | `filter=title_and_abstract.search:"alpha" AND EEG AND (Hadza OR Hadzabe OR "hunter-gatherer" OR "pre-modern" OR modernization)` | 8 | the two 2017 preprints only |
| OpenAlex | `filter=fulltext.search:"EEG Data Quality in Large-Scale Field Studies in India and Tanzania",from_publication_date:2025-01-01` | 2 | Vianney, Mushtaq & Ibanez |
| Semantic Scholar | `paper/DOI:10.1523/ENEURO.0006-25.2025/citations` | 2 | Nat Neurosci 2026, EJN 2025 |
| Semantic Scholar | `paper/DOI:10.1101/125898/citations` | 5 | section 3 |
| Semantic Scholar | keyword search: `ds007358`; `aperiodic alpha EEG India Tanzania`; `Sapien Labs EEG alpha aperiodic`; `alpha oscillation absent aperiodic low-income field EEG` | HTTP 429 on all | not reached |
| OpenCitations | `citations/doi:10.1523/ENEURO.0006-25.2025`; `.../doi:10.1101/2024.12.05.626951` | 2; 1 | section 3 |
| Crossref | `works/10.1523/ENEURO.0006-25.2025`; `works/10.1101/2024.12.05.626951`; `works/10.1101/125898` | is-referenced-by 2; 1; 4 | - |
| Crossref | `query.bibliographic=aperiodic alpha EEG India Tanzania Sapien Labs`, from 2025-06-01, top 8 | 128,806 (loose match) | none in top 8 |
| Crossref | `query.bibliographic=ds007358 EEG`, from 2025-06-01, top 8 | 13,896 (loose match) | none in top 8 |
| Crossref | `query.bibliographic=alpha peak absent aperiodic specparam field EEG low-income`, from 2025-06-01, top 8 | 291,085 (loose match) | none in top 8 |
| Crossref Event Data | `events?obj-id=10.1523/ENEURO.0006-25.2025` | timed out twice | not reached |
| bioRxiv API | `details/biorxiv/10.1101/125898`; `pubs/biorxiv/10.1101/2024.12.05.626951` | 2 versions, no published DOI; published as the eNeuro paper | - |
| OpenNeuro GraphQL | `dataset(id:"ds007358")` | 1 | one snapshot (1.0.0, 2026-02-04); `derivatives: []`; only linked paper is Vianney et al.; 3,407 views, 78 downloads; CC0 |
| DataCite | `dois/10.18112/openneuro.ds007358.v1.0.0`; `query=ds007358`; `query=on007358` | citationCount 0; 0; 0 | - |
| GitHub | `search/repositories?q=ds007358` | 2 | OpenNeuroDatasets/ds007358; brkh1222-byte/resting-eeg-india-tanzania |
| GitHub | `search/issues?q=ds007358` | 2 | OpenNeuroOrg/openneuro#3705, neurobagel/annotate-openneuro#2 (infrastructure, by title) |
| GitHub | `search/commits?q=ds007358` | 2 | nemarDatasets/on007358; anitaavdiu/env-cognitive-dataset-eval |
| GitHub | `search/repositories?q="sapien labs" EEG` | 0 | - |
| GitHub | `search/code?q=ds007358` | 401 | not reached (needs login) |
| Zenodo | `ds007358` | 0 | - |
| Zenodo | `"Sapien Labs" EEG`; `Tanzania India EEG aperiodic`; `alpha EEG Tanzania specparam` | 8,460; 302,636; 67,043 (loose OR matching) | none in top 10 of each |
| Zenodo | `+Tanzania +EEG +(aperiodic specparam FOOOF alpha)` | 1 | not relevant |
| OSF preprints API | `filter[title]=ds007358`; `Sapien Labs`; `Tanzania EEG` | 0; 0; 0 | - (title filter only; PsyArXiv is also covered by Europe PMC preprint index) |
| NEMAR | `https://doi.org/10.82901/nemar.on007358` | page loads | dataset mirror |
| Google Scholar | `"ds007358"`; `"EEG Data Quality in Large-Scale Field Studies in India and Tanzania"` | HTTP 302 | not reached |
| bioRxiv site search | `https://www.biorxiv.org/search/ds007358` | HTTP 403 (bot check) | not reached |

## 6. Sources not reached / limits

- Google Scholar: both queries returned a redirect with no results page. Its "Cited by" list for Vianney et al. was not seen; Scholar often has citing theses and preprints that the other indexes miss.
- bioRxiv/medRxiv site search: blocked (403). Preprints were covered through Europe PMC and OpenAlex only; both index with a delay of days to weeks.
- Semantic Scholar keyword search: rate-limited (429) on every attempt. Its citation endpoints worked.
- GitHub code search: needs login. Only repository, issue and commit search were run. The GitHub MCP connector failed to connect in this session.
- Crossref Event Data: timed out twice.
- One Europe PMC query lost its hit count and the top of its result list; two late Europe PMC queries timed out (one returned 0 on retry, one was not completed: `"Vianney" AND "EEG data quality" AND "India and Tanzania"`).
- Not searched: conference abstract books (OHBM, SfN, FENS), thesis repositories (ProQuest, national repositories), the Sapien Labs website, Web of Science, Scopus.
- Not read in full: Thiagarajan et al. 2026 (Nat Neurosci), the Nature news item, "Pandora's Box", and the summer camp preprint beyond its abstract. Whether any of them comments on alpha absence or aperiodic correction in the India/Tanzania data is unknown.
- The GitHub repository brkh1222-byte/resting-eeg-india-tanzania was not opened; it is assumed, not confirmed, to belong to this project.
- Zenodo and Crossref free-text searches match loosely, so only the top results were checked.
