"""Minimal health endpoint for MedMentor AI deployment."""
from fastapi import FastAPI

app = FastAPI(title="MedMentor AI")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "medmentor-ai"}

@app.get("/")
async def home():
    return {"name": "MedMentor AI", "telegram": "https://t.me/Medicalteacher_bot", "health": "/health"}
