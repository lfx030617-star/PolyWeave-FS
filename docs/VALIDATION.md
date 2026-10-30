# Public-release validation

Fourteen standard-library tests pass, including artifact identity and verified multipart restoration checks. The 300 published structures reproduce their frozen finite-graph IDs under RDKit2026.03.5; all 30 existing condition–target pairs satisfy the frozen constraints. Original evaluator/sampler function bodies are retained with local imports adapted.

The received final full-data DPO seed101 archive and all12 members were checked. Its actual 222,893,568-parameter model loaded with the paired 32,115-token tokenizer. All30 prompts preserve exact serialization and tokenizer round trips. Cached/uncached sampling and per-candidate RNG were checked on a tiny T5; the actual model's complete CLI passed two public conditions, four attempts each, including optional size constraints. This is an engineering smoke check, not an estimate of scientific performance; generated test records remain local. The CPU runtime differs from the server's manufacturer build, so cross-hardware numerical equivalence is not claimed.

The seven actual model pieces were locally reassembled and extracted using the public downloader. The restored archive SHA256 exactly equals the author's original. Remote asset integrity and download access are checked separately at publication. See MODEL_VALIDATION.json for the bounded validation summary. No new training was performed.

The small data examples do not form a complete training or independent benchmark release. Mean and sample-SD recalculation uses the 60 published endpoint-summary rows.
