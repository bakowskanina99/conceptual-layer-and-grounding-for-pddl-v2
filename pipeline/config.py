"""Central constants for the pipeline. Single source of truth so no value is
hand-copied into more than one module. Every non-obvious value below traces to
a spec file or a recorded implementation decision -- see the inline comment on
each.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Ollama / model config -------------------------------------------------

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3-vl:8b"

# num_ctx: user's brief said >= 8192 (a smaller window caused silent failures
# in a prior pipeline). Found empirically 8192 is not enough HERE either --
# Ollama's own server log showed real context-overflow truncation events
# during this project's testing. Raised to 12288: the
# smallest safe increase given this GPU's VRAM (RTX 5060, 8GB) -- confirmed
# free VRAM headroom (~2.1 GiB after model load at 8192) comfortably fits the
# ~480 MiB additional KV-cache cost of 12288, whereas 16384 (~960 MiB more)
# would leave very little margin.
NUM_CTX = 12288

# Deterministic decoding: adopted for reproducibility, and specifically to make
# the Variant-B goal-invariance check meaningful (if decoding were stochastic,
# identical output across goals couldn't be attributed to the prompt being
# goal-invariant).
TEMPERATURE = 0.0
SEED = 42

# One object per Ollama call -- crash-resilience over batching.
OBJECTS_PER_CALL = 1

# --- Real-data goals (formal_artifacts_owl_pddl_v2.md, Part A3) ------------

# G4_real's R(G): calories <= 55 kcal/100g. NOT the symbolic walkthrough's
# illustrative 150 -- see formal_artifacts_owl_pddl_v2.md Part A3 for the full
# rationale (150 would admit every vegan item in the real
# sample, making G3_real/G4_real empirically indistinguishable; 55 sits inside
# the real vegan-item calorie range of 52-70 kcal/100g).
G4_REAL_CALORIE_THRESHOLD = 55

# --- Fast Downward -----------------------------------------------------------

FAST_DOWNWARD_ALIAS = "lama-first"  # spec's own example (experimental_design_v2.md)
# Built from source (CMake+Ninja+MinGW via winget -- no MSVC/WSL available).
# Verified against the repo's bundled gripper example.
FAST_DOWNWARD_ENTRY_POINT = PROJECT_ROOT / "fast-downward" / "fast-downward.py"

# --- Paths -------------------------------------------------------------------

SPEC_DIR = PROJECT_ROOT
DATA_DIR = PROJECT_ROOT / "experiment_data"
IMAGES_DIR = DATA_DIR / "images"
REFERENCE_LABELS_PATH = DATA_DIR / "reference_labels.json"

ONTOLOGY_DIR = PROJECT_ROOT / "pipeline" / "ontology"
WELL_FORMED_TTL = ONTOLOGY_DIR / "well_formed.ttl"
WEAKENED_TTL = ONTOLOGY_DIR / "weakened.ttl"
SHAPES_TTL = ONTOLOGY_DIR / "shapes.ttl"

RUNS_DIR = PROJECT_ROOT / "runs"

STORE_NS = "http://example.org/store#"
