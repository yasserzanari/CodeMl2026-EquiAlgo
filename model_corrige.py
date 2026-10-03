"""EquiAlgo: transparent context-neutralized policy, independent of leaderboard tuning.

Train and validate: python model_corrige.py --train --output-dir <new directory>
Replay saved policy: python model_corrige.py --model <model.json> --output <new.csv>
Neither command overwrites an existing output or submits anything.
"""
from pathlib import Path
import argparse,hashlib,json,warnings
from decimal import Decimal
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import log_loss,f1_score,accuracy_score,brier_score_loss
from sklearn.exceptions import ConvergenceWarning

ROOT=Path(__file__).resolve().parent
REMOTE={'Bas-Saint-Laurent','Cote-Nord','Gaspesie-Iles-de-la-Madeleine'}
NUM={'academique':['R','heures'],'compact':['R','heures','log_revenu','eloigne'],
     'etendu':['R','heures','log_revenu','distance','premiere_generation']}
FAMILIES=list(NUM)
CS=[.1,1.,10.]
RATE=.40
SEED=20261003

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def features(d):
    return pd.DataFrame(dict(R=d.cote_r_equivalent.to_numpy(float),heures=d.heures_travail_semaine.to_numpy(float),
        log_revenu=np.log(d.revenu_familial_estime.to_numpy(float)),eloigne=d.region_administrative.isin(REMOTE).to_numpy(int),
        distance=d.distance_domicile_campus_km.to_numpy(float),premiere_generation=d.premiere_generation_universitaire.to_numpy(float),
        region=d.region_administrative.to_numpy(str),programme=d.programme_etudes.to_numpy(str)))

def fit(d,y,family,c):
    transforms=[('numeric',StandardScaler(),NUM[family])]
    if family=='etendu':transforms.append(('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['region','programme']))
    pipe=Pipeline([('preprocess',ColumnTransformer(transforms)),('model',LogisticRegression(C=c,max_iter=2500,tol=1e-9))])
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        pipe.fit(features(d),y)
    return pipe

def parameters(pipe,family):
    scale=pipe.named_steps['preprocess'].named_transformers_['numeric']
    coef=pipe.named_steps['model'].coef_[0];names=NUM[family];raw=coef[:len(names)]/scale.scale_
    intercept=float(pipe.named_steps['model'].intercept_[0]-np.dot(raw,scale.mean_))
    result={name:float(value) for name,value in zip(names,raw)}
    if family=='etendu':
        enc=pipe.named_steps['preprocess'].named_transformers_['categorical']
        for name,value in zip(enc.get_feature_names_out(['region','programme']),coef[len(names):]):result[str(name)]=float(value)
    return dict(intercept=intercept,coefficients=result)

def score_parts(pipe,d,family):
    p=parameters(pipe,family);b=p['coefficients']
    assert b['R']>0 and b['heures']>0,'Stop: policy requires positive R and hours slopes.'
    neutral=d.cote_r_equivalent.to_numpy(float)+(b['heures']/b['R'])*d.heures_travail_semaine.to_numpy(float)
    total=pipe.decision_function(features(d))/b['R']
    return neutral,total-neutral

def keys(ids):return np.array([hashlib.sha256(('equialgo-ties-v1|'+i).encode()).hexdigest() for i in ids])
def allocate(score,ids,rate=RATE):
    d=np.zeros(len(ids),dtype=int);d[np.lexsort((keys(ids),-np.round(score,12)))[:round(rate*len(ids))]]=1;return d

def select(d):
    y=d.decision_octroi.to_numpy(int);strat=d.region_administrative+'_'+d.decision_octroi.astype(str)
    splits=list(StratifiedKFold(3,shuffle=True,random_state=20261004).split(d,strat));trials=[]
    for family in FAMILIES:
        for c in CS:
            losses=[]
            for tr,va in splits:
                pipe=fit(d.iloc[tr],y[tr],family,c)
                losses.append(float(log_loss(y[va],pipe.predict_proba(features(d.iloc[va]))[:,1])))
            trials.append(dict(family=family,C=c,losses=losses,mean=float(np.mean(losses)),se=float(np.std(losses,ddof=1)/np.sqrt(3))))
    best=min(trials,key=lambda r:r['mean']);limit=best['mean']+best['se']
    chosen=min((r for r in trials if r['mean']<=limit),key=lambda r:(FAMILIES.index(r['family']),r['C']))
    return dict(family=chosen['family'],C=chosen['C'],one_se_limit=limit,best_loss=best['mean'],trials=trials)

def policy_decisions(d,model):
    w=Decimal(model['hours_weight_decimal'])
    scores=[Decimal(str(r))+w*Decimal(str(h)) for r,h in zip(d.cote_r_equivalent,d.heures_travail_semaine)]
    tie=keys(d.id_candidat);order=sorted(range(len(d)),key=lambda i:(-scores[i],tie[i]))
    out=np.zeros(len(d),int);out[order[:round(model['rate']*len(d))]]=1
    return out,scores

def export_policy(d,model,path):
    path=Path(path)
    if path.exists():raise FileExistsError(f'Refuse to overwrite: {path}')
    pred,_=policy_decisions(d,model)
    assert d.id_candidat.is_unique and d.id_candidat.notna().all()
    pd.DataFrame({'id_candidat':d.id_candidat,'decision_octroi':pred}).to_csv(path,index=False,lineterminator='\n')
    return pred

def run_training(output):
    import importlib.util
    driver=ROOT/'artifacts/equialgo/methode_finale_20261003/entrainer.py'
    spec=importlib.util.spec_from_file_location('methodology_training',driver)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.run(Path(output))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train',action='store_true');parser.add_argument('--output-dir')
    parser.add_argument('--model');parser.add_argument('--output');parser.add_argument('--data',default=str(ROOT/'data/equialgo/data/candidats_evaluation.csv'))
    args=parser.parse_args()
    if args.train:
        if not args.output_dir:parser.error('--train requires --output-dir (new directory)')
        run_training(args.output_dir)
    else:
        if not args.model or not args.output:parser.error('Replay requires --model and --output')
        model=json.loads(Path(args.model).read_text(encoding='utf-8'))
        d=pd.read_csv(args.data);export_policy(d,model,args.output)
        print(json.dumps({'file':args.output,'sha256':sha(args.output),'rows':len(d)}))
