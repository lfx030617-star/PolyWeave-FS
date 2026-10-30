# Public data schema

structures_300.csv: example_id; primary_source (exclusive allocation for this sample); sources (all original memberships, pipe-separated); graph_id (frozen finite-graph identifier); canonical_psmiles; real_heavy_atom_count; ring_count; graph_split; pilot_eligible.

condition_target_examples_30.jsonl: sample_id, graph_id, condition_id, condition_type, input_text, target_psmiles, condition, sampling_source, sources, partition, query_origin and example_role. Each line is one existing supervised pair. F+B requires the specified fragment and two legal ports; F+B+D adds a size bin. Several answers may share an exact condition in the full task; these 30 examples do not define the complete answer set.

paper_endpoint_summaries_60.csv: one row per original experiment, scale, arm and training seed. Quantities such as Y_common are reported under the corresponding experiment's reference set. Do not combine B and C into one continuous scale curve. summarize_results.py reports descriptive means and sample SD, without adding p-values or transferring original CHOSEN1 confirmatory tests to DPO.

Only source-attributed train examples are released. The upstream sources are credited even though this public collection is called PolyWeave-FS.
