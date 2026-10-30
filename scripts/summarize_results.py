from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from polyweave_public.data import endpoints
from polyweave_public.results import summarize

if __name__=='__main__':
    print(json.dumps({'scope':'Descriptive mean and sample SD over five original training seeds. No new significance tests.','groups':summarize(endpoints())},ensure_ascii=False,indent=2))
