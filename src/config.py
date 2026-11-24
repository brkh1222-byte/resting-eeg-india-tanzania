"""Central settings for the pipeline.

Every analysis choice that the pre-registration fixes lives here, so the
code and preregistration/prereg.md can be checked against each other line
by line. Do not change a PRIMARY value after the pre-registration commit;
add a dated amendment instead (see CLAUDE.md).
"""
from pathlib import Path

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ds007358"          # git-ignored raw data
DERIV = ROOT / "data" / "derivatives"      # git-ignored intermediate files
RESULTS = ROOT / "results"                 # derived tables only (committed)
FIGURES = ROOT / "paper" / "figures"

DATASET_ID = "ds007358"
DATASET_VERSION = "1.0.0"
S3_BASE = "https://s3.amazonaws.com/openneuro.org/ds007358"
TASKS = ("ec", "eo")                       # eyes closed, eyes open; Raven's task ("pc") not used

# ------------------------------------------------------- sample rules
ADULT_AGE_GROUPS = ["18-20", "21-24", "25-34", "35-44", "45-54",
                    "55-64", "65-74", "75-84", "85+"]
AGE_GROUP_FIXES = {"21": "21-24"}          # stray label in participants.tsv
SEX_FIXES = {"महिला": "F"}                  # Hindi for "female"
# Bin midpoints in years, used for linear age slopes.
AGE_MIDPOINTS = {"18-20": 19.0, "21-24": 22.5, "25-34": 29.5, "35-44": 39.5,
                 "45-54": 49.5, "55-64": 59.5, "65-74": 69.5, "75-84": 79.5,
                 "85+": 87.0}
MIN_CLUSTER_SIZE = 10                      # smaller researcher groups -> "other"

# --------------------------------------------------------- channels
ROI_PRIMARY = ["O1", "O2"]
ROI_POSTERIOR4 = ["O1", "O2", "P7", "P8"]
NON_EEG_PREFIXES = ("CQ_", "EQ_", "POW", "MOT", "PM_")
NON_EEG_NAMES = {
    "TIME_STAMP_s", "TIME_STAMP_ms", "OR_TIME_STAMP_s", "OR_TIME_STAMP_ms",
    "COUNTER", "INTERPOLATED", "HighBitFlex", "SaturationFlag", "RAW_CQ",
    "BATTERY", "BATTERY_PERCENT", "MarkerIndex", "MarkerType",
    "MarkerValueInt", "MARKER_HARDWARE",
}
FRONTAL_BLINK_CHANNELS = ["AF3", "AF4", "Fp1", "Fp2"]  # first two present are used

# ----------------------------------------------------- preprocessing
L_FREQ, H_FREQ = 1.0, 45.0
EPOCH_SEC = 4.0
EPOCH_OVERLAP = 0.5                        # 50% overlap
REJECT_ROBUST_Z = 3.0                      # epoch variance outlier rule
MIN_CLEAN_SEC = 60.0

# --------------------------------------------------------- spectra
WELCH_AVERAGE = "median"

# ------------------------------------------------------- specparam (PRIMARY)
FIT_RANGE = (2.0, 40.0)
APERIODIC_MODE = "fixed"
PEAK_WIDTH_LIMITS = (1.0, 8.0)
MAX_N_PEAKS = 6
MIN_PEAK_HEIGHT = 0.1                      # log10 power above the aperiodic fit
PEAK_THRESHOLD = 2.0                       # specparam default (SD units)
ALPHA_BAND = (7.0, 14.0)
THETA_BAND = (4.0, 7.0)
R2_FLOOR = 0.90
REACTIVITY_HALF_WIDTH = 2.0                # IAF +/- 2 Hz

# ------------------------------------------------- robustness grid
GRID = {
    "roi": ["O1O2", "posterior4", "best_channel"],
    "fit_range": [(2.0, 40.0), (1.0, 40.0), (3.0, 30.0)],
    "aperiodic_mode": ["fixed", "knee"],
    "min_peak_height": [0.05, 0.1, 0.15, 0.2, 0.25, 0.3],
    "r2_floor": [0.90, 0.80, 0.0],
}

# ------------------------------------------------- statistics
ALPHA_LEVEL = 0.05
EQUIV_OR_BOUNDS = (0.80, 1.25)             # H2 income, per SD of within-site rank
EQUIV_STD_SLOPE = 0.10                     # H5, SD of alpha power per decade
PRESENCE_BAR = 0.80                        # H1 and V1
