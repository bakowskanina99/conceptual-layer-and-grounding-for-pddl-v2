# Experiment Data — Reference Labels and Provenance

`reference_labels.json` is the ground-truth/reference file used throughout Section 8's
accuracy figures: one entry per object (`obj_001`–`obj_032`), each carrying an
`object_id`, an `image_file` name, a `source`, a `reference_type` (validated against the
ontology's exact class names before the run — see
`../pipeline/logging_/reference_validation.py`), and `reference_properties`.

## Provenance — two distinct sources, not one

**23 grocery items (`obj_001`–`obj_023`), `"source": "open_food_facts"`.** Reference
type and properties (`veganAttributeMatch`, `nutriscoreMatch`, `calories`, etc.) are
taken directly from Open Food Facts' own product database via each item's barcode
(`off_barcode`), **not independently re-verified by the authors** — this is a stated
scope decision, discussed as a limitation in Section 10 of the paper. Open Food Facts
data is published under the **Open Database License (ODbL)** and its associated images
under **CC BY-SA**; any reuse of the OFF-derived fields in this file must retain
attribution to Open Food Facts (https://world.openfoodfacts.org) and its contributors,
per ODbL's attribution requirement. This repository does not redistribute Open Food
Facts' own database or images — only the specific per-item property values recorded
here, keyed by barcode, for reproducibility of this experiment's reference labels.

**9 non-grocery items (`obj_024`–`obj_032`), `"source": "own_photo"`.** These are the
authors' own photographs (household, clothing, and electronics items), not drawn from
Open Food Facts or any other third-party catalogue — labelled by direct visual
inspection by one author rather than external metadata. This distinction matters and was
corrected once already during paper editing (an earlier draft's phrasing conflated the
two provenance paths); `reference_labels.json`'s `source` field is the authoritative,
machine-checkable record of which of the two paths each object actually took.

## Fields

| Field | Meaning |
|---|---|
| `object_id` | `obj_001`–`obj_032`, matching the photo labels used throughout the pipeline and `results.jsonl` |
| `image_file` | Filename of the corresponding photograph, found in `images/` in this folder |
| `source` | `open_food_facts` or `own_photo` — see provenance section above |
| `off_barcode` | Open Food Facts barcode, present only for `open_food_facts`-sourced items |
| `reference_type` | Ground-truth type, validated against the ontology's exact class names |
| `reference_properties` | Ground-truth property values used to compute the accuracy figures in Section 8 |

## Images (`images/obj_001.jpg`–`images/obj_032.jpg`)

The actual 32 images shown to the vision-language agent are included in this folder,
under `images/`, one file per `object_id` as named in `reference_labels.json`. The two
provenance paths carry **different licensing** and neither is superseded by this
repository's own CC BY 4.0 license (see `../LICENSE`):

- **`images/obj_001.jpg`–`images/obj_023.jpg`** (`open_food_facts`) are Open Food
  Facts' own product photographs, downloaded as-served from their database (hence the
  small, capped resolution — OFF serves these at a maximum ~400px edge). They remain
  licensed under **CC BY-SA** by Open Food Facts and its contributors, independent of
  this repository's license. For the specific contributor attribution of any one image,
  look up its `off_barcode` (in `reference_labels.json`) at
  `https://world.openfoodfacts.org/product/<off_barcode>`.
- **`images/obj_024.jpg`–`images/obj_032.jpg`** (`own_photo`) are the authors' own
  phone photographs (hence the larger, uncropped resolution) and are covered by this
  repository's **CC BY 4.0** license like everything else here.

No image in either group carries EXIF, XMP, or IPTC metadata (checked directly on the
files before adding them to this repository).
