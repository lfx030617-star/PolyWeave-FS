"""Descriptive aggregation of the released seed-level summaries only."""
from collections import defaultdict
from statistics import mean,stdev

def summarize(records):
    groups=defaultdict(list)
    for row in records:groups[row['experiment'],row['scale'],row['arm']].append(row)
    results=[]
    for (experiment,scale,arm),rows in sorted(groups.items()):
        seeds=[int(r['seed']) for r in rows]
        if sorted(seeds)!=[101,202,303,404,505]:raise ValueError('Exactly one row per original training seed is required')
        out={'experiment':experiment,'scale':scale,'arm':arm,'n_training_seeds':5}
        for metric in ['Y_common','parse_pct']:
            values=[float(r[metric]) for r in rows]
            out[metric+'_mean']=mean(values);out[metric+'_sample_sd']=stdev(values)
        results.append(out)
    return results
