from fastapi import FastAPI, HTTPException
import requests
import re

app = FastAPI(title="HULKCHICHA Temp Mail API")

BASE = "https://api.catchmail.io/v1"
BRANDING = "\n\nMade by HULKCHICHA 🔥"

@app.post("/create")
async def create_inbox():
    try:
        resp = requests.post(f"{BASE}/inboxes", json={"domain": "catchmail.io"}, timeout=10)
        data = resp.json()
        data["note"] = BRANDING
        return data
    except Exception as e:
        raise HTTPException(500, detail=f"Error: {str(e)}{BRANDING}")

@app.get("/inbox/{inbox_id}")
async def get_messages(inbox_id: str):
    try:
        resp = requests.get(f"{BASE}/inboxes/{inbox_id}/messages", timeout=10)
        data = resp.json()
        if isinstance(data, list):
            for msg in data:
                msg["note"] = BRANDING
        return data
    except Exception as e:
        raise HTTPException(500, detail=f"Error: {str(e)}{BRANDING}")

@app.get("/message/{msg_id}")
async def get_message(msg_id: str):
    try:
        resp = requests.get(f"{BASE}/messages/{msg_id}", timeout=10)
        data = resp.json()
        if isinstance(data, dict):
            data["note"] = BRANDING
            body = data.get("textBody", "") or data.get("htmlBody", "")
            otp = re.search(r'\b(\d{4,8})\b', body)
            if otp:
                data["otp"] = otp.group(1)
        return data
    except Exception as e:
        raise HTTPException(500, detail=f"Error: {str(e)}{BRANDING}")

@app.get("/message/{msg_id}/otp")
async def extract_otp(msg_id: str):
    try:
        resp = requests.get(f"{BASE}/messages/{msg_id}", timeout=10)
        data = resp.json()
        body = data.get("textBody", "") or data.get("htmlBody", "")
        otp_match = re.search(r'\b(\d{4,8})\b', body)
        return {
            "otp": otp_match.group(1) if otp_match else None,
            "note": BRANDING
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Error: {str(e)}{BRANDING}")

@app.get("/")
async def root():
    return {"status": "HULKCHICHA Temp Mail API Running ✅", "note": BRANDING}
