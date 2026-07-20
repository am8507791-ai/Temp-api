from fastapi import FastAPI, HTTPException
import requests
import re
import random
from typing import Optional

app = FastAPI(
    title="HULKCHICHA Temp Mail API",
    description="Free Temporary Email API - Made by HULKCHICHA",
    version="1.0"
)

BASE_URL = "https://api.mail.tm"
BRANDING = "\n\n🚀 Made by HULKCHICHA 🔥"

# ====================== HELPER FUNCTIONS ======================

def get_token(email: str, password: str):
    """Login aur token le aao"""
    try:
        resp = requests.post(
            f"{BASE_URL}/authentication",
            json={"address": email, "password": password},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get("token")
        return None
    except:
        return None

# ====================== ROUTES ======================

@app.get("/")
async def home():
    return {
        "message": "HULKCHICHA Temp Mail API is Running!",
        "note": BRANDING,
        "endpoints": {
            "/create": "POST - New Temp Email",
            "/inbox/{email}": "GET - Messages list (password bhi bhejna)",
            "/message/{id}": "GET - Single message + OTP",
            "/message/{id}/otp": "GET - Direct OTP"
        }
    }

@app.post("/create")
async def create_temp_email():
    """Naya temporary email banao"""
    try:
        # Available domains lo
        domains_resp = requests.get(f"{BASE_URL}/domains", timeout=8)
        domains = domains_resp.json()["hydra:member"]
        domain = random.choice(domains)["domain"]

        username = f"hulk{random.randint(10000, 99999)}"
        email = f"{username}@{domain}"
        password = "hulk12345"

        # Account create
        resp = requests.post(
            f"{BASE_URL}/accounts",
            json={"address": email, "password": password},
            timeout=10
        )

        if resp.status_code in [201, 200]:
            return {
                "email": email,
                "password": password,
                "status": "success",
                "note": BRANDING
            }
        else:
            raise HTTPException(400, "Failed to create email")
    except Exception as e:
        raise HTTPException(500, f"Server error: {str(e)}{BRANDING}")

@app.get("/inbox/{email}")
async def get_inbox(email: str, password: str):
    """Inbox ke messages dekho"""
    try:
        token = get_token(email, password)
        if not token:
            raise HTTPException(401, "Invalid credentials")

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/messages", headers=headers, timeout=10)
        
        data = resp.json()
        data["note"] = BRANDING
        return data
    except Exception as e:
        raise HTTPException(500, str(e) + BRANDING)

@app.get("/message/{msg_id}")
async def get_single_message(msg_id: str, email: str, password: str):
    """Pura message + auto OTP"""
    try:
        token = get_token(email, password)
        if not token:
            raise HTTPException(401, "Invalid credentials")

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/messages/{msg_id}", headers=headers, timeout=10)
        
        data = resp.json()
        body = data.get("text", "") or data.get("html", "")

        # Auto OTP extract
        otp_match = re.search(r'\b(\d{4,8})\b', body)
        if otp_match:
            data["otp"] = otp_match.group(1)

        data["note"] = BRANDING
        return data
    except Exception as e:
        raise HTTPException(500, str(e) + BRANDING)

@app.get("/message/{msg_id}/otp")
async def get_otp_only(msg_id: str, email: str, password: str):
    """Sirf OTP nikaalo"""
    try:
        token = get_token(email, password)
        if not token:
            raise HTTPException(401, "Invalid credentials")

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/messages/{msg_id}", headers=headers, timeout=10)
        
        body = resp.json().get("text", "")
        otp_match = re.search(r'\b(\d{4,8})\b', body)
        
        return {
            "otp": otp_match.group(1) if otp_match else None,
            "note": BRANDING
        }
    except Exception as e:
        raise HTTPException(500, str(e) + BRANDING)
