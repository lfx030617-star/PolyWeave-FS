from pathlib import Path
import argparse,json,sys
from itertools import islice
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from polyweave_public.data import structures,condition_targets

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=2);ap.add_argument('--table',choices=['structures','conditions'],default='structures');a=ap.parse_args()
    if not 1<=a.limit<=30:ap.error('--limit must be 1..30')
    for row in islice(structures() if a.table=='structures' else condition_targets(),a.limit):print(json.dumps(row,ensure_ascii=False,indent=2))
