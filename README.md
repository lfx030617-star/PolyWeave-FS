# PolyWeave-FS · Public examples

**A partial public release of source-attributed polymer examples and structural-evaluation tools.** PolyWeave-FS（链织）links polymer structures to fragment (F) and size (S) constraints.

This repository intentionally publishes only a selected subset. It is **not** the complete dataset, training release or full experimental reproduction package. The remaining research materials are not uploaded to this repository. The final DPO model is separately authorized for publication; its weights are still awaiting export from the author server.

## Available here

| Public material | Scope |
|---|---|
| Structure examples | 300 unique structures: 100 primary examples each from PI1M, OMG and SMiPoly |
| Condition–target examples | 30 training-origin records: 5 F+B and 5 F+B+D per source |
| Paper endpoint summaries | 60 experiment/scale/method/seed rows supporting reported descriptive comparisons |
| Code | Streaming readers, selected frozen graph/constraint evaluator, example checks, mean/SD summaries and a checkpoint-verified inference interface |

Only retained training-origin structures are used for the examples; no formal test condition table is released. Examples are selected deterministically from frozen file order, not randomly, and are not a representative performance benchmark. The 30 targets are existing input–target records, not generated outputs.

## Quick start

Python 3.12 is recommended. To inspect data or recompute summary statistics, no additional packages are needed:

```sh
python scripts/preview_data.py --limit 2
python scripts/summarize_results.py
python -m unittest discover -s tests -v
```

For chemical evaluation, use a compatible RDKit environment:

```sh
python -m pip install -r requirements-evaluation.txt
python scripts/check_examples.py
```

The evaluator follows the frozen RDKit 2026.03.5 graph semantics. It checks parsing, connected structure, two degree-one bare `*` single-bond ports, task-domain elements, fragment SMARTS matching with chirality and optional size bins. The evaluator does not train a model. An additional inference-only interface is provided in `scripts/generate.py`; it requires the final model checkpoint, which is not downloadable yet. Full-reference novelty cannot be reconstructed from 300 examples; no full-library novelty claim is made by the example script.

## Not included

Full structures, complete training tables, preference pairs/reference caches, training pipelines, model weights (pending separate authorized release), formal test conditions, raw generation logs, local archives, private source maps and manuscript drafts are not included. Public samples and code cannot reproduce the entire training or all formal raw outputs. See [PUBLIC_CONTENTS.json](PUBLIC_CONTENTS.json) for exact scope.

## Licensing and attribution

Author-owned public code is MIT licensed. Dataset examples retain source-specific notices and conditions; see [data/TERMS.md](data/TERMS.md) and licenses/. Root MIT does not override upstream data terms. Endpoint summary results use CC BY 4.0. Computational constraint checks do not establish synthesizability or material properties.

中文说明：[README_中文.md](README_中文.md). Schema and usage: [docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md).

## Final DPO model status

The inference interface is available, while the actual checkpoint is awaiting author-server export. See [MODEL_RELEASE.json](MODEL_RELEASE.json) and [docs/MODEL_USAGE.md](docs/MODEL_USAGE.md). Training code and private generation-pool pipelines remain unpublished.
