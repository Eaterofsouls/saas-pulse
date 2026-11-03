import json,sys,pandas as pd
R=sys.argv[1]; RUN=R+'/runs/20261102_2144/run_outputs/'
M=json.load(open(RUN+'metrics.json')); RQ=json.load(open(RUN+'rq4_correlations.json'))
P=pd.read_csv(RUN+'predictions.csv'); MO=pd.read_csv(RUN+'moat_scores.csv'); S=pd.read_csv(R+'/dataset/stock_performance.csv')
G=pd.read_csv(R+'/dataset/gold_10k_moats.csv'); MAN=pd.read_csv(R+'/dataset/MANIFEST.csv').set_index('filename')
V=pd.read_excel(sys.argv[2],sheet_name='10K_review'); V['f']=V.your_label.fillna(V.suggested_label); E=V[V.f!='exclude']
ag=(E.f==E.suggested_label).mean(); cats=set(E.f)|set(E.suggested_label); pe=sum((E.f==c).mean()*(E.suggested_label==c).mean() for c in cats)
T=M['task_1_moats']['methods']; ok=S[S.status=='ok']
tt=P.merge(V[['para_id','suggested_label']],on='para_id')
mm=MO.merge(ok[['ticker','excess_return_vs_igv']],on='ticker')
mm['rx']=mm.moat_score.rank(pct=True); mm['ry']=mm.excess_return_vs_igv.rank(pct=True)
sec=ok.groupby('category').agg(n=('ticker','size'),ret=('return_pct','median'),exc=('excess_return_vs_igv','median')).sort_values('exc',ascending=False).reset_index()
ex=P.merge(G[['para_id','text']],on='para_id').sort_values('para_id')
exs=pd.concat([ex[(ex.pred_lora==ex.true_label)&(ex.pred_few_shot!=ex.true_label)].head(2),ex[ex.pred_lora!=ex.true_label].head(1)])
h=M['task_2_hn_stance']; hp=pd.read_csv(RUN+'hn_predictions.csv')
D=dict(
 n=dict(co=int(MAN.loc['companies.csv','row_count']),fil=int(MAN.loc['filings_index.csv','row_count']),par=int(MAN.loc['filings_paragraphs.jsonl','row_count']),
   rev=int(MAN.loc['revenue.csv','row_count']),hn=int(MAN.loc['hn_comments.jsonl','row_count']),price=int(MAN.loc['pricing_pages.jsonl','row_count']),stk=len(ok),
   igv=float(S.igv_return_pct.dropna().iloc[0]),train=int((G.split=='train').sum()),test=int(len(P)),rev_eval=len(E),excl=int((V.f=='exclude').sum()),
   agree=ag,kappa=(ag-pe)/(1-pe),rule_kept=int((tt.suggested_label==tt.true_label).sum())),
 methods=[dict(k=k,name=nm,acc=T[k]['accuracy'],aci=T[k]['accuracy_wilson_ci'],f1=T[k]['macro_f1'],fci=T[k]['macro_f1_bootstrap_ci']) for k,nm in
   [('majority_baseline','Majority class'),('random_baseline','Random'),('keyword_rule_baseline','Keyword rule *'),('zero_shot','Zero-shot'),('few_shot_cot','Few-shot (6 ex.)'),('lora','LoRA fine-tuned')]],
 mcn={k:v['chi2_p_value'] for k,v in M['task_1_moats']['mcnemar_tests'].items()},
 perclass={k:v for k,v in T['lora']['per_class'].items()},
 testdist=P.true_label.value_counts().to_dict(),
 hn=dict(z=h['zero_shot']['accuracy'],zci=h['zero_shot']['accuracy_wilson_ci'],zf=h['zero_shot']['macro_f1'],f=h['few_shot']['accuracy'],fci=h['few_shot']['accuracy_wilson_ci'],ff=h['few_shot']['macro_f1'],
   zd=h['zero_shot']['pred_dist'],fd=h['few_shot']['pred_dist']),
 rho=RQ['spearman_moat_vs_excess_return'],rhog=RQ['spearman_moat_vs_revenue_growth'],
 catmoat={c['category']:c['median'] for c in RQ['category_moat_stats']},
 sec=sec.to_dict('records'),pts=mm[['ticker','rx','ry']].to_dict('records'),
 ex=[dict(t=r.ticker,fy=int(r.fiscal_year),id=r.para_id,text=' '.join(str(r.text).split()),g=r.true_label,l=r.pred_lora,f=r.pred_few_shot) for _,r in exs.iterrows()],
 epochs=float(pd.read_csv(RUN+'training_loss.csv').epoch.max()))
json.dump(D,open('data.json','w'),indent=1,default=float); print(json.dumps(D['n']))
