from pathlib import Path
import sys,json,platform
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import log_loss,f1_score,accuracy_score,brier_score_loss
from threadpoolctl import threadpool_limits
import sklearn

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import model_corrige as m

def gap(d,g):return float(abs(np.mean(d[g==1])-np.mean(d[g==0])))
def measures(y,p):
    return dict(logloss=float(log_loss(y,p)),f1_macro=float(f1_score(y,p>=.5,average='macro')),
        accuracy=float(accuracy_score(y,p>=.5)),brier=float(brier_score_loss(y,p)))

def parity_frontier(e,score):
    g=e.region_administrative.isin(m.REMOTE).to_numpy(int);tie=m.keys(e.id_candidat)
    orders=[np.array(sorted(np.flatnonzero(g==a),key=lambda i:(-score[i],tie[i]))) for a in [0,1]]
    cumulative=[np.r_[0,np.cumsum(score[order])] for order in orders]
    n0,n1=map(len,orders);q=1600;options=[]
    for k1 in range(max(0,q-n0),min(q,n1)+1):
        k0=q-k1;options.append(dict(k0=k0,k1=k1,gap=abs(k0/n0-k1/n1),total=float(cumulative[0][k0]+cumulative[1][k1])))
    max_total=max(o['total'] for o in options);rows=[]
    for epsilon in [0.,.005,.01,.02,.05,None]:
        feasible=[o for o in options if epsilon is None or o['gap']<=epsilon+1e-12]
        if not feasible:
            rows.append(dict(epsilon=epsilon,feasible=False,selection_gap=np.nan,score_retained=np.nan,score_loss=np.nan,remote_grants=np.nan));continue
        best=max(feasible,key=lambda o:o['total'])
        rows.append(dict(epsilon=epsilon,feasible=True,selection_gap=best['gap'],score_retained=best['total']/max_total,
            score_loss=max_total-best['total'],remote_grants=best['k1']))
    return pd.DataFrame(rows)

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    hp=ROOT/'data/equialgo/data/donnees_demandes.csv';ep=ROOT/'data/equialgo/data/candidats_evaluation.csv';bp=ROOT/'predictions.csv'
    hashes={str(p):m.sha(p) for p in [hp,ep,bp,ROOT/'model_corrige.py',Path(__file__),Path(__file__).with_name('PROTOCOLE.md')]}
    h=pd.read_csv(hp);e=pd.read_csv(ep);y=h.decision_octroi.to_numpy(int)
    assert len(h)==10000 and len(e)==4000 and h.id_candidat.is_unique and e.id_candidat.is_unique
    assert not h.isna().any().any() and not e.isna().any().any() and not set(h.id_candidat)&set(e.id_candidat)
    assert not h.drop(columns=['id_candidat','decision_octroi']).duplicated().any()
    strat=h.region_administrative+'_'+h.decision_octroi.astype(str)
    choices=[];records=[];oof=[];tradeoff=[];fold_models=[]
    for fold,(tr,va) in enumerate(StratifiedKFold(5,shuffle=True,random_state=m.SEED).split(h,strat)):
        assert not set(h.id_candidat.iloc[tr])&set(h.id_candidat.iloc[va])
        choice=m.select(h.iloc[tr].reset_index(drop=True));choices.append(dict(fold=fold,**choice))
        pipe=m.fit(h.iloc[tr],y[tr],choice['family'],choice['C'])
        p=pipe.predict_proba(m.features(h.iloc[va]))[:,1];s,c=m.score_parts(pipe,h.iloc[va],choice['family'])
        d=m.allocate(s,h.id_candidat.iloc[va]);g=h.region_administrative.iloc[va].isin(m.REMOTE).to_numpy(int)
        b=m.parameters(pipe,choice['family']);weight=b['coefficients']['heures']/b['coefficients']['R']
        fold_models.append(dict(fold=fold,family=choice['family'],C=choice['C'],**b))
        row=dict(fold=fold,family=choice['family'],C=choice['C'],hours_weight=weight,**measures(y[va],p),
            policy_f1_committee=float(f1_score(y[va],d,average='macro')),policy_accuracy_committee=float(accuracy_score(y[va],d)),
            policy_selection_gap=gap(d,g))
        records.append(row)
        oof.append(pd.DataFrame(dict(id_candidat=h.id_candidat.iloc[va].to_numpy(),fold=fold,label_committee=y[va],
            committee_probability=p,neutral_score=s,context_score=c,policy_decision=d,remote=g,
            region=h.region_administrative.iloc[va].to_numpy())))
        for gamma in [0.,.25,.5,.75,1.]:
            pred=m.allocate(s+(1-gamma)*c,h.id_candidat.iloc[va])
            tradeoff.append(dict(fold=fold,neutralisation=gamma,selection_gap=gap(pred,g),
                accuracy_committee=float(accuracy_score(y[va],pred)),f1_committee=float(f1_score(y[va],pred,average='macro'))))
        print(json.dumps(row),flush=True)
    final_choice=m.select(h);pipe=m.fit(h,y,final_choice['family'],final_choice['C']);pars=m.parameters(pipe,final_choice['family'])
    weight=pars['coefficients']['heures']/pars['coefficients']['R'];assert weight>0
    model=dict(schema_version=1,family=final_choice['family'],C=final_choice['C'],rate=.40,
        hours_weight_decimal=repr(weight),normative_features=['cote_r_equivalent','heures_travail_semaine'],
        neutralisation=1.,regional_quota=False,score_is_merit_probability=False,committee_model=pars,
        historical_data_sha256=m.sha(hp),code_sha256=m.sha(ROOT/'model_corrige.py'),selection='nested CV / one-standard-error rule, no leaderboard selection',
        warnings=['Context neutralization is a policy choice, not an identified causal correction.','R and hours can retain structural regional information.'])
    (out/'modele.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
    pred=m.export_policy(e,model,out/'predictions_methodologiques.csv')
    score,context=m.score_parts(pipe,e,final_choice['family']);g=e.region_administrative.isin(m.REMOTE).to_numpy(int)
    # Stability conditional on selected specification; does not choose another weight.
    rng=np.random.default_rng(20261005);groups=[np.flatnonzero(strat.to_numpy()==s) for s in sorted(strat.unique())]
    weights=[]
    for i in range(200):
        ix=np.concatenate([rng.choice(indices,len(indices),replace=True) for indices in groups])
        boot=m.fit(h.iloc[ix],y[ix],final_choice['family'],final_choice['C']);b=m.parameters(boot,final_choice['family'])['coefficients']
        weights.append(b['heures']/b['R'])
        if (i+1)%50==0:print(json.dumps({'bootstraps_completed':i+1}),flush=True)
    lo=[]
    for region in sorted(h.region_administrative.unique()):
        tr=h.region_administrative!=region;b=m.parameters(m.fit(h[tr],y[tr],final_choice['family'],final_choice['C']),final_choice['family'])['coefficients']
        lo.append(dict(excluded_region=region,hours_weight=b['heures']/b['R']))
    o=pd.concat(oof,ignore_index=True);o.to_csv(out/'hors_pli.csv',index=False)
    pd.DataFrame(records).to_csv(out/'metriques_plis.csv',index=False)
    pd.DataFrame(tradeoff).to_csv(out/'neutralisation_plis.csv',index=False)
    pd.DataFrame({'replicate':np.arange(200),'hours_weight':weights}).to_csv(out/'bootstrap_poids.csv',index=False)
    pd.DataFrame(lo).to_csv(out/'stabilite_regions.csv',index=False)
    (out/'selection_interne.json').write_text(json.dumps(dict(outer=choices,final=final_choice),indent=2),encoding='utf-8')
    (out/'modeles_plis.json').write_text(json.dumps(fold_models,indent=2),encoding='utf-8')
    frontier=parity_frontier(e,score);frontier.to_csv(out/'frontiere_parite.csv',index=False)
    slices=[]
    for region,part in o.groupby('region'):
        yy=part.label_committee.to_numpy();dd=part.policy_decision.to_numpy()
        slices.append(dict(region=region,n=len(part),selection_rate=float(dd.mean()),
            historical_tpr=float(dd[yy==1].mean()),historical_fpr=float(dd[yy==0].mean())))
    pd.DataFrame(slices).to_csv(out/'equite_historique_hors_pli.csv',index=False)
    pd.DataFrame({'id_candidat':e.id_candidat,'score_politique':score,'decision_octroi':pred,'region':e.region_administrative}).to_csv(out/'audit_evaluation.csv',index=False)
    by_region=[]
    for region,part in e.assign(decision=pred).groupby('region_administrative'):
        by_region.append(dict(region=region,n=len(part),grants=int(part.decision.sum()),selection_rate=float(part.decision.mean())))
    metric_cols=['logloss','f1_macro','accuracy','brier','policy_f1_committee','policy_accuracy_committee','policy_selection_gap']
    summary={k:float(np.mean([r[k] for r in records])) for k in metric_cols}
    report=dict(input_hashes=hashes,selected_model=model,cv_mean_metrics=summary,
        cv_sd_metrics={k:float(np.std([r[k] for r in records],ddof=1)) for k in metric_cols},
        cv_pooled_committee=measures(o.label_committee,o.committee_probability),
        bootstrap_hours_weight_percentiles=np.quantile(weights,[.025,.5,.975]).tolist(),bootstrap_all_positive=bool(np.all(np.array(weights)>0)),
        region_stability=lo,evaluation_selection_gap=gap(pred,g),evaluation_group_rates={name:float(pred[g==a].mean()) for name,a in [('centre',0),('eloigne',1)]},
        evaluation_region_rates=by_region,rows=4000,grants=int(pred.sum()),quota_percent=40.,
        candidate_sha256=m.sha(out/'predictions_methodologiques.csv'),historical_best_unchanged=True,
        true_merit_f1=None,official_equal_opportunity=None,official_35_points=None,submitted=False,
        python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__)
    assert all(m.sha(p)==v for p,v in hashes.items())
    (out/'rapport.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'selected':model,'metrics':summary,'weight_ci':report['bootstrap_hours_weight_percentiles'],
        'evaluation_selection_gap':report['evaluation_selection_gap'],'candidate_sha256':report['candidate_sha256']}),flush=True)

if __name__=='__main__':
    with threadpool_limits(limits=2):run(Path(__file__).with_name('resultats'))
