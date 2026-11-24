#!/bin/sh
# One command for the pre-registered analysis, to run AFTER the researcher has
# approved and committed preregistration/prereg.md (see notes/STATUS.md).
# Every step refuses to start while the pre-registration is a draft or uncommitted.
#
#   sh run_all.sh            # default: 2 worker processes, low priority
#   JOBS=1 sh run_all.sh     # on a busy machine
#
# Restartable: psd.py skips spectra that already exist. Logs go to results/run_logs/.
set -eu
cd "$(dirname "$0")"
PY=.venv/bin/python
JOBS="${JOBS:-2}"
mkdir -p results/run_logs
unset ALPHA_SIM_ROOT ALPHA_SIM_SMALL_GRID || true

step() {
    name="$1"; shift
    echo "== $name  ($(date '+%Y-%m-%d %H:%M:%S'))"
    if nice "$PY" -W ignore "$@" > "results/run_logs/$name.log" 2>&1; then
        tail -n 25 "results/run_logs/$name.log"
    else
        tail -n 25 "results/run_logs/$name.log"
        echo "== STOPPED: step $name failed (full log: results/run_logs/$name.log)"
        exit 1
    fi
}

step psd           src/psd.py --jobs "$JOBS"
step fit_specparam src/fit_specparam.py --jobs "$JOBS"
step models        src/models.py
step robustness    src/robustness.py
step figures       src/figures.py
echo "== done. Next: copy the numbers from results/confirmatory.csv and"
echo "   results/robustness_summary.csv into paper/notes.md, then into paper/main.tex."
