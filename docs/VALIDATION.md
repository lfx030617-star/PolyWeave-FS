# Public-release validation

The ten standard-library tests pass. All 300 published structures reproduce their frozen finite-graph IDs under RDKit 2026.03.5, and all 30 existing condition–target pairs satisfy the published constraints. Original evaluator function bodies are preserved; only imports and resource paths were adapted. No model was trained and no new candidate was generated.

The example files are intentionally small and do not form a complete training or independent benchmark release. Mean and sample-SD recalculation uses the 60 published endpoint-summary rows.

Inference publication preparation: the 30 serialized prompts exactly match their frozen input strings and round-trip through the adapted tokenizer. Artifact tests reject altered weights, path traversal, extra files and incorrect seed identities. The separate server exporter passed synthetic allowlist, archive checksum, tamper and overwrite tests. These are packaging/interface checks, not trained-model loading or scientific generation tests. The actual final checkpoint is still awaited. Local PyTorch import was blocked by an existing OpenMP runtime conflict, so the sampler was not executed locally in this preparation.
