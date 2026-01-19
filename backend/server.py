
from fastapi import FastAPI, Request, Header, HTTPException
import requests
import os
import datetime
import pytz

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}

@app.post('/gitlab')
async def gitlab(
    request: Request,
    x_gitlab_token: str = Header(None)
):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    if os.environ.get('GITLAB_TOKEN') != x_gitlab_token:
        raise HTTPException(status_code=403, detail="Invalid X-Gitlab-Token header")
    
    text = f"""[push gitlab]
repository : {data.get('project', {}).get('name', "-")}
ref        : {data.get('ref', '')}
username   : {data.get('user_username', '')}
timestamp  : {datetime.datetime.now(tz=pytz.timezone('asia/bangkok'))}
"""
    commits = data.get("commits", [])
    if commits:
        text += "\ncommits:\n"
        for c in commits:
            text += (
                f"  - id       : {c.get('id')[:8]}\n"
                f"    message  : {c.get('message', '').strip()}\n"
                f"    timestamp: {c.get('timestamp')}\n"
                f"    added    : {', '.join(c.get('added', [])) or '-'}\n"
                f"    modified : {', '.join(c.get('modified', [])) or '-'}\n"
                f"    url      : {c.get('url')}\n\n"
            )
    requests.post(os.environ.get('GOOGLE_CHAT_HOOK_URI'), json={
        'text': text
    })
    return {}