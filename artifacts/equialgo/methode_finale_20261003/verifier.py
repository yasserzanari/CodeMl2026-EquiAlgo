"""Independent calculations and replay before installing the recommended CSV."""
from pathlib import Path, PureWindowsPath, PurePosixPath
import sys,json,csv,hashlib
from decimal import Decimal,InvalidOperation
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.model_selection import StratifiedKFold
from threadpoolctl import threadpool_limits

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;OUT=HERE/'resultats'
sys.path.insert(0,str(ROOT));import model_corrige as m

def manual(y,p):
    y=np.asarray(y);p=np.asarray(p);d=p>=.5;tp=((y==1)&d).sum();tn=((y==0)&~d).sum();wrong=(y!=d).sum()
    return dict(logloss=float(-(y*np.log(p)+(1-y)*np.log1p(-p)).mean()),f1_macro=float(tp/(2*tp+wrong)+tn/(2*tn+wrong)),
        accuracy=float((y==d).mean()),brier=float(np.mean((y-p)**2)))

def main():
    report=json.loads((OUT/'rapport.json').read_text(encoding='utf-8'))
    root_csv=ROOT/'predictions.csv'
    # Recorded provenance retains its original absolute paths. Resolve their
    # common project root to this checkout instead of requiring that machine.
    recorded_key=next(k for k in report['input_hashes'] if k.replace('\\','/').endswith('/predictions.csv'))
    path_kind=PureWindowsPath if '\\' in recorded_key else PurePosixPath
    recorded_root=path_kind(recorded_key).parent
    relocated={ROOT.joinpath(*path_kind(k).relative_to(recorded_root).parts):value
               for k,value in report['input_hashes'].items()}
    expected_old=report['input_hashes'][recorded_key]
    old_path=root_csv if m.sha(root_csv)==expected_old else ROOT/'artifacts/equialgo/archive/predictions_leaderboard_Q1650_bacd6c51.csv'
    def verify_inputs():
        for p,value in relocated.items():
            assert m.sha(old_path if p==root_csv else p)==value
        assert m.sha(root_csv) in [expected_old,report['candidate_sha256']]
    verify_inputs()
    h=pd.read_csv(ROOT/'data/equialgo/data/donnees_demandes.csv');e=pd.read_csv(ROOT/'data/equialgo/data/candidats_evaluation.csv')
    model=json.loads((OUT/'modele.json').read_text(encoding='utf-8'))
    p=OUT/'predictions_methodologiques.csv'
    d=pd.read_csv(p,dtype={'id_candidat':str,'decision_octroi':int});old=pd.read_csv(old_path)
    assert d.shape==(4000,2) and d.columns.tolist()==['id_candidat','decision_octroi']
    assert d.id_candidat.tolist()==e.id_candidat.tolist() and d.id_candidat.is_unique and not d.isna().any().any()
    assert set(d.decision_octroi)=={0,1} and d.decision_octroi.sum()==1600
    assert m.sha(p)==report['candidate_sha256']
    # Independent decimal formula and sort, not the prediction routine.
    w=Decimal(model['hours_weight_decimal'])
    exact=[Decimal(str(r))+w*Decimal(str(hh)) for r,hh in zip(e.cote_r_equivalent,e.heures_travail_semaine)]
    order=sorted(range(4000),key=lambda i:(-exact[i],hashlib.sha256(('equialgo-ties-v1|'+e.id_candidat.iloc[i]).encode()).hexdigest()))
    selected=set(order[:1600]);assert d.decision_octroi.tolist()==[int(i in selected) for i in range(4000)]
    target=d.set_index('id_candidat').decision_octroi.to_dict()
    for seed in [39,101,712]:
        shuffled=e.sample(frac=1,random_state=seed).reset_index(drop=True);pred,_=m.policy_decisions(shuffled,model)
        assert dict(zip(shuffled.id_candidat,pred))==target
    altered=e.copy();altered['region_administrative']='Montreal';altered['revenu_familial_estime']=50000
    altered['programme_etudes']='Arts et lettres';altered['premiere_generation_universitaire']=1;altered['distance_domicile_campus_km']=500
    invariant,changed_scores=m.policy_decisions(altered,model)
    assert np.array_equal(invariant,d.decision_octroi) and changed_scores==exact
    for col,step in [('cote_r_equivalent',.01),('heures_travail_semaine',1)]:
        increased=e.copy();increased[col]+=step;_,s=m.policy_decisions(increased,model)
        assert all(a>=b for a,b in zip(s,exact))
    # Inner selection is checked from saved fold losses, with correct simplicity rule.
    selections=json.loads((OUT/'selection_interne.json').read_text(encoding='utf-8'))
    for selection in selections['outer']+[selections['final']]:
        for trial in selection['trials']:
            assert abs(trial['mean']-np.mean(trial['losses']))<1e-12
            assert abs(trial['se']-np.std(trial['losses'],ddof=1)/np.sqrt(3))<1e-12
        best=min(selection['trials'],key=lambda x:x['mean']);limit=best['mean']+best['se']
        expected=min([t for t in selection['trials'] if t['mean']<=limit],key=lambda x:(m.FAMILIES.index(x['family']),x['C']))
        assert (expected['family'],expected['C'])==(selection['family'],selection['C'])
    o=pd.read_csv(OUT/'hors_pli.csv');metrics=pd.read_csv(OUT/'metriques_plis.csv')
    assert len(o)==10000 and o.id_candidat.is_unique
    truth=h.set_index('id_candidat').decision_octroi
    assert np.array_equal(o.id_candidat.map(truth),o.label_committee)
    packs=json.loads((OUT/'modeles_plis.json').read_text(encoding='utf-8'))
    strat=h.region_administrative+'_'+h.decision_octroi.astype(str)
    replay={}
    for fold,(tr,va) in enumerate(StratifiedKFold(5,shuffle=True,random_state=m.SEED).split(h,strat)):
        assert not set(h.id_candidat.iloc[tr])&set(h.id_candidat.iloc[va])
        saved=o[o.fold==fold].set_index('id_candidat').loc[h.id_candidat.iloc[va]]
        pack=packs[fold];assert pack['family']=='compact'
        f=m.features(h.iloc[va]);b=pack['coefficients'];z=np.full(len(f),pack['intercept'])
        for k,value in b.items():z+=value*f[k].to_numpy()
        prob=expit(z);assert np.max(abs(prob-saved.committee_probability.to_numpy()))<1e-12
        mm=manual(saved.label_committee,saved.committee_probability);row=metrics[metrics.fold==fold].iloc[0]
        assert all(abs(mm[k]-row[k])<1e-12 for k in mm)
        neutral=f.R.to_numpy()+b['heures']/b['R']*f.heures.to_numpy()
        assert np.max(abs(neutral-saved.neutral_score.to_numpy()))<1e-12
        assert np.array_equal(m.allocate(neutral,saved.index),saved.policy_decision.to_numpy())
        yy=saved.label_committee.to_numpy();dd=saved.policy_decision.to_numpy();gg=saved.remote.to_numpy()
        tp=((yy==1)&(dd==1)).sum();tn=((yy==0)&(dd==0)).sum();wrong=(yy!=dd).sum()
        assert abs(tp/(2*tp+wrong)+tn/(2*tn+wrong)-row.policy_f1_committee)<1e-12
        assert abs((dd==yy).mean()-row.policy_accuracy_committee)<1e-12
        assert abs(abs(dd[gg==0].mean()-dd[gg==1].mean())-row.policy_selection_gap)<1e-12
        if fold==0:
            again=m.select(h.iloc[tr].reset_index(drop=True))
            original=selections['outer'][0]
            assert again['family']==original['family'] and again['C']==original['C']
            assert all(abs(a['mean']-b['mean'])<1e-10 for a,b in zip(again['trials'],original['trials']))
            pipe=m.fit(h.iloc[tr],h.decision_octroi.iloc[tr],again['family'],again['C'])
            error=float(np.max(abs(pipe.predict_proba(m.features(h.iloc[va]))[:,1]-prob)))
            assert error<1e-10
            replay=dict(inner_selection_reproduced=True,max_probability_difference=error)
    # Full model re-fit yields the same weight and serialized coefficients.
    full=m.fit(h,h.decision_octroi,model['family'],model['C']);params=m.parameters(full,model['family'])
    assert abs(params['coefficients']['heures']/params['coefficients']['R']-float(w))<1e-12
    all_matches=[];comparisons=[]
    for path in sorted(set(ROOT.glob('*.csv'))|set((ROOT/'artifacts/equialgo').rglob('*.csv'))):
        if path.parent==OUT:continue
        if path==root_csv and m.sha(path)==report['candidate_sha256']:continue
        try:
            with path.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f);fields=reader.fieldnames or []
                if not {'id_candidat','decision_octroi'}<=set(fields):continue
                rows=list(reader)
            if len(rows)!=4000:continue
            mapping={r['id_candidat']:Decimal(r['decision_octroi']) for r in rows}
            if len(mapping)!=4000 or set(mapping)!=set(target) or not all(v in (0,1) for v in mapping.values()):continue
            diff=sum(mapping[i]!=target[i] for i in target)
            comparisons.append(dict(file=path.relative_to(ROOT).as_posix(),changes=diff))
            if diff==0:all_matches.append(str(path))
        except (UnicodeError,InvalidOperation,ValueError,TypeError):continue
    delta=d.decision_octroi.to_numpy()-old.decision_octroi.to_numpy()
    result=dict(candidate_sha256=m.sha(p),format_verified=True,rows=4000,grants=1600,
        independent_decimal_replay=True,permutation_invariant=True,context_invariant=True,monotonic_score=True,
        all_outer_metrics_recomputed=True,first_nested_fold_reproduced=replay,full_model_refit=True,
        comparisons_count=len(comparisons),identical_previous=all_matches,nearest_previous=sorted(comparisons,key=lambda x:x['changes'])[:5],
        changes_vs_historical_best=int((delta!=0).sum()),entries=int((delta==1).sum()),exits=int((delta==-1).sum()),
        true_merit_validated=False,old_best_unchanged=True)
    verify_inputs()
    (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=2):main()
