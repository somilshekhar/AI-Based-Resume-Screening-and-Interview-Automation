
import json, os, datetime, uuid
LOG_PATH = '/tmp/audit_logs.jsonl'

def log_decision(candidate_id, parsed, decision, model_version='v0.0.1'):
    entry = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.datetime.utcnow().isoformat()+'Z',
        'candidate_id': candidate_id,
        'parsed_snapshot': parsed,
        'decision': decision,
        'model_version': model_version
    }
    with open(LOG_PATH,'a') as fh:
        fh.write(json.dumps(entry)+'\n')
    return entry
