"""Reproduce regional-proxy diagnostics; writes only beside this script."""
from pathlib import Path
import hashlib, json, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nbformat
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REMOTE={'Bas-Saint-Laurent','Cote-Nord','Gaspesie-Iles-de-la-Madeleine'}
NUM=['cote_r_equivalent','heures_travail_semaine','log_revenu','distance_domicile_campus_km','premiere_generation_universitaire']
CAT=['code_postal_3','programme_etudes']
LABELS={'cote_r_equivalent':'Cote R','heures_travail_semaine':'Heures travaillées','log_revenu':'Log du revenu','distance_domicile_campus_km':'Distance au campus','premiere_generation_universitaire':'Première génération','code_postal_3':'Code postal','programme_etudes':'Programme','R_heures':'Cote R + heures','ensemble_sans_postal':'Ensemble sans postal','ensemble':'Ensemble avec postal','controle_permute':'Contrôle permuté'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build(cols):
    transforms=[]
    n=[c for c in cols if c in NUM]; c=[c for c in cols if c in CAT]
    if n: transforms.append(('num',StandardScaler(),n))
    if c: transforms.append(('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),c))
    return Pipeline([('prep',ColumnTransformer(transforms)),('model',LogisticRegression(C=1,max_iter=3000,tol=1e-9))])

def run():
    source=ROOT/'data/equialgo/data/donnees_demandes.csv'
    oofpath=ROOT/'artifacts/equialgo/methode_finale_20261003/resultats/hors_pli.csv'
    data=pd.read_csv(source); data['log_revenu']=np.log(data.revenu_familial_estime)
    assert data.id_candidat.is_unique and not data.isna().any().any()
    assert (data.revenu_familial_estime>0).all()
    assert data.drop(columns=['id_candidat','decision_octroi']).duplicated().sum()==0
    y=data.region_administrative.isin(REMOTE).to_numpy(int)
    splits=list(StratifiedKFold(5,shuffle=True,random_state=20261013).split(data,data.region_administrative))
    families={c:[c] for c in NUM+CAT}
    families.update(R_heures=NUM[:2],ensemble_sans_postal=NUM+['programme_etudes'],ensemble=NUM+CAT,controle_permute=NUM+['programme_etudes'])
    rows=[]; foldrows=[]; predictions=pd.DataFrame({'id_candidat':data.id_candidat,'remote':y,'fold':-1})
    perm=np.random.default_rng(20261014).permutation(y)
    for name,cols in families.items():
        assert not set(cols)&{'region_administrative','id_candidat','decision_octroi'}
        target=perm if name=='controle_permute' else y
        p=np.full(len(data),np.nan);seen=np.zeros(len(data),int)
        for fold,(tr,va) in enumerate(splits):
            assert not set(tr)&set(va)
            model=build(cols)
            with warnings.catch_warnings():
                warnings.simplefilter('error',ConvergenceWarning)
                model.fit(data.iloc[tr],target[tr])
            p[va]=model.predict_proba(data.iloc[va])[:,1];seen[va]+=1
            predictions.loc[va,'fold']=fold
            unknown={c:int((~data.iloc[va][c].isin(data.iloc[tr][c])).sum()) for c in cols if c in CAT}
            foldrows.append(dict(model=name,fold=fold,n_train=len(tr),n_valid=len(va),auc=float(roc_auc_score(target[va],p[va])),unknown_categories=json.dumps(unknown)))
        assert (seen==1).all() and np.isfinite(p).all()
        predictions[name]=p
        aucs=[r['auc'] for r in foldrows if r['model']==name]
        rows.append(dict(model=name,label=LABELS[name],auc_oof=float(roc_auc_score(target,p)),auc_mean=float(np.mean(aucs)),auc_min=min(aucs),auc_max=max(aucs),auc_sd=float(np.std(aucs,ddof=1))))
    predictions['remote_permuted']=perm
    summary=pd.DataFrame(rows);summary.to_csv(HERE/'auc_proxies.csv',index=False)
    pd.DataFrame(foldrows).to_csv(HERE/'auc_plis.csv',index=False)
    predictions.to_csv(HERE/'predictions_region_hors_pli.csv',index=False)
    distribution=[]
    for col in NUM+['revenu_familial_estime']:
        a=data.loc[y==0,col];b=data.loc[y==1,col]
        smd=(b.mean()-a.mean())/np.sqrt((a.var(ddof=1)+b.var(ddof=1))/2)
        distribution.append(dict(variable=col,n_centre=len(a),n_eloigne=len(b),mean_centre=a.mean(),mean_eloigne=b.mean(),median_centre=a.median(),median_eloigne=b.median(),smd_eloigne_moins_centre=smd))
    pd.DataFrame(distribution).to_csv(HERE/'distributions.csv',index=False)
    cats=[]
    for col in CAT:
        for value,part in data.groupby(col):
            cats.append(dict(variable=col,category=value,n=len(part),remote_rate=part.region_administrative.isin(REMOTE).mean()))
    pd.DataFrame(cats).to_csv(HERE/'categories.csv',index=False)
    oof=pd.read_csv(oofpath)
    merged=data.merge(oof[['id_candidat','label_committee','policy_decision','committee_probability']],on='id_candidat',validate='one_to_one')
    assert len(merged)==len(data) and (merged.decision_octroi==merged.label_committee).all()
    merged['group']=np.where(merged.region_administrative.isin(REMOTE),'Régions éloignées','Centres')
    rates=[]
    for field in ['group','region_administrative']:
        for group,part in merged.groupby(field):
            rates.append(dict(level=field,group=group,n=len(part),committee_rate=part.decision_octroi.mean(),committee_model_oof_rate=(part.committee_probability>=.5).mean(),policy_oof_rate=part.policy_decision.mean()))
    rateframe=pd.DataFrame(rates);rateframe.to_csv(HERE/'taux_octroi.csv',index=False)
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    plot=summary.set_index('model').loc[list(families)].iloc[::-1]
    fig,ax=plt.subplots(figsize=(9.6,6.5))
    xs=plot.auc_mean.to_numpy();err=np.vstack([xs-plot.auc_min,plot.auc_max-xs])
    ax.errorbar(xs,np.arange(len(plot)),xerr=err,fmt='o',color='#176b87',capsize=4)
    ax.set_yticks(np.arange(len(plot)),plot.label);ax.axvline(.5,color='#777',linestyle='--')
    ax.set_xlim(.45,1.03);ax.set_xlabel('AUC ROC — moyenne des cinq plis (barres : min–max)')
    ax.set_title('Information régionale mesurable dans les variables',loc='left',fontweight='bold')
    ax.grid(axis='x',alpha=.18)
    for i,v in enumerate(xs):ax.annotate(f'{v:.3f}',(v,i),xytext=(5,7),textcoords='offset points',fontsize=9)
    fig.text(.02,.01,'Diagnostic historique du groupe régional, pas prédiction du mérite. Régression logistique fixée.',fontsize=9)
    fig.tight_layout(rect=[0,.03,1,1]);fig.savefig(HERE/'proxies_auc.png',dpi=170);plt.close(fig)
    groups=rateframe.loc[rateframe.level=='group'].set_index('group').loc[['Centres','Régions éloignées']]
    fig,ax=plt.subplots(figsize=(9.5,5.5));x=np.arange(2);width=.24
    for i,(col,label,color) in enumerate([('committee_rate','Décisions historiques','#ba554b'),('committee_model_oof_rate','Modèle comité hors pli','#d4a247'),('policy_oof_rate','Politique neutralisée hors pli','#176b87')]):
        vals=groups[col].to_numpy()*100
        bars=ax.bar(x+(i-1)*width,vals,width,label=label,color=color)
        ax.bar_label(bars,fmt='%.2f %%',padding=4,fontsize=9)
    ax.set_ylim(0,60);ax.set_xticks(x,groups.index);ax.set_ylabel('Taux d’octroi (%)')
    ax.set_title('Le déséquilibre du comité est observable',loc='left',fontweight='bold')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.1),ncol=1,frameon=False)
    fig.text(.02,.01,'Taux descriptifs ; ils ne mesurent ni mérite réel ni égalité des chances.',fontsize=9)
    fig.tight_layout(rect=[0,.08,1,1]);fig.savefig(HERE/'octroi_groupes.png',dpi=170);plt.close(fig)
    evidence={'historical_sha256':sha(source),'oof_policy_sha256':sha(oofpath),'code_sha256':sha(Path(__file__)),'protocol_sha256':sha(HERE/'PROTOCOLE.md'),'seed':20261013,'permutation_seed':20261014,'rows':len(data),'n_centre':int((y==0).sum()),'n_eloigne':int(y.sum()),'folds':5,'models':len(families),'fits':len(foldrows),'auc':rows,'rates':rates,'checks':{'unique_ids':True,'no_missing':True,'no_duplicate_features':True,'exactly_one_oof_prediction_per_row_model':True,'disjoint_folds':True,'no_forbidden_feature':True,'all_models_converged':True},'versions':{'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__},'limits':['Associations, not causal effects','No merit labels, no equal-opportunity claim','Linear log-odds diagnostic cannot exclude nonlinear proxies','Known regions and exchangeable applicants; no temporal/household validation']}
    (HERE/'resultats.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    print(summary[['label','auc_mean','auc_min','auc_max']].to_string(index=False))
    print(groups.to_string())

if __name__=='__main__':
    with threadpool_limits(limits=2):run()
