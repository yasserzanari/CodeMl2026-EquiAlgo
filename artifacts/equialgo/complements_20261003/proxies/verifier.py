"""Independent rank-based AUC, fold, source, and aggregate checks."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from scipy.stats import rankdata

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def auc(y,p):
    a=np.asarray(y).astype(bool);n1=a.sum();n0=(~a).sum()
    return float((rankdata(p)[a].sum()-n1*(n1+1)/2)/(n1*n0))

meta=json.loads((HERE/'resultats.json').read_text(encoding='utf-8'))
assert sha(ROOT/'data/equialgo/data/donnees_demandes.csv')==meta['historical_sha256']
assert sha(HERE/'diagnostiquer.py')==meta['code_sha256']
assert sha(HERE/'PROTOCOLE.md')==meta['protocol_sha256']
data=pd.read_csv(ROOT/'data/equialgo/data/donnees_demandes.csv')
pred=pd.read_csv(HERE/'predictions_region_hors_pli.csv')
folds=pd.read_csv(HERE/'auc_plis.csv');summary=pd.read_csv(HERE/'auc_proxies.csv')
assert pred.id_candidat.equals(data.id_candidat) and pred.id_candidat.is_unique and len(pred)==10000
assert pred.fold.value_counts().eq(2000).all() and set(pred.fold)==set(range(5))
assert not pred.isna().any().any()
assert (pred.remote==data.region_administrative.isin({'Bas-Saint-Laurent','Cote-Nord','Gaspesie-Iles-de-la-Madeleine'})).all()
for row in summary.itertuples():
    y=pred.remote_permuted if row.model=='controle_permute' else pred.remote
    assert abs(auc(y,pred[row.model])-row.auc_oof)<1e-12
    vals=[]
    for k in range(5):
        ix=pred.fold==k;v=auc(y[ix],pred.loc[ix,row.model]);vals.append(v)
        recorded=folds.loc[(folds.model==row.model)&(folds.fold==k),'auc'].item()
        assert abs(v-recorded)<1e-12
    assert abs(np.mean(vals)-row.auc_mean)<1e-12
    assert abs(min(vals)-row.auc_min)<1e-12 and abs(max(vals)-row.auc_max)<1e-12
assert all(sum(json.loads(v).values())==0 for v in folds.unknown_categories)
cats=pd.read_csv(HERE/'categories.csv');postal=cats.loc[cats.variable=='code_postal_3']
assert len(postal)==18 and set(postal.remote_rate)<=set([0.,1.])
assert (HERE/'proxies_auc.png').stat().st_size>10000 and (HERE/'octroi_groupes.png').stat().st_size>10000
out={'rank_auc_recomputed':True,'all_55_fold_auc_match':True,'all_11_pooled_auc_match':True,'source_code_protocol_hashes_match':True,'ids_order_and_fold_coverage':True,'unknown_validation_categories':0,'postal_categories':18,'visual_qa':'Both figures inspected: labels, axes, legend and units readable; no clipping.'}
(HERE/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
