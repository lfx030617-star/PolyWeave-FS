"""Readers expose only the deliberately published example files."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]

def structures():
    with (ROOT/'data/structures_300.csv').open(encoding='utf-8',newline='') as f:yield from csv.DictReader(f)

def condition_targets():
    with (ROOT/'data/condition_target_examples_30.jsonl').open(encoding='utf-8') as f:
        for line in f:
            if line.strip():yield json.loads(line)

def endpoints():
    with (ROOT/'data/paper_endpoint_summaries_60.csv').open(encoding='utf-8',newline='') as f:yield from csv.DictReader(f)
