# Final DPO model and inference interface

The author has authorized publication of one final full-data DPO model, fixed training seed101, together with the generation interface. The checkpoint is still on the author server and is NOT downloadable from this repository yet. MODEL_RELEASE.json records the expected fingerprint and current status; no base-model substitute or fake checkpoint is provided.

The pending artifact will contain only final safetensors weights, model configuration, the adapted 32,115-token tokenizer, a model card, licence/notice and checksums. It will be distributed as a GitHub Release asset rather than committing large weights to Git history. Training data, training code, optimiser states, preference caches and original generation logs remain unpublished. The original PolyTAO Apache-2.0 licence will accompany the model; root MIT applies to the public interface code.

After obtaining the verified model artifact and extracting it locally, use a compatible environment with hardware-appropriate PyTorch plus requirements-inference.txt. Existing accepted DCU environments do not need to reinstall or replace their manufacturer PyTorch.

```sh
python scripts/generate.py --example-index 0 --validate-input-only
python scripts/generate.py --model-dir /path/to/PolyWeave-FS-DPO-full-seed101 --example-index 0 --attempts 20 --device auto --output results/example_0
python scripts/generate.py --model-dir /path/to/PolyWeave-FS-DPO-full-seed101 --fragment '[C&+0]-[C&+0]-[O&+0]-[C&+0]' --size 40:59 --attempts 20 --output results/custom_query
```

The input-only check does not load weights or generate candidates. The example-index mode uses only the published condition, not its target. Prompt serialization and sampling follow the original task: max256 input/target tokens, temperature1.0, top-p0.95, top-k0, independent per-candidate RNG and fixed decode seed20261016 by default. Unknown or lossy tokenizer encodings are rejected.

Outputs are local attempts.jsonl (all raw attempts, including failures and duplicates), qualified_unique.csv and summary.json. Computational checks do not certify synthesis or material properties. Full-reference novelty is not computed, since the complete training/PI1M reference sets are not public. A single released seed does not represent the paper's five-seed average. Identical outputs across hardware or library versions are not guaranteed.

Current validation: interface preparation and engineering checks only, pending receipt and validation of the actual trained checkpoint.
