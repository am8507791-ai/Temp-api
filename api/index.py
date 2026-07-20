from fastapi import FastAPI, HTTPException
import httpx
import re

app = FastAPI(title="HULKCHICHA Temp Mail API")

BASE = "https://api.catchmail.io/v1"
BRANDING = "\n\nMade by HULKCHICHA 🔥"

@app.post("/create")
async def create_inbox():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{BASE}/inboxes", json={"domain": "catchmail.io"}, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            data["note"] = BRANDING
            return data
        except Exception as e:
            raise HTTPException(500, detail=f"Error: {str(e)} {BRANDING}")

@app.get("/inbox/{inbox_id}")
async def get_messages(inbox_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE}/inboxes/{inbox_id}/messages", timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                for msg in data:
                    # INJECT BRANDING INTO SUBJECT
                    msg["subject"] = f"{msg.get('subject', 'No Subject')} | HULKCHICHA 🔥"
                    msg["note"] = BRANDING
            return data
        except Exception as e:
            raise HTTPException(500, detail=f"Error: {str(e)} {BRANDING}")

@app.get("/message/{msg_id}")
async def get_message(msg_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE}/messages/{msg_id}", timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                data["note"] = BRANDING
                
                # INJECT BRANDING DIRECTLY INTO THE EMAIL BODY
                if data.get("textBody"):
                    data["textBody"] += BRANDING
                if data.get("htmlBody"):
                    data["htmlBody"] += f"<br><br><b>Made by HULKCHICHA 🔥</b>"

                body = data.get("textBody", "") or data.get("htmlBody", "")
                otp = re.search(r'\b(\d{4,8})\b', body)
                if otp:
                    data["otp"] = otp.group(1)
            return data
        except Exception as e:
            raise HTTPException(500, detail=f"Error: {str(e)} {BRANDING}")

@app.get("/message/{msg_id}/otp")
async def extract_otp(msg_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE}/messages/{msg_id}", timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            body = data.get("textBody", "") or data.get("htmlBody", "")
            otp_match = re.search(r'\b(\d{4,8})\b', body)
            
            # Tie the OTP directly to the brand in the return value
            return {
                "otp": otp_match.group(1) if otp_match else None,
                "powered_by": "HULKCHICHA 🔥"
            }
        except Exception as e:
            raise HTTPException(500, detail=f"Error: {str(e)} {BRANDING}")

# Health check
@app.get("/")
async def root():
    return {"status": "HULKCHICHA Temp Mail API Running ✅", "note": BRANDING}
  
