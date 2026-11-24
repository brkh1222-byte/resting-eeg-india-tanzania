# CLAUDE.md

This is a research project by an independent researcher. It reanalyses open resting EEG from 1,000 Indian and 1,000 Tanzanian adults (OpenNeuro ds007358, CC0) with specparam, to test whether alpha is really "absent" in some populations and how alpha and the aperiodic exponent change with age. Read PROPOSAL.md first.

- **Stack:** Python with MNE, specparam/fooof, statsmodels, pandas and matplotlib. Laptop-scale; no GPU needed.
- **Pre-registration:** `preregistration/prereg.md` must be committed before any outcome statistics are computed. Never edit it after commit; add dated amendments.
- **Data:** EEG files under `data/` are git-ignored. Only derived feature tables go in `results/`.
- **Framing:** describe population differences as environment, recording context or data quality, never as innate or racial traits.
- **Roles:** the researcher pilots; Claude runs the project and drafts the paper (`paper/main.tex`), and the researcher edits and approves it. The paper carries an AI-use disclosure. Authorship is undecided: keep the placeholders `[AUTHORS — TBD]` and `[AI-USE STATEMENT — TBD]` until the researcher fills them.
- **Integrity:** explain methods when implementing them. Verify every citation (Crossref/PubMed) and log every number with its source in `paper/notes.md`. Never compute, plot or inspect a real-data spectrum before the pre-registration is approved and committed by the researcher (`src/prereg_guard.py`).
- **Status log:** `notes/STATUS.md`.
