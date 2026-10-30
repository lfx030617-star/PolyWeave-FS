# PolyWeave-FS · Public examples and final DPO model

PolyWeave-FS（链织）links polymer repeat units to fragment and size constraints. This partial public release provides selected source-attributed examples, structural-evaluation tools, an inference interface and one final full-data DPO checkpoint (fixed training seed 101).

| Public material | Scope |
|---|---|
| Structure examples | 300 unique structures: 100 primary examples each from PI1M, OMG and SMiPoly |
| Condition–target examples | 30 training-origin records: 5 F+B and 5 F+B+D per source |
| Paper endpoint summaries | 60 experiment/scale/method/seed rows for descriptive comparisons |
| Code | Streaming readers, frozen constraint evaluator, result summaries, verified model downloader and inference interface |
| Final model | [Full-data DPO seed101](https://github.com/lfx030617-star/PolyWeave-FS/releases/tag/model-dpo-full-seed101-v1.0.0), approximately 895 MB; configuration, adapted tokenizer and notices included |

The complete dataset, complete training tables, training pipelines, preference/reference caches, other checkpoints, formal test conditions, original generation records and manuscript drafts remain unpublished. See [PUBLIC_CONTENTS.json](PUBLIC_CONTENTS.json). Model weights are Release attachments, outside Git history.

## Quick start

Python 3.12 is recommended. Standard-library tools inspect examples and reproduce summary statistics:

```sh
python scripts/preview_data.py --limit 2
python scripts/summarize_results.py
python -m unittest discover -s tests -v
```

Download the final model with the standard-library downloader. It fetches seven pieces, verifies every piece, restores the original ZIP, checks its SHA256 and validates the extracted checkpoint:

```sh
python scripts/download_model.py
```

Install hardware-appropriate PyTorch and the pinned inference dependencies; preserve an existing accepted manufacturer DCU PyTorch build. Then run:

```sh
python -m pip install -r requirements-inference.txt
python scripts/generate.py --model-dir models/PolyWeave-FS-DPO-full-seed101 --example-index 0 --attempts 20 --output results/example_0
```

For chemical example checks alone, install requirements-evaluation.txt and run scripts/check_examples.py. The frozen evaluator uses RDKit 2026.03.5, two bare `*` ports, fragment SMARTS matching with chirality and optional heavy-atom bins. See [model usage](docs/MODEL_USAGE.md), [model validation](docs/MODEL_VALIDATION.json) and [data schema](docs/DATA_SCHEMA.md).

## Interpretation and scope

The 300 structures and 30 condition–target records are deterministic training-origin illustrations, not a representative performance benchmark or a formal test release. Their targets are existing records. A single released seed is not the paper's five-seed average. Full-reference novelty cannot be reconstructed from the small public examples. Generated candidates are not experimentally validated synthesis routes or material properties.

## Licensing and attribution

Author-owned public interface code is MIT licensed. The final model archive includes the original PolyTAO Apache-2.0 licence and modification notice. Dataset examples retain their source-specific notices and conditions; see [data/TERMS.md](data/TERMS.md) and licenses/. Root MIT does not override upstream model or data terms. Endpoint summary results use CC BY 4.0.

中文说明：[README_中文.md](README_中文.md).
