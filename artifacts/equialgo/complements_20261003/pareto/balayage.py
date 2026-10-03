"""Diagnostic de contraintes; ne modifie jamais la soumission ou le modèle."""
from pathlib import Path
from fractions import Fraction
from itertools import combinations
import hashlib, json, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score
import nbformat

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
SOURCE=ROOT/'artifacts/equialgo/methode_finale_20261003/resultats'
EPS=[0,.005,.01,.02,.05,.10,.15,.20,.25,None]
REMOTE={'Bas-Saint-Laurent','Cote-Nord','Gaspesie-Iles-de-la-Madeleine'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ties(ids):return np.array([hashlib.sha256(('equialgo-ties-v1|'+str(i)).encode()).hexdigest() for i in ids])

def allocate(score, ids, group, epsilon, quota):
    score=np.asarray(score,float);group=np.asarray(group,int);ids=np.asarray(ids)
    assert set(np.unique(group))=={0,1} and len(set(ids))==len(ids)
    order=[ix[np.lexsort((ties(ids[ix]),-score[ix]))] for g in [0,1] for ix in [np.flatnonzero(group==g)]]
    counts=list(map(len,order));cum=[np.r_[0,np.cumsum(score[ix])] for ix in order]
    options=[]
    for k1 in range(max(0,quota-counts[0]),min(quota,counts[1])+1):
        k0=quota-k1;gap=abs(Fraction(k1,counts[1])-Fraction(k0,counts[0]))
        if epsilon is None or gap<=Fraction(str(epsilon)):
            options.append((float(cum[0][k0]+cum[1][k1]),-k1,gap))
    if not options:return None
    objective,negative_k1,gap=max(options,key=lambda x:(x[0],x[1]))
    k1=-negative_k1;k0=quota-k1;d=np.zeros(len(score),int)
    d[order[0][:k0]]=1;d[order[1][:k1]]=1
    assert d.sum()==quota and set(np.unique(d))<={0,1}
    assert abs(float(gap)-abs(d[group==0].mean()-d[group==1].mean()))<1e-14
    return d,dict(selection_gap=float(gap),objective=objective,remote_grants=k1,centre_grants=k0,
                  remote_rate=k1/counts[1],centre_rate=k0/counts[0],feasible_allocations=len(options))

def metrics(y,d,g):
    r=dict(accuracy=float(accuracy_score(y,d)),f1_macro=float(f1_score(y,d,average='macro')))
    for grp,name in [(0,'centre'),(1,'remote')]:
        use=g==grp;yy=y[use];dd=d[use]
        tp=int(((yy==1)&(dd==1)).sum());fn=int(((yy==1)&(dd==0)).sum())
        fp=int(((yy==0)&(dd==1)).sum());tn=int(((yy==0)&(dd==0)).sum())
        r.update({f'{name}_tp':tp,f'{name}_fn':fn,f'{name}_fp':fp,f'{name}_tn':tn,
                  f'{name}_tpr_committee':tp/(tp+fn),f'{name}_fpr_committee':fp/(fp+tn)})
    r['tpr_gap_committee']=abs(r['centre_tpr_committee']-r['remote_tpr_committee'])
    r['fpr_gap_committee']=abs(r['centre_fpr_committee']-r['remote_fpr_committee'])
    return r

def nondominated(frame,utility):
    # Strict improvement in one axis and no worsening in the other; ties remain.
    out=[]
    for _,a in frame.iterrows():
        dom=((frame.selection_gap<=a.selection_gap+1e-12)&(frame[utility]>=a[utility]-1e-12)&
             ((frame.selection_gap<a.selection_gap-1e-12)|(frame[utility]>a[utility]+1e-12))).any()
        out.append(not bool(dom))
    return out

def check_optimizer():
    rng=np.random.default_rng(20261003)
    for n in [8,10,12]:
        ids=np.array([f'T{i}' for i in range(n)]);score=rng.normal(size=n)
        group=np.arange(n)%2;quota=round(.4*n)
        for eps in EPS:
            ans=allocate(score,ids,group,eps,quota);brute=[]
            for chosen in combinations(range(n),quota):
                d=np.zeros(n,int);d[list(chosen)]=1
                gap=abs(Fraction(int(d[group==1].sum()),int((group==1).sum()))-Fraction(int(d[group==0].sum()),int((group==0).sum())))
                if eps is None or gap<=Fraction(str(eps)):brute.append(float(score[d==1].sum()))
            assert bool(brute)==(ans is not None)
            if ans is not None:assert abs(ans[1]['objective']-max(brute))<1e-12

def main():
    before=sha(ROOT/'predictions.csv');check_optimizer()
    oof=pd.read_csv(SOURCE/'hors_pli.csv');evals=pd.read_csv(SOURCE/'audit_evaluation.csv')
    assert len(oof)==10000 and oof.id_candidat.is_unique and sorted(oof.fold.unique())==list(range(5))
    records=[];decisions=[]
    for fold,df in oof.groupby('fold'):
        group=df.remote.to_numpy(int);ids=df.id_candidat.to_numpy();score=df.committee_probability.to_numpy()
        last=-np.inf
        for eps in EPS:
            ans=allocate(score,ids,group,eps,round(.4*len(df)));row=dict(fold=int(fold),epsilon=eps,feasible=ans is not None)
            if ans is not None:
                d,r=ans;assert r['objective']>=last-1e-10;last=r['objective']
                perm=np.random.default_rng(77).permutation(len(df));p=allocate(score[perm],ids[perm],group[perm],eps,int(d.sum()))[0]
                assert np.array_equal(d[perm],p)
                row.update(r);row.update(metrics(df.label_committee.to_numpy(int),d,group))
                decisions.extend(dict(id_candidat=i,fold=int(fold),epsilon=eps,decision=int(v)) for i,v in zip(ids,d))
            records.append(row)
    byfold=pd.DataFrame(records);byfold.to_csv(OUT/'contraintes_hors_pli.csv',index=False)
    pd.DataFrame(decisions).to_csv(OUT/'decisions_diagnostic_hors_pli.csv',index=False)
    aggregate=[]
    for eps in EPS:
        part=byfold[byfold.epsilon.isna() if eps is None else byfold.epsilon==eps]
        r=dict(epsilon=eps,feasible_folds=int(part.feasible.sum()),complete=bool(part.feasible.all()))
        if r['complete']:
            for c in ['selection_gap','accuracy','f1_macro','objective','tpr_gap_committee','fpr_gap_committee']:
                r[c]=float(part[c].mean());r[c+'_se']=float(part[c].std(ddof=1)/np.sqrt(5))
        aggregate.append(r)
    avg=pd.DataFrame(aggregate);valid=avg[avg.complete].copy()
    for name in ['accuracy','f1_macro','objective']:
        avg['nondomine_'+name]=pd.Series(pd.NA,index=avg.index,dtype='boolean')
        avg.loc[valid.index,'nondomine_'+name]=nondominated(valid,name)
    avg.to_csv(OUT/'front_pareto_moyennes.csv',index=False)
    ids=evals.id_candidat.to_numpy();group=evals.region.isin(REMOTE).to_numpy(int);score=evals.score_politique.to_numpy()
    ev=[];last=-np.inf
    for eps in EPS:
        ans=allocate(score,ids,group,eps,1600);r=dict(epsilon=eps,feasible=ans is not None)
        if ans is not None:
            d,info=ans;r.update(info);r['changes_vs_recommendation']=int((d!=evals.decision_octroi.to_numpy()).sum())
            assert info['objective']>=last-1e-10;last=info['objective']
            if eps is None:assert r['changes_vs_recommendation']==0
        ev.append(r)
    ev=pd.DataFrame(ev);ev.to_csv(OUT/'contrainte_politique_finale.csv',index=False)
    # Two observable panels; no claim that historical agreement is real utility.
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    ax=axes[0]
    ax.plot(valid.selection_gap*100,valid.accuracy*100,'o-',color='#244a7c',lw=1.5)
    ax.errorbar(valid.selection_gap*100,valid.accuracy*100,yerr=valid.accuracy_se*100,fmt='none',ecolor='#9badc7',capsize=3)
    offsets=[(7,-17),(-34,28),(14,3),(7,-15),(6,-15),(6,-15),(7,-16),(5,7),(7,-19)]
    for ((_,r),(dx,dy)) in zip(valid.iterrows(),offsets):
        label='Libre' if pd.isna(r.epsilon) else f'ε={r.epsilon:g}'
        ax.annotate(label,(r.selection_gap*100,r.accuracy*100),xytext=(dx,dy),textcoords='offset points',fontsize=8)
    ax.set(xlabel='Écart de taux de sélection observé (points de %)',ylabel='Accord avec le comité historique (%)',
           title='Score du comité hors pli, budget 40 %')
    ax.grid(alpha=.2);ax.margins(x=.14,y=.18)
    ax=axes[1];x=[float(e)*100 for e in EPS if e is not None and e>0]
    y=ev.loc[ev.epsilon.notna()&(ev.epsilon>0),'selection_gap'].to_numpy()*100
    ax.plot(x,y,'o-',color='#147d64');ax.plot(x,x,'--',color='#b1b1b1',label='Borne autorisée')
    ax.set(xlabel='Contrainte ε (points de %)',ylabel='Écart de taux observé (points de %)',
           title='Politique finale : contraintes non actives')
    ax.annotate('0,0207 point ; mêmes 1 600 bénéficiaires',xy=(13,float(y[0])),xytext=(7,6),
                arrowprops={'arrowstyle':'->','color':'#147d64'},fontsize=9)
    ax.legend(loc='upper left');ax.grid(alpha=.2)
    fig.suptitle('Balayage d’une contrainte explicite de parité démographique',fontsize=14)
    fig.savefig(OUT/'front_pareto_contrainte.png',dpi=160);plt.close(fig)
    # Additional direct constraint-response chart avoids any ambiguity in epsilon labels.
    fig,ax=plt.subplots(figsize=(9,4.7),constrained_layout=True)
    points=valid[valid.epsilon.notna()]
    ax.plot(points.epsilon*100,points.selection_gap*100,'o-',label='Écart observé',color='#244a7c')
    ax.plot(points.epsilon*100,points.epsilon*100,'--',label='Borne ε',color='#999999')
    ax.set(xlabel='Contrainte ε (points de %)',ylabel='Écart de taux de sélection (points de %)',title='Contrainte et écart obtenu — moyenne des cinq plis')
    ax.legend();ax.grid(alpha=.2);fig.savefig(OUT/'contrainte_et_ecart.png',dpi=160);plt.close(fig)
    assert sha(ROOT/'predictions.csv')==before
    report=dict(epsilon_grid=EPS,budget=.4,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [SOURCE/'hors_pli.csv',SOURCE/'audit_evaluation.csv',ROOT/'predictions.csv',OUT/'PROTOCOLE.md',Path(__file__)]},
                checks={'exhaustive_small_cases':True,'budget':True,'exact_rational_constraint':True,'monotonic_objective':True,'permutation_invariance':True,'recommended_csv_unchanged':True,'unconstrained_final_replayed':True},
                note='Front observable auxiliaire contre le comité biaisé. Aucune performance contre mérite ni égalité des chances réelle disponible.')
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    write_docs(avg,ev)
    print(avg.to_string(index=False));print(ev.to_string(index=False));print('CHECKS OK')

def write_docs(avg,ev):
    complete=avg[avg.complete];tight=complete.iloc[0];free=complete.iloc[-1]
    text=f'''## Front de Pareto observable : contrainte de parité explicite

Le cahier exige plusieurs réglages d’une contrainte d’équité. Nous fixons **ε = 0 ; 0,005 ; 0,01 ; 0,02 ; 0,05 ; 0,10 ; 0,15 ; 0,20 ; 0,25 ; sans contrainte**, avant le calcul. ε borne la différence absolue entre les taux de sélection des centres et des régions éloignées. Budget fixé à 40 % pour chaque cohorte. ε = 0,005 correspond à **0,5 point de pourcentage**, pas 0,005 point.

Dans chaque pli externe de 2 000 observations, on utilise les probabilités déjà produites hors pli par le modèle du comité. On énumère chaque nombre entier admissible de bourses régionales et on sélectionne les meilleurs scores de chaque groupe. L’allocation retenue maximise la somme des probabilités prédites, sous quota total et contrainte de parité. Les étiquettes du pli servent seulement à mesurer les résultats ; aucun seuil n’est ajusté pour optimiser ses étiquettes. Il s’agit d’une politique de sélection par cohorte utilisant ses groupes et scores, pas d’un seuil individuel estimé sur ces étiquettes.

**Les résultats sont des diagnostics contre les décisions biaisées du comité, pas contre le mérite.** L’accuracy mesure ici un accord historique ; le TPR signifie « proportion des anciens bénéficiaires sélectionnés ». Ni ce TPR ni sa différence régionale ne mesurent l’égalité des chances officielle. Aucun point de ce balayage n’est utilisé pour modifier la recommandation.

À ε = {tight.epsilon:g}, l’écart moyen est **{tight.selection_gap*100:.3f} points**, l’accord historique **{tight.accuracy*100:.3f} %** et le F1 macro **{tight.f1_macro*100:.3f} %**. Sans contrainte, l’écart est **{free.selection_gap*100:.3f} points**, l’accord **{free.accuracy*100:.3f} %** et le F1 macro **{free.f1_macro*100:.3f} %**. Les moyennes utilisent les cinq plis externes, avec exactement 800 bourses par pli. La parité exacte (ε = 0) est faisable dans trois plis seulement ; aucune moyenne sur ce sous-ensemble n’est présentée comme comparable aux cinq plis. Les barres représentent une erreur standard descriptive entre cinq plis dépendants ; elles n’estiment pas l’incertitude du mérite caché.

Le fichier `front_pareto_moyennes.csv` identifie séparément les points non dominés pour écart/accuracy, écart/F1 et écart/somme des scores. « Non dominé » est limité à cette grille et à ces métriques auxiliaires. Les seuils de contrainte et le modèle de score sont fixés ; cette analyse ne constitue pas une nouvelle sélection indépendante de modèle. Les métriques TPR/FPR par groupe et les comptes TP/FN/FP/TN figurent dans `contraintes_hors_pli.csv`.

![Balayage de contrainte](front_pareto_contrainte.png)

La **politique finale neutralisée** est analysée séparément sur les 4 000 demandes sans étiquette. Sa parité démographique est presque spontanée : **0,0207 point**. Toutes les contraintes ε ≥ 0,005 sont non actives et redonnent exactement les mêmes 1 600 bénéficiaires. La parité exacte est infaisable pour ces effectifs entiers et ce budget. Il serait trompeur de dessiner plusieurs allocations distinctes pour ce modèle : son front observé se réduit à un point. Les points distincts de la figure de gauche proviennent donc explicitement du modèle reproduisant le comité, à des fins de diagnostic. Cette expérience démontre un compromis observable, pas le front officiel caché. La parité démographique est un indicateur accessible, alors que l’égalité des chances contre mérite est le critère du jury que nous ne pouvons mesurer.

**Limites et décision.** La contrainte utilise directement le groupe régional ; c’est un mécanisme de post-traitement étudié et non appliqué à `predictions.csv`. Aucun label de mérite n’est inventé. Une meilleure concordance avec le comité ne prouve pas une meilleure utilité réelle. Pour déployer une contrainte d’égalité des chances, il faudrait un échantillon de mérite indépendant et une politique approuvée, puis une nouvelle validation. Notre allocation neutralisée et son CSV restent inchangés.

Reproduction depuis la racine : `.\\.venv\\Scripts\\python.exe artifacts/equialgo/complements_20261003/pareto/balayage.py`. Le protocole, les décisions de diagnostic et la vérification numérique sont archivés dans le même dossier.
'''
    (OUT/'section_notebook.md').write_text(text,encoding='utf-8')
    # Fragment is deliberately nonexecuted; parent integrates and executes in final notebook.
    intro=text.split('![Balayage de contrainte]')[0]
    ending=text.split('![Balayage de contrainte](front_pareto_contrainte.png)')[1]
    code="""from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
pareto_dir = ROOT / 'artifacts/equialgo/complements_20261003/pareto'
pareto_moyennes = pd.read_csv(pareto_dir/'front_pareto_moyennes.csv')
pareto_final = pd.read_csv(pareto_dir/'contrainte_politique_finale.csv')
display(pareto_moyennes)
pf = pareto_moyennes[pareto_moyennes['complete']]
fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
axes[0].errorbar(pf.selection_gap*100, pf.accuracy*100,
                 yerr=pf.accuracy_se*100, fmt='o-', capsize=3, color='#244a7c')
label_offsets = [(7,-17),(-34,28),(14,3),(7,-15),(6,-15),(6,-15),(7,-16),(5,7),(7,-19)]
for (_, row), offset in zip(pf.iterrows(), label_offsets):
    label = 'Libre' if pd.isna(row.epsilon) else f'ε={row.epsilon:g}'
    axes[0].annotate(label, (row.selection_gap*100,row.accuracy*100),
                     xytext=offset,textcoords='offset points',fontsize=8)
axes[0].set(xlabel='Écart de taux de sélection (points de %)',
            ylabel='Accord avec le comité historique (%)', title='Score comité hors pli — budget 40 %')
axes[0].margins(x=.14,y=.18)
pf_eval = pareto_final[pareto_final.epsilon.notna() & (pareto_final.epsilon>0)]
axes[1].plot(pf_eval.epsilon*100, pf_eval.selection_gap*100, 'o-', color='#147d64', label='Écart obtenu')
axes[1].plot(pf_eval.epsilon*100, pf_eval.epsilon*100, '--', color='#999999', label='Borne ε')
axes[1].set(xlabel='Contrainte ε (points de %)',ylabel='Écart de taux (points de %)',
            title='Politique finale : mêmes 1 600 bénéficiaires')
axes[1].legend()
for ax in axes: ax.grid(alpha=.2)
fig.suptitle('Contrainte de parité démographique — diagnostic, pas score officiel')
plt.show()
display(pareto_final)
"""
    nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(intro),nbformat.v4.new_code_cell(code),nbformat.v4.new_markdown_cell(ending)])
    nbformat.write(nb,OUT/'cellules_notebook.ipynb')

if __name__=='__main__':main()
