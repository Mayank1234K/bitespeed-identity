from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.schemas import IdentifyRequest
from app.services import identify_contact

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/identify")
def identify(payload: IdentifyRequest, db: Session = Depends(get_db)):

    if not payload.email and not payload.phoneNumber:
        raise HTTPException(status_code=400, detail="Provide email or phoneNumber")

    result = identify_contact(db, payload.email, payload.phoneNumber)
    return result

@app.get("/")
def root():
    return {
        "service": "Bitespeed Identity Reconciliation API",
        "status": "running"
    }