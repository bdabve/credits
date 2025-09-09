from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import sys, os
# Go up one directory (from app/ to my_project/) and add to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_handler  # Ensure database handler is imported

app = FastAPI(title="LifeTipaza API", version="1.0.0")
db = db_handler.Database("../lifeTipazaDB.db")


# === MODELES ===
class ClientCreate(BaseModel):
    nom: str
    telephone: str = ""
    commune: str = ""
    observation: str = ""


class CreditCreate(BaseModel):
    client: str
    credit_date: str   # format "dd-mm-yyyy"
    montant: float
    motif: str = ""


class VersementCreate(BaseModel):
    credit_id: int
    client_id: int
    date_versement: str
    montant: float
    observation: str = ""


# === ROUTES CLIENTS ===
@app.get("/clients")
def list_clients():
    return db.dump_clients()


@app.post("/clients")
def create_client(client: ClientCreate):
    result = db.insert_new_client(client.nom, client.telephone, client.commune, client.observation)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# === ROUTES CREDITS ===
@app.get("/credits")
def list_credits():
    rows = db.dump_credits()
    return [
        {
            "id": row[0],
            "credit_date": row[1],
            "client": row[2],
            "montant": row[4],
            "motif": row[3]
        }
        for row in rows
    ]


@app.post("/credits")
def create_credit(credit: CreditCreate):
    result = db.insert_new_credit(credit.client, credit.credit_date, credit.montant, credit.motif)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# === ROUTES VERSEMENTS ===
@app.get("/credits/{credit_id}/versements")
def get_credit_versements(credit_id: int):
    return db.get_credit_versements(credit_id)


@app.post("/versements")
def create_versement(versement: VersementCreate):
    result = db.insert_new_versement(
        versement.credit_id, versement.client_id,
        versement.date_versement, versement.montant, versement.observation
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
