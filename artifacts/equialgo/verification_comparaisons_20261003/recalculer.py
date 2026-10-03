"""Recalcul indépendant des comparaisons publiables. Aucun export de soumission."""
from pathlib import Path
from fractions import Fraction
import hashlib,json
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
from threadpoolctl import threadpool_limits

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SRC=ROOT/'artifacts/equialgo/methode_finale_20261003/resultats'
PARETO=ROOT/'artifacts/equialgo/complements_20261003/pareto'
REMOTE={'Bas-Saint-Laurent','Cote-Nord','Gaspesie-Iles-de-la-Madeleine'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tie(i):return hashlib.sha256(('equialgo-ties-v1|'+i).encode()).hexdigest()
def top(scores,ids,q):
    order=sorted(range(len(ids)),key=lambda j:(-scores[j],tie(ids[j])))
    d=np.zeros(len(ids),int);d[order[:q]]=1
    return d
def metrics(d,g,y=None):
    n0=int((g==0).sum());n1=int((g==1).sum())
    k0=int(d[g==0].sum());k1=int(d[g==1].sum())
    r=dict(n=len(d),grants=int(d.sum()),centre_n=n0,remote_n=n1,centre_grants=k0,remote_grants=k1,
        centre_rate=k0/n0,remote_rate=k1/n1,gap=abs(k0/n0-k1/n1),signed_gap=k0/n0-k1/n1)
    if y is not None:
        tp=int(((y==1)&(d==1)).sum());tn=int(((y==0)&(d==0)).sum())
        fp=int(((y==0)&(d==1)).sum());fn=int(((y==1)&(d==0)).sum())
        f1=.5*(2*tp/(2*tp+fp+fn)+2*tn/(2*tn+fp+fn))
        assert abs(f1-f1_score(y,d,average='macro'))<1e-14
        r.update(tp=tp,tn=tn,fp=fp,fn=fn,f1_macro=f1,accuracy=(tp+tn)/len(d))
    else:r.update(f1_macro=None,accuracy=None)
    return r
def constrained(p,ids,g,q,epsilon):
    indices=[sorted(np.flatnonzero(g==a),key=lambda j:(-p[j],tie(ids[j]))) for a in [0,1]]
    sums=[np.r_[0,np.cumsum(p[ix])] for ix in indices]
    n0,n1=map(len,indices);options=[]
    for k1 in range(max(0,q-n0),min(q,n1)+1):
        k0=q-k1
        if abs(Fraction(k0,n0)-Fraction(k1,n1))<=Fraction(str(epsilon)):
            options.append((sums[0][k0]+sums[1][k1],-k1))
    _,neg=max(options);k1=-neg;k0=q-k1
    d=np.zeros(len(ids),int);d[indices[0][:k0]]=1;d[indices[1][:k1]]=1
    return d

def main():
    frozen={f:sha(ROOT/f) for f in ['predictions.csv','model_corrige.py','modele_equialgo.json']}
    h=pd.read_csv(ROOT/'data/equialgo/data/donnees_demandes.csv')
    o=pd.read_csv(SRC/'hors_pli.csv');e=pd.read_csv(ROOT/'data/equialgo/data/candidats_evaluation.csv')
    final=pd.read_csv(ROOT/'predictions.csv');models=json.loads((SRC/'modeles_plis.json').read_text())
    choices=json.loads((SRC/'selection_interne.json').read_text())['outer']
    assert len(h)==len(o)==10000 and h.id_candidat.is_unique and o.id_candidat.is_unique
    assert set(h.id_candidat)==set(o.id_candidat) and not set(h.id_candidat)&set(e.id_candidat)
    frame=o.merge(h,on='id_candidat',how='left',validate='one_to_one')
    assert np.array_equal(frame.label_committee,frame.decision_octroi)
    assert np.array_equal(frame.remote,frame.region_administrative.isin(REMOTE).astype(int))
    strat=h.region_administrative+'_'+h.decision_octroi.astype(str)
    rows=[];outputs=[];replays=[]
    oldtrade=pd.read_csv(SRC/'neutralisation_plis.csv')
    storedpar=pd.read_csv(PARETO/'decisions_diagnostic_hors_pli.csv')
    with threadpool_limits(limits=2):
        for fold,(tr,va) in enumerate(StratifiedKFold(5,shuffle=True,random_state=20261003).split(h,strat)):
            a=frame[frame.fold==fold].copy().reset_index(drop=True)
            assert set(a.id_candidat)==set(h.id_candidat.iloc[va]) and not set(a.id_candidat)&set(h.id_candidat.iloc[tr])
            assert models[fold]['family']==choices[fold]['family']=='compact' and choices[fold]['C']==.1
            def X(d):return np.column_stack([d.cote_r_equivalent,d.heures_travail_semaine,np.log(d.revenu_familial_estime),d.region_administrative.isin(REMOTE).astype(int)])
            # Ajustement indépendant : standardisation sur les 8 000 entraînements uniquement.
            scaler=StandardScaler().fit(X(h.iloc[tr]));lr=LogisticRegression(C=.1,max_iter=2500,tol=1e-9)
            lr.fit(scaler.transform(X(h.iloc[tr])),h.decision_octroi.iloc[tr])
            p=lr.predict_proba(scaler.transform(X(a)))[:,1]
            coef=lr.coef_[0]/scaler.scale_;weight=coef[1]/coef[0]
            neutral=a.cote_r_equivalent.to_numpy()+weight*a.heures_travail_semaine.to_numpy()
            b=models[fold]['coefficients'];raw=b['R']*a.cote_r_equivalent+b['heures']*a.heures_travail_semaine+b['log_revenu']*np.log(a.revenu_familial_estime)+b['eloigne']*a.remote+models[fold]['intercept']
            assert np.max(np.abs(expit(raw)-a.committee_probability))<1e-12
            err=float(np.max(np.abs(p-a.committee_probability)));assert err<1e-9
            g=a.remote.to_numpy();y=a.label_committee.to_numpy();ids=a.id_candidat.tolist()
            variants={'comite_top40':top(p,ids,800),'neutralisee_top40':top(neutral,ids,800),'pareto_eps0005_top40':constrained(p,ids,g,800,.005)}
            assert np.array_equal(variants['neutralisee_top40'],a.policy_decision)
            assert np.array_equal(variants['comite_top40'],top((a.neutral_score+a.context_score).to_numpy(),ids,800))
            par=storedpar[(storedpar.fold==fold)&(storedpar.epsilon==.005)].set_index('id_candidat').loc[ids].decision.to_numpy()
            assert np.array_equal(variants['pareto_eps0005_top40'],par)
            for name,d in variants.items():
                r=dict(variant=name,fold=fold,**metrics(d,g,y));assert r['grants']==800
                rows.append(r)
                outputs.extend(dict(id_candidat=i,fold=fold,variant=name,decision=int(v),remote=int(gg),label_committee=int(yy)) for i,v,gg,yy in zip(ids,d,g,y))
                if name!='pareto_eps0005_top40':
                    old=oldtrade[(oldtrade.fold==fold)&(oldtrade.neutralisation==(1 if name=='neutralisee_top40' else 0))].iloc[0]
                    assert abs(r['gap']-old.selection_gap)<1e-13 and abs(r['f1_macro']-old.f1_committee)<1e-13 and abs(r['accuracy']-old.accuracy_committee)<1e-13
            replays.append(dict(fold=fold,train_n=len(tr),validation_n=len(va),probability_max_abs_difference=err,neutral_weight=weight,all_decisions_reproduced=True))
    byfold=pd.DataFrame(rows);decisions=pd.DataFrame(outputs);summary=[]
    for name,part in byfold.groupby('variant'):
        r=dict(population='historique_10000',variant=name,aggregation='moyenne_5_plis',n=10000,grants=4000)
        for c in ['centre_rate','remote_rate','gap','signed_gap','f1_macro','accuracy']:r[c]=float(part[c].mean())
        summary.append(r)
        p=decisions[decisions.variant==name]
        summary.append(dict(population='historique_10000',variant=name,aggregation='hors_pli_concatenes',**metrics(p.decision.to_numpy(),p.remote.to_numpy(),p.label_committee.to_numpy())))
    assert list(final)==['id_candidat','decision_octroi'] and len(final)==len(e)==4000 and final.id_candidat.equals(e.id_candidat)
    assert final.id_candidat.is_unique and not final.isna().any().any() and set(final.decision_octroi)=={0,1}
    summary.append(dict(population='evaluation_4000_sans_labels',variant='CSV_final',aggregation='cohorte_finale',**metrics(final.decision_octroi.to_numpy(),e.region_administrative.isin(REMOTE).to_numpy(int))))
    s=pd.DataFrame(summary)
    reductions=[]
    for aggregation in ['moyenne_5_plis','hors_pli_concatenes']:
        rows=s[s.aggregation==aggregation].set_index('variant');before=rows.loc['comite_top40']
        for after in ['neutralisee_top40','pareto_eps0005_top40']:
            r=rows.loc[after]
            reductions.append(dict(before='comite_top40',after=after,aggregation=aggregation,gap_before=before.gap,gap_after=r.gap,reduction_pct=100*(1-r.gap/before.gap),f1_before=before.f1_macro,f1_after=r.f1_macro,accuracy_before=before.accuracy,accuracy_after=r.accuracy))
    byfold.to_csv(OUT/'mesures_par_pli.csv',index=False)
    decisions.to_csv(OUT/'decisions_recalculees.csv',index=False)
    s.to_csv(OUT/'tableau_comparaisons.csv',index=False)
    pd.DataFrame(reductions).to_csv(OUT/'reductions.csv',index=False)
    sources=[SRC/'hors_pli.csv',SRC/'modeles_plis.json',SRC/'selection_interne.json',SRC/'neutralisation_plis.csv',PARETO/'decisions_diagnostic_hors_pli.csv',ROOT/'data/equialgo/data/donnees_demandes.csv',ROOT/'data/equialgo/data/candidats_evaluation.csv',ROOT/'predictions.csv',Path(__file__)]
    assert all(sha(ROOT/f)==v for f,v in frozen.items())
    report=dict(source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sources},frozen_hashes=frozen,replays=replays,
        manual_confusion_metrics_crosschecked_with_sklearn=True,stored_metrics_matched=True,stored_decisions_matched=True,
        definition='gap_k=abs(centre_grants_k/centre_n_k - remote_grants_k/remote_n_k). CV: moyenne arithmétique des cinq gaps_k. Réduction: 100*(1-mean_gap_after/mean_gap_before).',
        aggregation_warning='La moyenne des écarts absolus n’est pas l’écart absolu des taux concaténés. Le F1 moyen n’est pas non plus le F1 concaténé.',
        scope='Réajustement des 5 modèles compacts externes indépendamment du code original. Sélection interne originale lue et auditée, non entièrement recalculée ici.',
        selection_bias='Données déjà explorées et anciens retours HxBuddy connus. Validation de développement, pas test confirmatoire indépendant.',
        leakage_scope='Plis externes reconstruits, train/validation disjoints, prétraitement réajusté sur train uniquement. Aucune fuite détectée sur cette voie; liens non observés et choix antérieurs restent une limite.',
        hidden_merit_validated=False,devpost_modified=False,submission_modified=False)
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(s.to_string(index=False));print(pd.DataFrame(reductions).to_string(index=False));print('RECALCUL INDEPENDANT OK')
if __name__=='__main__':main()
