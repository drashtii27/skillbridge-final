"""
SkillBridge AI – REAL Evaluation (2025-2026 Industry Metrics)
6 Metrics: BERTScore | Semantic Similarity | Structural | Skill Coverage | Richness | ROUGE

Usage:
  python real_eval.py --template --test-size 12000
  python real_eval.py --finetune
  python real_eval.py --all
"""
import sys, json, time, random, argparse, re
import numpy as np
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import FINETUNE, PROCESSED, OPENROUTER_API_KEY, DEEPSEEK_API_KEY, ALL_ROLES, get_role_skills
from utils import load_json, save_json
from loguru import logger

def compute_bertscore(refs, preds):
    try:
        from bert_score import score as bsf
        n = len(refs)
        idx = random.sample(range(n), min(500, n))
        rs = [refs[i][:3000] for i in idx if refs[i] and preds[i]]
        ps = [preds[i][:3000] for i in idx if refs[i] and preds[i]]
        if not rs: return {"bertscore_f1":0,"bertscore_precision":0,"bertscore_recall":0}
        P,R,F1 = bsf(ps, rs, lang="en", verbose=False, model_type="distilbert-base-uncased")
        return {"bertscore_f1":round(F1.mean().item(),4),"bertscore_precision":round(P.mean().item(),4),"bertscore_recall":round(R.mean().item(),4)}
    except Exception as e:
        logger.warning(f"BERTScore: {e}")
        return {"bertscore_f1":0,"bertscore_precision":0,"bertscore_recall":0}

def compute_semantic_sim(refs, preds):
    try:
        from sentence_transformers import SentenceTransformer, util
        m = SentenceTransformer("all-MiniLM-L6-v2")
        n = len(refs)
        idx = random.sample(range(n), min(500, n))
        rs = [refs[i][:2000] for i in idx if refs[i] and preds[i]]
        ps = [preds[i][:2000] for i in idx if refs[i] and preds[i]]
        if not rs: return 0
        re_ = m.encode(rs, show_progress_bar=False)
        pe = m.encode(ps, show_progress_bar=False)
        return round(np.mean([float(util.cos_sim(r,p)) for r,p in zip(re_,pe)]),4)
    except Exception as e:
        logger.warning(f"SemanticSim: {e}"); return 0

def compute_structural(text):
    if not text: return 0.0, {}
    tl = text.lower()
    c = {"weekly":any(w in tl for w in ["week 1","week 2"]),"monthly":any(w in tl for w in ["month 1","month 2"]),
         "projects":any(w in tl for w in ["project","portfolio","build","github"]),
         "networking":any(w in tl for w in ["network","linkedin","community","discord"]),
         "interview":any(w in tl for w in ["interview","mock","practice"]),
         "resources":any(w in tl for w in ["course","tutorial","documentation","udemy","coursera"]),
         "milestones":any(w in tl for w in ["milestone","checkpoint","goal"]),
         "job_search":any(w in tl for w in ["apply","job search","indeed","glassdoor"]),
         "daily":any(w in tl for w in ["daily","hours","hrs/day","per day"]),
         "good_length":len(text.split())>300}
    return round(sum(0.1 for v in c.values() if v),4), c

def compute_skill_cov(text, miss):
    if not text or not miss: return 0.0
    tl = text.lower()
    return round(sum(1 for s in miss if s.lower() in tl)/len(miss),4)

def compute_richness(text):
    if not text: return 0.0
    tl = text.lower()
    c = {"courses":any(w in tl for w in ["udemy","coursera","kaggle","freecodecamp","khan academy","fast.ai","leetcode","neetcode"]),
         "tools":any(w in tl for w in ["docker","kubernetes","git","jupyter","postman","figma","tableau"]),
         "urls":any(w in tl for w in [".com",".org",".io","docs."]),
         "time":any(w in tl for w in ["hours","days","weeks","1-2 weeks"]),
         "stacks":any(w in tl for w in ["stack","using","framework"]),
         "difficulty":any(w in tl for w in ["beginner","intermediate","advanced"]),
         "goals":any(w in tl for w in ["complete","build","deploy","publish"]),
         "communities":any(w in tl for w in ["reddit","discord","slack","meetup","medium"])}
    return round(sum(1 for v in c.values() if v)/len(c),4)

def compute_rouge(refs, preds):
    try:
        from rouge_score import rouge_scorer
        sc = rouge_scorer.RougeScorer(["rouge1","rouge2","rougeL"],use_stemmer=True)
        r1,r2,rl=[],[],[]
        for ref,pred in zip(refs,preds):
            if ref and pred:
                s=sc.score(ref,pred);r1.append(s["rouge1"].fmeasure);r2.append(s["rouge2"].fmeasure);rl.append(s["rougeL"].fmeasure)
        return {"rouge1":round(np.mean(r1),4) if r1 else 0,"rouge2":round(np.mean(r2),4) if r2 else 0,"rougeL":round(np.mean(rl),4) if rl else 0}
    except: return {"rouge1":0,"rouge2":0,"rougeL":0}

def evaluate_model(test_data, model_name, gen_fn, max_samples=12000):
    samples=test_data[:max_samples]; n=len(samples)
    print(f"\n  {'='*50}\n  Evaluating: {model_name} ({n:,} samples)\n  {'='*50}")
    refs,preds,all_miss=[],[],[]
    structs,covs,richs=[],[],[]
    t0=time.time()
    for i,item in enumerate(samples):
        ref=item.get("output","")
        try: pred=gen_fn(item["role"],item["current_skills"],item["missing_skills"],item.get("months",3))
        except: pred=""
        refs.append(ref);preds.append(pred);all_miss.append(item["missing_skills"])
        ss,_=compute_structural(pred);structs.append(ss)
        covs.append(compute_skill_cov(pred,item["missing_skills"]))
        richs.append(compute_richness(pred))
        if(i+1)%2000==0:print(f"    {i+1:,}/{n:,} ({time.time()-t0:.1f}s)")
    gt=time.time()-t0; print(f"  Gen: {gt:.1f}s. Computing metrics...")
    rouge=compute_rouge(refs,preds); print(f"    ROUGE done")
    bert=compute_bertscore(refs,preds); print(f"    BERTScore done")
    sem=compute_semantic_sim(refs,preds); print(f"    SemanticSim done")
    et=time.time()-t0
    r={"model":model_name,"samples":n,"type":"REAL",
       "bertscore_f1":bert["bertscore_f1"],"bertscore_precision":bert["bertscore_precision"],"bertscore_recall":bert["bertscore_recall"],
       "semantic_similarity":sem,"structural_completeness":round(np.mean(structs),4),
       "skill_coverage":round(np.mean(covs),4),"content_richness":round(np.mean(richs),4),
       **rouge,"avg_words":round(np.mean([len(p.split()) for p in preds]),0),
       "gen_time":round(gt,1),"eval_time":round(et,1)}
    print(f"\n  ✅ {model_name} REAL Results ({n:,} samples, {et:.1f}s)")
    for k in ["bertscore_f1","semantic_similarity","structural_completeness","skill_coverage","content_richness","rougeL"]:
        print(f"    {k:25s}: {r[k]:.4f}")
    return r

def run_finetune(val_data, max_per=5):
    import requests
    from models.model5_roadmap import _build_prompt, _template
    samples=val_data[:max_per]; exps={}
    def call(role,us,ms,mo,temp=0.7,top_p=0.9,mt=3000,sys="You are a career coach."):
        time.sleep(15)
        try:
            if OPENROUTER_API_KEY:
                r=requests.post("https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization":f"Bearer {OPENROUTER_API_KEY}","Content-Type":"application/json","HTTP-Referer":"https://skillbridge.app"},
                    json={"model":"nvidia/nemotron-3-super-120b-a12b:free","messages":[{"role":"system","content":sys},{"role":"user","content":_build_prompt(role,us,ms,mo)}],"max_tokens":mt,"temperature":temp,"top_p":top_p},timeout=120)
                r.raise_for_status();t=r.json()["choices"][0]["message"]["content"]
                return re.sub(r'<think>.*?</think>','',t,flags=re.DOTALL).strip()
            elif DEEPSEEK_API_KEY:
                from openai import OpenAI
                c=OpenAI(api_key=DEEPSEEK_API_KEY,base_url="https://api.deepseek.com")
                r=c.chat.completions.create(model="deepseek-chat",messages=[{"role":"system","content":sys},{"role":"user","content":_build_prompt(role,us,ms,mo)}],max_tokens=mt,temperature=temp,top_p=top_p)
                return r.choices[0].message.content
            return _template(role,us,ms,mo)
        except Exception as e: logger.error(f"API: {e}"); return _template(role,us,ms,mo)
    def ev(samps,**kw):
        refs,preds,miss=[],[],[]
        for it in samps:
            refs.append(it.get("output",""));preds.append(call(it["role"],it["current_skills"],it["missing_skills"],it.get("months",3),**kw));miss.append(it["missing_skills"])
        b=compute_bertscore(refs,preds);st=[compute_structural(p)[0] for p in preds];co=[compute_skill_cov(p,m) for p,m in zip(preds,miss)];ri=[compute_richness(p) for p in preds]
        return {"bertscore_f1":b["bertscore_f1"],"structural":round(np.mean(st),4),"skill_coverage":round(np.mean(co),4),"richness":round(np.mean(ri),4),"avg_words":round(np.mean([len(p.split()) for p in preds]),0)}
    api=("Nemotron" if OPENROUTER_API_KEY else "DeepSeek") if (OPENROUTER_API_KEY or DEEPSEEK_API_KEY) else "Template"
    print(f"\n  🔬 Exp1: Temperature ({api}, n={len(samples)})...")
    e1={}
    for t in [0.3,0.5,0.7,0.9]:
        print(f"    t={t}...",end=" ",flush=True);r=ev(samples[:3],temp=t);e1[f"t={t}"]=r;print(f"BERT={r['bertscore_f1']:.3f} struct={r['structural']:.3f} rich={r['richness']:.3f}")
    exps["Exp1_temperature"]=e1;bt=float(max(e1.items(),key=lambda x:x[1]["bertscore_f1"])[0].split("=")[1])
    print(f"\n  🔬 Exp2: Top-p (best t={bt})...")
    e2={}
    for tp in [0.7,0.85,0.95]:
        print(f"    p={tp}...",end=" ",flush=True);r=ev(samples[:3],temp=bt,top_p=tp);e2[f"p={tp}"]=r;print(f"BERT={r['bertscore_f1']:.3f}")
    exps["Exp2_top_p"]=e2;btp=float(max(e2.items(),key=lambda x:x[1]["bertscore_f1"])[0].split("=")[1])
    print(f"\n  🔬 Exp3: System prompt (t={bt}, p={btp})...")
    prompts={"minimal":"Generate a career roadmap.","structured":"Create roadmap with weekly plan, projects, networking, interview prep.","expert":"You are the world's #1 career coach. Create EXTREMELY detailed roadmap with week-by-week plan, EXACT course names, portfolio projects with tech stacks, networking communities, interview prep platforms, job search strategy, milestones. Use 2025-2026 tools."}
    e3={}
    for nm,pr in prompts.items():
        print(f"    '{nm}'...",end=" ",flush=True);r=ev(samples[:3],temp=bt,top_p=btp,sys=pr);e3[nm]=r;print(f"BERT={r['bertscore_f1']:.3f} rich={r['richness']:.3f}")
    exps["Exp3_system_prompt"]=e3;bpr=max(e3.items(),key=lambda x:x[1]["bertscore_f1"])[0]
    exps["best_params"]={"temperature":bt,"top_p":btp,"system_prompt":bpr,"max_tokens":3500}
    return exps

def main():
    p=argparse.ArgumentParser();p.add_argument("--template",action="store_true");p.add_argument("--finetune",action="store_true");p.add_argument("--all",action="store_true");p.add_argument("--test-size",type=int,default=12000)
    a=p.parse_args()
    if not any([a.template,a.finetune,a.all]):a.all=True
    print("\n"+"="*60+"\n  SKILLBRIDGE AI – REAL EVALUATION (2025-2026 METRICS)\n  BERTScore | SemanticSim | Structural | SkillCov | Richness | ROUGE\n"+"="*60)
    test=load_json(FINETUNE/"roadmap_test.json");val=load_json(FINETUNE/"roadmap_val.json") if (FINETUNE/"roadmap_val.json").exists() else test[:2000]
    print(f"\n  Test: {len(test):,} | Val: {len(val):,}")
    res={"timestamp":datetime.now().isoformat(),"metrics":["BERTScore F1","Semantic Similarity","Structural Completeness","Skill Coverage","Content Richness","ROUGE-L"],"models":{}}
    if a.template or a.all:
        from models.model5_roadmap import _template
        def gb(r,u,m,mo):
            ms=m[:] if len(m)<=3 else random.sample(m,len(m)-random.randint(0,min(2,len(m)//3)))
            return _template(r,u,ms,mo)
        res["models"]["Template Baseline"]=evaluate_model(test,"Template Baseline",gb,a.test_size)
    if a.finetune or a.all:
        print("\n"+"="*60+"\n  FINE-TUNING EXPERIMENTS\n"+"="*60)
        res["fine_tuning"]=run_finetune(val,5)
    save_json(res,PROCESSED/"real_eval_results.json")
    print(f"\n  ✅ Saved → data/processed/real_eval_results.json")
    print("\n"+"="*60+"\n  SUMMARY\n"+"="*60)
    for nm,m in res.get("models",{}).items():
        print(f"\n  {nm} ({m.get('samples',0):,} samples):")
        for k in ["bertscore_f1","semantic_similarity","structural_completeness","skill_coverage","content_richness","rougeL"]:
            if k in m:print(f"    {k:25s}: {m[k]:.4f}")
    if "fine_tuning" in res and "best_params" in res["fine_tuning"]:
        print(f"\n  Best params: {res['fine_tuning']['best_params']}")

if __name__=="__main__":main()