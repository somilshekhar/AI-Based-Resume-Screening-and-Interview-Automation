
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import aiofiles, uuid, os, json, asyncio, time
from pydantic import BaseModel
import requests

app = FastAPI(title='AI Resume Screening API', version='0.1.0')

PARSER_URL = os.environ.get('PARSER_URL', 'http://parser:8100/parse')
RANKER_URL = os.environ.get('RANKER_URL', 'http://ranker:8200/rank')

UPLOAD_DIR = '/tmp/resumes'
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RankRequest(BaseModel):
    job_description: str
    anonymize: bool = True

@app.post('/upload_resume')
async def upload_resume(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.pdf', '.docx', '.doc', '.txt']:
        raise HTTPException(status_code=400, detail='Unsupported file type')
    token = str(uuid.uuid4())
    dest = os.path.join(UPLOAD_DIR, f"{token}{ext}")
    async with aiofiles.open(dest, 'wb') as out:
        content = await file.read()
        await out.write(content)
    # send to parser service
    try:
        files = {'file': open(dest,'rb')}
        resp = requests.post(PARSER_URL, files=files, timeout=30)
        data = resp.json()
    except Exception as e:
        return JSONResponse({'error': 'parser_error', 'details': str(e)}, status_code=500)
    # store raw response
    with open(os.path.join(UPLOAD_DIR, f"{token}.json"), 'w') as fh:
        json.dump(data, fh, indent=2)
    return {'id': token, 'parsed': data}

@app.post('/rank/{resume_id}')
async def rank_resume(resume_id: str, payload: RankRequest):
    # load parsed resume
    path = os.path.join(UPLOAD_DIR, f"{resume_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Resume not found')
    with open(path,'r') as fh:
        parsed = json.load(fh)
    # anonymize
    if payload.anonymize:
        parsed['name'] = None
        parsed['email'] = None
    # call ranking service
    try:
        resp = requests.post(RANKER_URL, json={'parsed': parsed, 'job_description': payload.job_description}, timeout=60)
        result = resp.json()
    except Exception as e:
        return JSONResponse({'error': 'ranker_error', 'details': str(e)}, status_code=500)
    # audit log stub (could call audit service)
    # return final result
    return result

@app.post('/batch_rank')
async def batch_rank(job_description: str = Form(...)):
    # find all parsed resumes in UPLOAD_DIR
    results = []
    for p in os.listdir(UPLOAD_DIR):
        if p.endswith('.json'):
            with open(os.path.join(UPLOAD_DIR,p),'r') as fh:
                parsed = json.load(fh)
            # call ranker synchronously (demo)
            resp = requests.post(RANKER_URL, json={'parsed': parsed, 'job_description': job_description}).json()
            results.append(resp)
    # sort by score
    results = sorted(results, key=lambda x: x.get('score',0), reverse=True)
    return {'count': len(results), 'results': results}
