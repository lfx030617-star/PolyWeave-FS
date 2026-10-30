# Public-release validation

The five standard-library tests pass. All 300 published structures reproduce their frozen finite-graph IDs under RDKit 2026.03.5, and all 30 existing condition–target pairs satisfy the published constraints. Original evaluator function bodies are preserved; only imports and resource paths were adapted. No model was trained and no new candidate was generated.

The example files are intentionally small and do not form a complete training or independent benchmark release. Mean and sample-SD recalculation uses the 60 published endpoint-summary rows.
