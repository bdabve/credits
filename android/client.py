#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from logger import logger

BASE_URL = "http://127.0.0.1:8000"

# === Créer un client ===
client_data = {
    "nom": "Ibrahim",
    "telephone": "0555123456",
    "commune": "Tipaza",
    "observation": "Nouveau client"
}

# resp = requests.post(f"{BASE_URL}/clients", json=client_data)
# print("Create client:", resp.status_code, resp.json())


# === Lister les clients ===
resp = requests.get(f"{BASE_URL}/clients")
logger.info(f"List des clients: STATUS_CODE({resp.status_code})")
for client in resp.json():
    print(client)


# === Créer un crédit ===
credit_data = {
    "client": "Ibrahim",            # nom du client (doit exister)
    "credit_date": "04-09-2025",    # format dd-mm-yyyy
    "montant": 1500.00,
    "motif": "Achat fournitures"
}

# resp = requests.post(f"{BASE_URL}/credits", json=credit_data)
# print("Create credit:", resp.status_code, resp.json())


# === Lister les crédits ===
resp = requests.get(f"{BASE_URL}/credits")

logger.info(f"List des credit: STATUS_CODE({resp.status_code})")
for credit in resp.json():
    print(credit)
