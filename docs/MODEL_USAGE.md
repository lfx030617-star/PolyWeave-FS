# Final DPO model and inference interface

[Download page](https://github.com/lfx030617-star/PolyWeave-FS/releases/tag/model-dpo-full-seed101-v1.0.0). The released artifact is the actual final full-data DPO checkpoint, fixed training seed101. It is not the base PolyTAO checkpoint, an ensemble or the paper's five-seed average. Seed101 was selected by index rather than performance.

## Download and verify

From the repository directory, Python's standard library is sufficient:

```sh
python scripts/download_model.py --output-dir models --workers 4
```

Seven Release pieces restore the unchanged original archive (894,848,074 bytes). The downloader checks each piece, the complete archive SHA256 and the model identity before making the extracted model available. Download workers control HTTP transfers, independently of inference devices. Completed verified pieces can be reused after an interrupted run.

Original archive SHA256: `974f3aba98a6958c88a941f70edba659b0048b8feeae9cef8b9984dfde086b8e`.

Alternatively download all `.zip.part001` through `.zip.part007` files and the `.zip.sha256` attachment from the Release page. On Linux:

```sh
cat PolyWeave-FS-DPO-full-seed101.zip.part* > PolyWeave-FS-DPO-full-seed101.zip
sha256sum -c PolyWeave-FS-DPO-full-seed101.zip.sha256
unzip PolyWeave-FS-DPO-full-seed101.zip
```

MODEL_RELEASE.json records model identity and publication status. MODEL_DOWNLOAD.json records the exact piece sizes, hashes and URLs. The restored archive contains final safetensors weights, model configuration, the adapted 32,115-token tokenizer, licence/notice, model card and per-file checksums. Complete training data, training code, optimizer state, preference caches and original generation logs are excluded.

## Inference

Use Python3.12 with hardware-appropriate PyTorch plus requirements-inference.txt. Existing accepted DCU environments should preserve their manufacturer PyTorch build. The public release was checked on CPU with standard PyTorch2.5.1, Transformers5.15.1, tokenizers0.22.2, NumPy1.26.4 and RDKit2026.03.5; no cross-hardware identity claim is made.

```sh
python scripts/generate.py --example-index 0 --validate-input-only
python scripts/generate.py --model-dir models/PolyWeave-FS-DPO-full-seed101 --example-index 0 --attempts 20 --device auto --output results/example_0
python scripts/generate.py --model-dir models/PolyWeave-FS-DPO-full-seed101 --fragment '[C&+0]-[C&+0]-[O&+0]-[C&+0]' --size 40:59 --attempts 20 --output results/custom_query
```

The input-only check does not load weights. Example mode uses only the published condition, not its target. Prompt serialization and sampling retain the original task rules: max256 input/target tokens, temperature1.0, top-p0.95, top-k0, independent per-candidate RNG and default decode seed20261016. Unknown or lossy tokenizer encodings are rejected. Keep the paired adapted tokenizer.

Outputs are local attempts.jsonl (all attempts, including failures and duplicates), qualified_unique.csv and summary.json. Full-reference novelty is not computed because complete reference sets are unpublished. Constraint satisfaction does not establish synthesis or material properties. Identical outputs across hardware or library versions are not guaranteed.

The real model loaded successfully and the complete CLI was checked on two published conditions (with/without an explicit size bin), four attempts each. This is a release smoke check, not a new performance experiment. Details: docs/MODEL_VALIDATION.json. These new test outputs remain local.

The model archive preserves the original PolyTAO Apache-2.0 licence and modification notice; root MIT covers the public interface code. Upstream dataset terms remain separate.
