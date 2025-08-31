#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sqlite3
import shutil
from datetime import datetime


def backup_db(db_path: str) -> str:
    """Create a timestamped backup before migration."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{db_path}_backup_{ts}.db"
    shutil.copy2(db_path, backup_file)
    print(f"✅ Backup created at {backup_file}")
    return backup_file


def migrate_table(db_path: str, table_name: str, new_schema_sql: str, copy_columns: list):
    """
    Generic migration function for any table.

    :param db_path: Path to the SQLite DB file
    :param table_name: Name of the table to migrate
    :param new_schema_sql: CREATE TABLE statement for the new table (must use {table_name}_new as name)
    :param copy_columns: List of columns to copy from old to new table
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Backup first
        backup_db(db_path)

        cur.execute("PRAGMA foreign_keys=OFF;")
        cur.execute("BEGIN TRANSACTION;")

        # 1. Create new schema
        cur.execute(new_schema_sql)

        # 2. Copy old data
        cols = ", ".join(copy_columns)
        cur.execute(f"""
            INSERT INTO {table_name}_new ({cols})
            SELECT {cols} FROM {table_name}
        """)

        # 3. Drop old table
        cur.execute(f"DROP TABLE {table_name};")

        # 4. Rename new table
        cur.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name};")

        conn.commit()
        print(f"✅ Migration of {table_name} successful!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration of {table_name} failed:", e)

    finally:
        cur.execute("PRAGMA foreign_keys=ON;")
        conn.close()


if __name__ == "__main__":
    # Example: migrate operations table
    db_path = './lifeTipazaDB.db'

    migrate_table(
        db_path,
        "operations",
        """
        CREATE TABLE operations_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id INTEGER UNSIGNED NOT NULL,
            operation VARCHAR(50) CHECK(operation IN ('prime', 'retenu', 'avance')) NOT NULL,
            montant DECIMAL(10, 2),
            motif TEXT,
            date TEXT,
            observation TEXT,
            FOREIGN KEY(employe_id) REFERENCES employes(id) ON DELETE CASCADE
        )
        """,
        ["id", "employe_id", "operation", "montant", "motif", "date", "observation"]
    )

    # --- Migrate salaires ---
    migrate_table(
        db_path,
        "salaires",
        """
        CREATE TABLE salaires_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id INTEGER UNSIGNED NOT NULL,
            montant_base DECIMAL(10, 2),
            FOREIGN KEY(employe_id) REFERENCES employes(id) ON DELETE CASCADE
        )
        """,
        ["id", "employe_id", "montant_base"]
    )

    # -- Migrate salaire logs --
    migrate_table(
        db_path,
        "salaire_logs",
        """
        CREATE TABLE salaire_logs_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id INTEGER NOT NULL,
            mois TEXT NOT NULL,  -- format: '2025-07'
            salaire_base DECIMAL(10, 2),
            total_prime DECIMAL(10, 2),
            total_retenue DECIMAL(10, 2),
            total_avance DECIMAL(10, 2),
            salaire_net DECIMAL(10, 2),
            date_calcul TEXT NOT NULL,
            FOREIGN KEY(employe_id) REFERENCES employes(id) ON DELETE CASCADE
        )
        """,
        [
            "id", "employe_id", "mois",
            "salaire_base", "total_prime", "total_retenue", "total_avance", "salaire_net", "date_calcul"
        ]
    )

    # --- Migrate credit ---
    migrate_table(
        db_path,
        "credit",
        """
        CREATE TABLE credit_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_credit TEXT NOT NULL,
            client_id INTEGER UNSIGNED NOT NULL,
            montant DECIMAL(10, 2),
            motif TEXT,
            reste DECIMAL(10, 2) NOT NULL,
            statut VARCHAR(50) CHECK(statut IN ('en cours', 'terminé')) DEFAULT 'en cours',
            FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
        """,
        ["id", "date_credit", "client_id", "montant", "motif", "reste", "statut"]
    )

    # --- Migrate paiement ---
    migrate_table(
        db_path,
        "paiement",
        """
        CREATE TABLE paiement_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_versement TEXT NOT NULL,
            credit_id INTEGER UNSIGNED NOT NULL,
            client_id INTEGER UNSIGNED NOT NULL,
            montant DECIMAL(10, 2),
            observation TEXT,
            FOREIGN KEY(credit_id) REFERENCES credit(id) ON DELETE CASCADE,
            FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
        """,
        ["id", "date_versement", "credit_id", "client_id", "montant", "observation"]
    )
