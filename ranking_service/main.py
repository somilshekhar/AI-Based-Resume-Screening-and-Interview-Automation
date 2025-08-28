
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np, math, json
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI(title='Ranking Service', version='0.1.0')

class RankPayload(BaseModel):
    parsed: dict
    job_description: str

def skill_match_score(skills, jd):
    if not skills: return 0.0
    jd_lower = jd.lower()
    return sum(1 for s in skills if s.lower() in jd_lower) / len(skills)

def experience_score(parsed, jd):
    exp = parsed.get('experience_years') or 0
    # example heuristic: prefer 3-7 years for mid roles
    if exp >= 7: return 1.0
    if exp >= 3: return 0.8
    if exp >=1: return 0.5
    return 0.1

def education_score(parsed):
    edu = parsed.get('education') or []
    # naive scoring
    for e in edu:
        if 'phd' in e.lower(): return 1.0
        if 'master' in e.lower() or 'ms' in e.lower(): return 0.9
        if 'bachelor' in e.lower() or 'bs' in e.lower(): return 0.7
    return 0.5

@app.post('/rank')
def rank(payload: RankPayload):
    parsed = payload.parsed
    jd = payload.job_description
    # semantic similarity between resume text and jd
    try:
        emb_resume = model.encode(parsed.get('raw_text',''), convert_to_tensor=True)
        emb_jd = model.encode(jd, convert_to_tensor=True)
        sim = util.cos_sim(emb_resume, emb_jd).item()
    except Exception as e:
        sim = 0.0
    skill_score = skill_match_score(parsed.get('skills',[]), jd)
    exp_score = experience_score(parsed, jd)
    edu_score = education_score(parsed)
    # weighted aggregate
    overall = 0.5 * sim + 0.25 * skill_score + 0.15 * exp_score + 0.10 * edu_score
    result = {
        'score': round(float(overall), 4),
        'components': {
            'semantic_similarity': round(float(sim),4),
            'skill_score': round(float(skill_score),4),
            'experience_score': round(float(exp_score),4),
            'education_score': round(float(edu_score),4)
        },
        'recommendation': 'strong_candidate' if overall>0.7 else ('consider' if overall>0.4 else 'weak_candidate')
    }
    return result
