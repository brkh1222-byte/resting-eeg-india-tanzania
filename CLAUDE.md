# CLAUDE.md

This is a research project by a 17-year-old student. It reanalyses open resting EEG from 1,000 Indian and 1,000 Tanzanian adults (OpenNeuro ds007358, CC0) with specparam, to test whether alpha is really "absent" in some populations and how alpha and the aperiodic exponent change with age. Read PROPOSAL.md first.

- **Stack:** Python with MNE, specparam/fooof, statsmodels, pandas and matplotlib. Laptop-scale; no GPU needed.
- **Pre-registration:** `preregistration/prereg.md` must be committed before any outcome statistics are computed. Never edit it after commit; add dated amendments.
- **Data:** EEG files under `data/` are git-ignored. Only derived feature tables go in `results/`.
- **Framing:** describe population differences as environment, recording context or data quality, never as innate or racial traits.
- **Integrity:** the student must understand and write the paper themselves. Explain methods when implementing them. Verify every citation.
