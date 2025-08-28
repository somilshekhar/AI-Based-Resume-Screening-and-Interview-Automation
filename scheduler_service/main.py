
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json, os, datetime

app = FastAPI(title='Scheduler Service', version='0.1.0')
INVITES_FILE = '/tmp/scheduler_invites.json'

class Invite(BaseModel):
    candidate_name: str
    candidate_email: str
    slot_iso: str
    duration_minutes: int = 60
    interviewers: list = []

@app.post('/propose')
def propose(inv: Invite):
    # write to invites file (demo); in prod call Google Calendar/Outlook APIs
    invites = []
    if os.path.exists(INVITES_FILE):
        with open(INVITES_FILE,'r') as fh:
            invites = json.load(fh)
    invites.append(inv.dict())
    with open(INVITES_FILE,'w') as fh:
        json.dump(invites, fh, indent=2)
    return {'status':'proposed', 'invite': inv.dict()}
