# Reproducing the Experiment and the Paper

This guide covers three separable things: (1) setting up the environment and running the
pipeline end to end, (2) regenerating `results/results.jsonl` and every figure derived
from it, and (3) recompiling the paper itself and reproducing the character/page counts
reported during its editing.

## 1. Environment setup

**Python dependencies:** `owlready2` (OWL reasoning via HermiT), `rdflib` (Turtle
parsing/RDF graph construction), `pyshacl` (SHACL validation), `requests` (Ollama HTTP
client). No `requirements.txt` was maintained during the original project; install these
four packages plus their transitive dependencies with your package manager of choice.
Python 3.11+ is recommended (the original runs used 3.14).

**Ollama + model:** install Ollama and pull `qwen3-vl:8b`. The pipeline expects an Ollama
server reachable at `http://localhost:11434` (see `pipeline/config.py`). A GPU with at
least ~8GB VRAM is recommended for this model at the context window used here (12,288
tokens — see `pipeline/config.py`'s inline note on why 8192 was insufficient).

**Fast Downward:** clone the upstream [Fast Downward](https://www.fast-downward.org/)
repository and build it from source per its own documentation for your platform. This
repository does not vendor Fast Downward itself. `pipeline/config.py`'s
`FAST_DOWNWARD_ENTRY_POINT` expects the built `fast-downward.py` driver at
`<project-root>/fast-downward/fast-downward.py`; adjust that constant if your build
lives elsewhere. The original build used CMake + Ninja + MinGW-w64 on Windows (no MSVC or
WSL available) if you hit the same constraint; on Linux/macOS, Fast Downward's own build
instructions should work without modification.

**OWL/SHACL ontology and data:** already in this repository —
`pipeline/ontology/{well_formed,weakened,shapes}.ttl`,
`experiment-data/reference_labels.json`, and the 32 source photographs themselves in
`experiment-data/images/` (see `experiment-data/README.md` for their provenance and
licensing) — if you want to re-run the vision-language agent calls rather than just
re-derive statistics from the existing log, these images are already named
`obj_001.jpg`–`obj_032.jpg` matching `reference_labels.json`'s `image_file`/`object_id`
fields.

## 2. Running the pipeline end to end

From the project root (the directory containing `pipeline/`, not this repository's own
root — see the note at the end of this section):

```bash
python scripts/smoke_test.py     # small-scale sanity check first
python scripts/run_full.py       # the full 384-combination run (32 objects x 4 variants x 3 goals)
```

`run_full.py` calls `pipeline.orchestrate` for every (variant, goal) combination,
writing one row per object to `results/results.jsonl` incrementally (flushed after every
row — a crash partway through does not lose completed work; re-running simply continues
appending, so clear or rename any partial log before a clean re-run). Expect this to take
several hours depending on your GPU — 384 sequential vision-language calls at
`temperature=0` with a fixed seed, most Fast Downward invocations completing in well
under a second once objects are compiled.

**Regenerating the aggregate figures from an existing log**, without re-running the
model calls at all:

```bash
python pipeline/scripts/report_raw.py
```

This reads `results.jsonl` directly and reproduces every table in
`results/aggregate-tables.md` and `results/variant-D-ablation-full-results.md` — this is
the fastest way to verify a specific reported number without waiting for a full re-run.

**Note on paths:** the scripts in `pipeline/scripts/` and `scripts/` assume the layout of
the original working project (a `runs/`, `experiment_data/`, and `fast-downward/`
directory as siblings of `pipeline/`), which differs slightly from this repository's own
top-level layout (results live in `results/`, not `runs/full_run/`). If you clone this
repository to actually re-run the pipeline rather than only read the code, either adjust
`pipeline/config.py`'s path constants to match this repository's layout, or reconstruct
the original sibling-directory layout locally.

## 3. Recompiling the paper and reproducing character/page counts

The paper (`paper.tex`, not included in this repository — see the top-level README) was
compiled with a standard MiKTeX/TeX Live distribution:

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

(Two `pdflatex` passes after `bibtex` to resolve cross-references and citations; a third
initial pass before `bibtex` so the `.aux` file exists for it to read.)

**Character count**, as measured throughout the paper's editing to track ICAART's
submission character limit (10,000–50,000 characters excluding whitespace, per ICAART's
own submission instructions):

```python
import pymupdf, re
doc = pymupdf.open("paper.pdf")
text = "".join(page.get_text() for page in doc)
no_whitespace = re.sub(r"\s+", "", text)
print(len(no_whitespace))
```

Cross-checked against `pdftotext -layout paper.pdf - | python3 -c "import sys,re; print(len(re.sub(r'\s+','',sys.stdin.read())))"` — both methods agreed throughout editing to within a few characters. Plain `pdftotext` without `-layout` diverges by roughly 0.5–1% due to column-reflow handling and should not be used for this measurement.

**Page count** is simply `doc.page_count` (PyMuPDF) or the page count `pdflatex` reports
in its final "Output written on paper.pdf (N pages, ...)" line.
