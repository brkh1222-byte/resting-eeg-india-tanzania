"""Refuse to compute spectra or outcomes before the pre-registration is committed.

CLAUDE.md: preregistration/prereg.md must be committed before any outcome
statistics are computed. Every script that touches spectra calls
require_prereg() first. It checks that prereg.md is tracked by git, has no
uncommitted changes, and is not marked DRAFT.
"""
import subprocess
import sys

from config import ROOT

PREREG = ROOT / "preregistration" / "prereg.md"


def require_prereg() -> str:
    rel = PREREG.relative_to(ROOT).as_posix()

    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(ROOT), *args],
                              capture_output=True, text=True).stdout.strip()

    tracked = git("ls-files", rel)
    dirty = git("status", "--porcelain", rel)
    text = PREREG.read_text(encoding="utf-8") if PREREG.exists() else ""
    problems = []
    if not tracked:
        problems.append("prereg.md is not committed")
    if dirty:
        problems.append("prereg.md has uncommitted changes")
    if "STATUS: DRAFT" in text:
        problems.append("prereg.md is still marked 'STATUS: DRAFT'")
    if problems:
        sys.exit("Pre-registration gate: " + "; ".join(problems)
                 + ". Review, finalise and commit preregistration/prereg.md first.")
    return git("log", "-1", "--format=%H %cI", "--", rel)
