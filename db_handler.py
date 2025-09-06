#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------


import sqlite3
from datetime import datetime
from collections import namedtuple
# import utils
# from decimal import Decimal


class Database:
    def __init__(self, db_name='lifeTipazaDB.db'):
        self.db_name = db_name
        # Enable foreign key constraints
        result = self._create_tables()
        print(f'Creating Tables Result: {result}')

        # employe and his tables
        self.employes_fields = [
            'emp.id', 'emp.nom', 'emp.telephone', 'emp.poste', 's.montant_base',
            'strftime("%d-%m-%Y", emp.date_embauche)', 'emp.observation'
        ]

        self.operation_fields = [
            'ope.id', 'strftime("%d-%m-%Y", ope.date)', 'ope.operation', 'emp.nom', 'ope.montant', 'ope.motif'
        ]
        self.operation_sum_fileds = [
            "e.nom",
            "SUM(CASE WHEN o.operation = 'prime' THEN o.montant ELSE 0 END) AS total_prime",
            "SUM(CASE WHEN o.operation = 'retenu' THEN o.montant ELSE 0 END) AS total_retenue",
            "SUM(CASE WHEN o.operation = 'avance' THEN o.montant ELSE 0 END) AS total_avance"
        ]
        # clients and his tables
        self.clients_fields = [
            "c.id", "c.nom",
            "IFNULL(SUM(CASE WHEN cr.statut = 'en cours' THEN cr.reste ELSE 0 END), 0) AS total_en_cours",
            "c.telephone", "c.commune", "c.observation"
        ]

        self.credit_fields = [
            'cr.id', 'strftime("%d-%m-%Y", cr.date_credit)', 'c.nom', 'cr.motif', 'cr.montant',
            'IFNULL(SUM(v.montant), 0) AS Versement',
            'cr.reste', 'cr.statut'
        ]

        # Charge
        self.charge_fields = [
            'ch.id', 'strftime("%d-%m-%Y", ch.date_charge)',
            'emp.nom', 'ch.montant', 'ch.motif'
        ]

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_tables(self):
        """
        Crée toutes les tables nécessaires si elles n'existent pas déjà.
        """
        with self.connect() as conn:
            cursor = conn.cursor()

            # === Tables Employés ===
            try:
                # emplyes Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom VARCHAR(255) NOT NULL,
                        telephone VARCHAR(255),
                        poste VARCHAR(255),
                        date_embauche TEXT,
                        observation TEXT
                    )
                """)
                # salaires Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS salaires (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employe_id INTEGER UNSIGNED NOT NULL,
                        montant_base DECIMAL(10, 2),
                        FOREIGN KEY(employe_id) REFERENCES employes(id) ON DELETE CASCADE
                    )
                """)
                # Operations Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS operations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employe_id INTEGER UNSIGNED NOT NULL,
                        operation VARCHAR(50) CHECK(operation IN ('prime', 'retenu', 'avance')) NOT NULL,
                        montant DECIMAL(10, 2),
                        motif TEXT,
                        date TEXT,
                        observation TEXT,
                        FOREIGN KEY(employe_id) REFERENCES employes(id) ON DELETE CASCADE
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS salaire_logs (
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
                """)
                # ======================
                # === Tables Clients ===
                # ======================
                # clients Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom VARCHAR(255) NOT NULL,
                        telephone VARCHAR(100),
                        commune VARCHAR(100),
                        observation TEXT
                    )
                """)
                # credit Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS credit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_credit TEXT NOT NULL,
                        client_id INTEGER UNSIGNED NOT NULL,
                        montant DECIMAL(10, 2),
                        motif TEXT,
                        reste DECIMAL(10, 2) NOT NULL,
                        statut VARCHAR(50) CHECK(statut IN ('en cours', 'terminé')) DEFAULT 'en cours',
                        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
                    )
                """)
                # paiment (versement) Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS paiement (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_versement TEXT NOT NULL,
                        credit_id INTEGER UNSIGNED NOT NULL,
                        client_id INTEGER UNSIGNED NOT NULL,
                        montant DECIMAL(10, 2),
                        observation TEXT,
                        FOREIGN KEY(credit_id) REFERENCES credit(id) ON DELETE CASCADE,
                        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
                    )
                """)

                # Charge
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS charges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_charge TEXT NOT NULL,
                        effectue_par VARCHAR(255),
                        montant DECIMAL(10, 2),
                        motif TEXT NOT NULL
                    )
                """)

                conn.commit()
                return {'success': True}
            except sqlite3.Error as e:
                return {'success': False, 'error': str(e)}

    def get_item_id(self, table, column_name, value):
        """
        Retrieve the ID of the last inserted item in the Persone table.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT id FROM {table} WHERE {column_name} = ?', (value,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_item(self, table, column, item_id):
        """
        get column from table_name by id
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT {column} FROM {table} WHERE id = ?', (item_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_total_credit(self):
        """
        Retrieve the total amount of all credits.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(reste) FROM credit WHERE statut = "en cours"')
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0

    def get_total_credit_by_client(self):
        """
        Retrieve the total amount of all credits.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = """
                SELECT SUM(cr.reste) FROM credit AS cr
                LEFT JOIN clients AS c ON cr.client_id = c.id
                WHERE cr.statut = "en cours"
            """
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0

    def delete_item(self, table, item_id):
        """
        Delete one or multiple items from the specified table by ID.
        :param table: Table name
        :param item_id: int or list of ints
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            try:
                if isinstance(item_id, list):
                    placeholders = ",".join("?" * len(item_id))
                    query = f"DELETE FROM {table} WHERE id IN ({placeholders})"
                    cursor.execute(query, item_id)
                else:
                    query = f"DELETE FROM {table} WHERE id = ?"
                    cursor.execute(query, (item_id,))

                conn.commit()
                return {'success': True}
            except sqlite3.Error as e:
                return {'success': False, 'error': str(e)}

    def fetch_namedtuple(self, cursor, query, params=None, tuple_name="Row"):
        """
        Executes a query and returns the result as a list of namedtuples.

        Args:
            cursor: sqlite3 cursor object.
            query (str): SQL query to execute.
            params (tuple or list, optional): Parameters for the query.
            tuple_name (str): Name for the namedtuple type.

        Returns:
            list: List of namedtuple instances, or an empty list if no results.
        """
        cursor.execute(query, params or ())
        columns = [desc[0] for desc in cursor.description]
        RowTuple = namedtuple(tuple_name, columns)
        return [RowTuple(*row) for row in cursor.fetchall()]

    # =========================
    # === EMPLOYES METHODES ===
    # =========================
    def insert_new_employe(self, nom, poste, telephone, salaire, date_embauche, observation=""):
        """
        Insert new emplye into database
        :params: nom, poste, telephone, salaire, date_embauche
        """
        with self.connect() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO employes (nom, poste, telephone, date_embauche, observation)
                    VALUES (?, ?, ?, ?, ?)""",
                    (nom, poste, telephone, date_embauche, observation)
                )
                employe_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO salaires (employe_id, montant_base) VALUES (?, ?)",
                    (employe_id, salaire)
                )
                conn.commit()
                return {'success': True, 'employe_id': employe_id}
            except sqlite3.Error as err:
                return {'success': False, 'error': str(err)}

    def dump_employes(self):
        """
        Retrieve all personnes from the database.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT {", ".join(self.employes_fields)}
                FROM employes emp
                LEFT JOIN salaires s ON emp.id = s.employe_id
                ORDER BY emp.nom
            """
            cursor.execute(query)
            return cursor.fetchall()

    def search_employe(self, search_word):
        """
        Search for personnes by name or telephone.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT {", ".join(self.employes_fields)}
                FROM employes emp
                LEFT JOIN salaires s ON emp.id = s.employe_id
                WHERE emp.nom LIKE ? OR emp.telephone LIKE ? OR emp.poste LIKE ?
                ORDER BY emp.nom
            """
            search_pattern = f'%{search_word}%'
            params = [search_pattern] * 3  # For nom, telephone, poste
            cursor.execute(query, params)
            return cursor.fetchall()

    def update_employe(self, emp_id, column, new_text):
        """
        Updates a specific column for an employee in the database.
        Parameters:
            emp_id (int): The ID of the employee to update.
            column (int): The column to update (1: nom, 2: telephone, 3: poste, 4: salaire, 5: date_embauche, 6: observation).
            new_text (str): The new value to set for the specified column.
        Returns:
            dict: A dictionary containing the result of the operation.
                - If successful: {'success': True, 'message': <success_message>}
                - If failed: {'success': False, 'error': <error_message>}
        Notes:
            - For column 4 (salaire), the value is updated in the 'salaires' table and formatted using 'format_to_decimal' from the 'utils' module.
            - Returns an error if the column is invalid or if the 'utils' module cannot be imported.

        """
        with self.connect() as conn:
            cursor = conn.cursor()
            if column == 1:  # Nom
                cursor.execute("UPDATE employes SET nom = ? WHERE id = ?", (new_text, emp_id))
                message = 'Nom mis à jour avec succès.'
            elif column == 2:  # Telephone
                cursor.execute("UPDATE employes SET telephone = ? WHERE id = ?", (new_text, emp_id))
                message = 'Téléphone mis à jour avec succès.'
            elif column == 3:  # Poste
                cursor.execute("UPDATE employes SET poste = ? WHERE id = ?", (new_text, emp_id))
                message = 'Poste mis à jour avec succès.'
            elif column == 4:  # Salaire
                try:
                    from utils import format_to_decimal
                    result = format_to_decimal(new_text)
                    if not result['success']:
                        return {'success': False, 'error': result['error']}
                    salaire_base = str(result['value'])
                    cursor.execute("UPDATE salaires SET montant_base = ? WHERE employe_id = ?", (salaire_base, emp_id))
                    message = 'Salaire mis à jour avec succès.'
                except ImportError:
                    return {'success': False, 'error': 'Module utils introuvable.'}
            elif column == 5:  # Date Embauche
                cursor.execute("UPDATE employes SET date_embauche = ? WHERE id = ?", (new_text, emp_id))
                message = "Date d'embauche mise à jour avec succès."
            elif column == 6:  # Observation
                cursor.execute("UPDATE employes SET observation = ? WHERE id = ?", (new_text, emp_id))
                message = 'Observation mise à jour avec succès.'
            else:
                return {'success': False, 'error': 'Colonne invalide.'}
            conn.commit()
            return {'success': True, 'message': message}

    # ========================
    # == Accompte Functions ==
    # ========================
    def sum_accompte(self, month):
        """
        Retrieves the sum of 'prime', 'retenu', and 'avance' operations for a given month.

        Args:
            month (str): The month in 'YYYY-MM' format to filter operations. If 'Tous', sums are calculated for all months.

        Returns:
            namedtuple: A named tuple with fields 'total_prime', 'total_retenu', and 'total_avance'.
        """
        query = """
        SELECT
            IFNULL(SUM(CASE WHEN operation = 'prime' THEN montant ELSE 0 END), 0) AS total_prime,
            IFNULL(SUM(CASE WHEN operation = 'retenu' THEN montant ELSE 0 END), 0) AS total_retenu,
            IFNULL(SUM(CASE WHEN operation = 'avance' THEN montant ELSE 0 END), 0) AS total_avance
        FROM operations
        """
        params = ()
        if month != 'Tous':
            query += " WHERE strftime('%Y-%m', date) = ?"
            params = (month,)
        with self.connect() as conn:
            cursor = conn.cursor()
            return self.fetch_namedtuple(cursor, query, params=params, tuple_name="SUM_ACCOMPTE")[0]

    def dump_operations(self, month=None):
        """
        Retrieves summarized operation data for each employee from the database.
        Executes a SQL query that selects specified fields from the 'employes' table,
        left joins the 'operations' table on employee ID, optionally filters by month,
        groups the results by employee, and orders them by employee name in ascending order.

        Args:
            month (str, optional): A string in 'YYYY-MM' format to filter operations by month.

        Returns:
            list: A list of tuples containing the selected fields for each employee.
        """
        with self.connect() as conn:
            cursor = conn.cursor()

            # base query
            query = f"""
                SELECT {", ".join(self.operation_sum_fileds)}
                FROM employes e
                LEFT JOIN operations AS o ON e.id = o.employe_id
            """

            params = ()
            if month:
                query += " WHERE strftime('%Y-%m', o.date) = ?"
                params = (month,)

            query += """
                GROUP BY e.id
                ORDER BY e.nom ASC;
            """

            cursor.execute(query, params)
            return cursor.fetchall()

    def filter_accomptes(self, employe, selected_operation, selected_month):
        """
        Retrieve all operations for a specific employe by ID and operation type.
        :emp_id: name of the employe
        :operation: Type of operation ('prime', 'retenu', 'avance')
        :month: Month in 'YYYY-MM' format to filter operations
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
            SELECT {", ".join(self.operation_fields)}
                FROM operations ope
                LEFT JOIN employes emp ON emp.id = ope.employe_id
                WHERE 1 = 1
            """
            params = []

            if employe != 'Tous':
                emp_id = self.get_item_id('employes', 'nom', employe)
                query += " AND emp.id = ?"
                params.append(emp_id)

            if selected_operation != 'tous':
                query += " AND ope.operation = ?"
                params.append(selected_operation)

            if selected_month != 'Tous':
                query += " AND strftime('%Y-%m', ope.date) = ?"
                params.append(selected_month)

            query += " ORDER BY emp.nom"
            # logger.debug(query)
            # logger.debug(params)

            cursor.execute(query, params)
            return cursor.fetchall()

    def employee_accompts(self, employe_id, date):
        """
        Retrieve all operations for a specific employe by ID, operation type, and date.
        :employe_id: ID of the employe
        :operation: Type of operation ('prime', 'retenu', 'avance')
        :date: Date in 'YYYY-MM' format to filter operations
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
            SELECT {", ".join(self.operation_fields)}
                FROM operations ope
                LEFT JOIN employes emp ON emp.id = ope.employe_id
                WHERE emp.id = ? AND strftime('%Y-%m', ope.date) = ?
                ORDER BY emp.nom
            """
            cursor.execute(query, (employe_id, date))
            return cursor.fetchall()

    def insert_new_operation(self, emp_id, operation, montant, motif, date, observation):
        """
        INSERT New Operation('prime', 'retenu' , 'avance')
        """
        query = """
            INSERT INTO operations(employe_id, operation, montant, motif, date, observation)
            VALUES(?, ?, ?, ?, ?, ?)
        """
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (emp_id, operation, montant, motif, date, observation))
                conn.commit()
                return {'success': True, 'operation_id': cursor.lastrowid}
        except sqlite3.Error as err:
            return {'success': False, 'error': str(err)}

    def calculate_salaire_mensuel(self, month: str, emp_id: int = None):
        """
        Calcule le salaire mensuel d'un employé ou de tous les employés pour un mois donné.
        :param month: 'YYYY-MM'
        :param emp_id: Optionnel (ID de l'employé)
        :return: liste de dicts ou dict si emp_id fourni
        """
        base_query = """
            SELECT
                e.id,
                s.montant_base AS salaire_base,
                COALESCE(SUM(CASE WHEN o.operation = 'prime' THEN o.montant ELSE 0 END), 0) AS total_prime,
                COALESCE(SUM(CASE WHEN o.operation = 'retenu' THEN o.montant ELSE 0 END), 0) AS total_retenue,
                COALESCE(SUM(CASE WHEN o.operation = 'avance' THEN o.montant ELSE 0 END), 0) AS total_avance
            FROM employes e
            LEFT JOIN salaires s ON e.id = s.employe_id
            LEFT JOIN operations o ON e.id = o.employe_id
                AND strftime('%Y-%m', o.date) = ?
        """
        params = [month]

        if emp_id:
            base_query += " WHERE e.id = ?"
            params.append(emp_id)

        base_query += " GROUP BY e.id"

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(base_query, params)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                emp_id, salaire_base, prime, retenue, avance = row
                salaire_base = salaire_base if salaire_base is not None else 0
                prime = prime if prime is not None else 0
                retenue = retenue if retenue is not None else 0
                avance = avance if avance is not None else 0
                salaire_final = salaire_base + prime - retenue - avance
                result.append({
                    'employe_id': emp_id,
                    'salaire_base': salaire_base,
                    'total_prime': prime,
                    'total_retenue': retenue,
                    'total_avance': avance,
                    'salaire_final': salaire_final
                })

            return result if not emp_id else (result[0] if result else None)

    def update_accompte(self, emp_id, column, new_text):
        with self.connect() as conn:
            cursor = conn.cursor()
            if column == 1:     # Date
                cursor.execute("UPDATE operations SET date = ? WHERE id = ?", (new_text, emp_id))
                message = 'Date mis à jour avec succès.'
            elif column == 2:     # operation
                # Validate operation
                operation = new_text.lower()
                if operation not in ('prime', 'retenu', 'avance'):
                    return {'success': False, 'error': "Valide operation sont: 'prime', 'retenu', 'avance'."}
                cursor.execute("UPDATE operations SET operation = ? WHERE id = ?", (operation, emp_id))
                message = 'Type d\'opération mis à jour avec succès.'
            elif column == 3:   # Employee
                return {'success': False, 'error': 'Employé ne peut pas être modifié.'}
            elif column == 4:      # Montant
                cursor.execute("UPDATE operations SET montant = ? WHERE id = ?", (str(new_text), emp_id))
                message = 'Montant mis à jour avec succès.'
            elif column == 5:   # Motif
                cursor.execute("UPDATE operations SET motif = ? WHERE id = ?", (new_text, emp_id))
                message = 'Motif mis à jour avec succès.'
            else:
                return {'success': False, 'error': 'Colonne invalide.'}
            conn.commit()
            return {'success': True, 'message': message}

    # =============
    # == Clients ==
    # =============
    def insert_new_client(self, nom, telephone, commune, observation):
        """
        Ajoute un client à la base de données.
        :params: nom, telephone, observation
        """
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO clients (nom, telephone, commune, observation) VALUES (?, ?, ?, ?)",
                    (nom, telephone, commune, observation)
                )
                conn.commit()
                return {'success': True, 'client_id': cursor.lastrowid}
        except sqlite3.Error as err:
            return {'success': False, 'error': str(err)}

    def dump_clients(self):
        """
        Retrieve all personnes from the database.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT {", ".join(self.clients_fields)}
                FROM clients c
                LEFT JOIN credit cr ON c.id = cr.client_id
                GROUP BY c.id
                ORDER BY c.nom
            """
            cursor.execute(query)
            return cursor.fetchall()

    def get_names(self, table_name):
        """
        Retrieve all clients names to display in QComboBox.
        :table_name: Name of the table to retrieve names from (e.g., 'clients', 'employes').
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT nom FROM {table_name}')
            return [row[0] for row in cursor.fetchall()]

    def search_clients(self, search_word):
        """
        Search for personnes by name or telephone.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT {", ".join(self.clients_fields)}
                FROM clients AS c
                LEFT JOIN credit cr ON c.id = cr.client_id
                WHERE c.nom LIKE ? OR c.telephone LIKE ?
                GROUP BY c.nom
            """
            search_pattern = f'%{search_word}%'
            cursor.execute(query, (search_pattern, search_pattern))
            return cursor.fetchall()

    def update_client(self, client_id, column, new_text):
        """
        Update an employe field in the database.
        :emp_id: ID of the employe
        :col: Column to update (e.g., 'nom', 'telephone', 'poste', 'observation')
        :text: New value for the column
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            if column == 1:     # Nom
                cursor.execute("UPDATE clients SET nom = ? WHERE id = ?", (new_text, client_id))
                message = 'Nom mis à jour avec succès.'
            elif column == 2:   # Credit
                # Disabled
                return {'success': False, 'error': 'Modification du crédit non autorisée.'}
            elif column == 3:   # Telephone
                cursor.execute("UPDATE clients SET telephone = ? WHERE id = ?", (new_text, client_id))
                message = 'Téléphone mis à jour avec succès.'
            elif column == 4:   # Comune
                cursor.execute("UPDATE clients SET commune = ? WHERE id = ?", (new_text, client_id))
                message = 'Commune mise à jour avec succès.'
            elif column == 5:   # Observation
                cursor.execute("UPDATE clients SET observation = ? WHERE id = ?", (new_text, client_id))
                message = 'Observation mise à jour avec succès.'
            else:
                return {'success': False, 'error': 'Colonne invalide.'}

            conn.commit()
            return {'success': True, 'message': message}

    # =========================
    # === CREDITS METHODES ===
    # =========================
    def dump_credits(self):
        """
        Retrieve all credits with associated persone names.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT {', '.join(self.credit_fields)}
                FROM credit cr
                JOIN clients c ON cr.client_id = c.id
                LEFT JOIN paiement v on v.credit_id = cr.id
                GROUP BY cr.id
                ORDER BY c.nom DESC
            """
            cursor.execute(query)
            return cursor.fetchall()

    def search_credits(self, search_word):
        """
        Search for credits by description or persone name.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT {', '.join(self.credit_fields)}
                FROM credit cr
                JOIN clients c ON cr.client_id = c.id
                LEFT JOIN paiement v on v.credit_id = cr.id
                WHERE cr.motif LIKE ? OR c.nom LIKE ? OR cr.date_credit LIKE ?
                GROUP BY cr.id
                ORDER BY c.nom DESC
            """
            params = [search_word] * 3
            cursor.execute(query, params)  # Search pattern for all three fields
            return cursor.fetchall()

    def credit_by_status(self, status):
        """
        Retrieve all credits grouped by their status.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            query = f"""
            SELECT {', '.join(self.credit_fields)}
            FROM credit cr
            JOIN clients c ON cr.client_id = c.id
            LEFT JOIN paiement v ON cr.id = v.credit_id
            WHERE cr.statut = ?
            GROUP BY cr.id
            ORDER BY c.nom DESC
            """
            cursor.execute(query, (status,))
            return cursor.fetchall()

    def insert_new_credit(self, client, credit_date, montant, motif=''):
        """
        Add a credit entry for a specific persone.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            client_id = self.get_item_id('clients', 'nom', client)
            if not client_id:
                return {'success': False, 'error': f"Client {client} n'existe pas."}

            reste = montant  # Initial remaining balance is the total amount
            try:
                query = """
                    INSERT INTO credit(client_id, date_credit, montant, reste, motif)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(query, (client_id, credit_date, montant, reste, motif))
                conn.commit()
                return {'success': True, 'credit_id': cursor.lastrowid}
            except sqlite3.Error as e:
                return {'success': False, 'error': str(e)}

    def get_client_credits(self, client_id):
        """
        Retrieve all credits for a specific client by name.
        :client: the client name
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            # Check for credit
            cursor.execute('SELECT COUNT(id) FROM credit WHERE client_id = ?', (client_id,))
            if cursor.fetchone()[0] == 0:
                return False

            query = f"""
                SELECT {', '.join(self.credit_fields)}
                FROM credit cr
                LEFT JOIN clients c ON cr.client_id = c.id
                LEFT JOIN paiement v on v.credit_id = cr.id
                WHERE cr.client_id = ?
                GROUP BY cr.id
            """
            cursor.execute(query, (client_id,))
            return cursor.fetchall()

    def regle_credit(self, credit_id, client_id):
        """
        Settles a credit by marking it as fully paid.

        This method retrieves the remaining amount ('reste') for a given credit.
        If the credit is already settled or not found, it returns an error.
        Otherwise, it records a full payment in the 'paiement' table, updates the credit's status to 'terminé',
        and sets the remaining amount to zero.

        Args:
            credit_id (int): The ID of the credit to settle.
            client_id (int): The ID of the client making the payment.

        Returns:
            dict: A dictionary containing the result of the operation.
                - If successful: {'success': True, 'message': 'Crédit réglé avec succès.'}
                - If failed: {'success': False, 'error': <error_message>}
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT reste FROM credit WHERE id = ?", (credit_id,))
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'error': 'Credit Introuvable'}
            reste = row[0]
            if reste <= 0:
                return {'success': False, 'error': 'Le crédit est déjà réglé ou terminé.'}
            try:
                cursor.execute('BEGIN')
                # Add Full Versement
                date = datetime.now().strftime("%d-%m-%Y")
                cursor.execute(
                    """INSERT INTO paiement(credit_id, client_id, date_versement, montant, observation)
                       VALUES (?, ?, ?, ?, ?)""",
                    (credit_id, client_id, date, reste, "")
                )
                # Update Credit Status
                cursor.execute(
                    "UPDATE credit SET reste = 0, statut = 'terminé' WHERE id = ?",
                    (credit_id,)
                )
                conn.commit()
                return {'success': True, 'message': 'Crédit réglé avec succès.'}
            except sqlite3.Error as e:
                conn.rollback()
                return {'success': False, 'error': str(e)}

    def update_credit(self, client_id, column, text, reste):
        """
        Updates a specific field of a credit record in the database for a given client.

        Args:
            client_id (int): The ID of the client whose credit record is to be updated.
            column (int): The column identifier to update:
                1 - date_credit
                3 - motif
                4 - montant
                (Other values are considered invalid or not updatable.)
            text (Any): The new value to set for the specified column.
            reste (float): The remaining amount, used for validation when updating 'montant'.

        Returns:
            dict: A dictionary containing the result of the operation:
                - 'success' (bool): True if the update was successful, False otherwise.
                - 'message' (str, optional): Success message if the update was successful.
                - 'error' (str, optional): Error message if the update failed.

        Notes:
            - Only columns with identifiers 1 (date_credit), 3 (motif), and 4 (montant) can be updated.
            - When updating 'montant', the new value must be greater than zero and greater than or equal to 'reste'.
            - Other columns or invalid identifiers will result in an error.

        """
        with self.connect() as conn:
            cursor = conn.cursor()
            if column in (2, 5, 6, 7):
                # Montant, Motif, Date
                return {'success': False, 'error': 'Modification non autorisée pour cette colonne.'}
            elif column == 1:   # Date
                cursor.execute("UPDATE credit SET date_credit = ? WHERE id = ?", (text, client_id))
                message = 'Date mis à jour avec succès.'
            elif column == 3:   # motif
                cursor.execute("UPDATE credit SET motif = ? WHERE id = ?", (text, client_id))
                message = 'Motif mis à jour avec succès.'
            elif column == 4:   # montant
                # FIXME:  check if versement is lower than the montant
                # FIXME:  check if status is 'en cours'

                if text <= 0:
                    return {'success': False, 'error': 'Montant doit être supérieur à zéro.'}
                elif text < reste:
                    return {'success': False, 'error': 'Montant doit être supérieur ou égal au reste.'}

                cursor.execute("UPDATE credit SET montant = ? WHERE id = ?", ("{:.2f}".format(text), client_id))
                message = 'Montant mis à jour avec succès.'
            else:
                # invalid colonne
                return {'success': False, 'error': 'Colonne invalide.'}
            conn.commit()
            return {'success': True, 'message': message}

    # ====================================
    # === PAYMENTS(VERSEMENT) METHODES ===
    # ====================================
    def get_credit_versements(self, credit_id):
        """
        Retrieve all versements (payments) associated with a specific credit.

        Args:
            credit_id (int): The unique identifier of the credit.

        Returns:
            list of tuple: A list of tuples, each containing the payment's id, date_versement,
            montant (amount), and observation.

        Raises:
            sqlite3.DatabaseError: If a database error occurs during the query.
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT id, date_versement, montant, observation
                    FROM paiement WHERE credit_id = ?
                """,
                (credit_id,)
            )
            return cursor.fetchall()

    def insert_new_versement(self, credit_id, client_id, date_versement, montant, observation=""):
        """
        Inserts a new versement (payment) record into the database for a given credit and client.

        This method performs the following actions:
        1. Inserts a new payment into the 'paiement' table.
        2. Updates the remaining balance ('reste') in the 'credit' table by subtracting the payment amount.
        3. If the remaining balance is less than or equal to zero, marks the credit as "terminé" (finished).
        4. Commits the transaction if successful; rolls back if an error occurs.

        Args:
            credit_id (int): The ID of the credit to which the payment is associated.
            client_id (int): The ID of the client making the payment.
            date_versement (str): The date of the payment (format: 'YYYY-MM-DD').
            montant (float): The amount of the payment.
            observation (str, optional): Additional notes or observations about the payment. Defaults to "".

        Returns:
            dict: A dictionary containing:
                - 'success' (bool): True if the operation was successful, False otherwise.
                - 'versement_id' (int, optional): The ID of the newly inserted payment (if successful).
                - 'error' (str, optional): Error message (if unsuccessful).
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO paiement(credit_id, client_id, date_versement, montant, observation)
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (credit_id, client_id, date_versement, montant, observation)
                )
                # Update remaining balance
                cursor.execute(
                    "UPDATE credit SET reste = reste - ?  WHERE id = ?",
                    (montant, credit_id)
                )
                # If reste <= 0 => mark as "terminé"
                cursor.execute(
                    "UPDATE credit SET statut = 'terminé' WHERE id = ? AND reste <= 0",
                    (credit_id,)
                )
                conn.commit()
                return {'success': True, 'versement_id': cursor.lastrowid}
            except sqlite3.Error as e:
                conn.rollback()
                return {'success': False, 'error': str(e)}

    def delete_paiement(self, paiement_id):
        with self.connect() as conn:
            cursor = conn.cursor()

            # 1. Get montant and credit_id
            cursor.execute('SELECT montant, credit_id FROM paiement WHERE id = ?', (paiement_id,))
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'message': "❌ Versement introuvable."}

            montant, credit_id = row

            try:
                cursor.execute('BEGIN')
                # 2. Delete the versement
                cursor.execute('DELETE FROM paiement WHERE id = ?', (paiement_id,))
                # 3. Add back the montant to credit.reste
                cursor.execute('UPDATE credit SET reste = reste + ?  WHERE id = ?', (montant, credit_id))
                # 4. If credit was terminé, set it to en cours
                cursor.execute("UPDATE credit SET statut = 'en cours' WHERE id = ? AND reste > 0", (credit_id,))

                conn.commit()
                return {'success': True, 'message': "✅ Versement supprimé avec succès."}
            except Exception as e:
                conn.rollback()
                return {'success': False, 'message': f"❌ Erreur : {str(e)}"}

    # ======================
    # === Charge Methods ===
    # ======================
    def sum_charges(self, month=None):
        query = "SELECT IFNULL(SUM(montant), 0) AS total_charges FROM charges"
        params = ()
        if month:
            query += " WHERE strftime('%Y-%m', date_charge) = ?"
            params = (month, )

        with self.connect() as conn:
            cursor = conn.cursor()
            result = self.fetch_namedtuple(cursor, query, params=params)
            return result[0] if result else 0

    def dump_charges(self, month):
        query = f"""
        SELECT {", ".join(self.charge_fields)} FROM charges ch
        LEFT JOIN employes emp ON emp.id = ch.effectue_par
        WHERE strftime('%Y-%m', ch.date_charge) = ?
        ORDER BY ch.date_charge DESC
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (month, ))
            return cursor.fetchall()

    def search_charge(self, search_word, month):
        with self.connect() as conn:
            cursor = conn.cursor()

            query = f"""
                SELECT {", ".join(self.charge_fields)}
                FROM charges ch
                LEFT JOIN employes emp ON emp.id = ch.effectue_par
            """
            conditions = []
            params = []

            # Add search conditions if a word is provided
            if search_word:
                conditions.append("(emp.nom LIKE ? OR ch.motif LIKE ? OR ch.date_charge LIKE ?)")
                params.extend([f"%{search_word}%"] * 3)

            # Add month condition if not "Tous"
            if month != "Tous":
                conditions.append("strftime('%Y-%m', ch.date_charge) = ?")
                params.append(month)

            # Add WHERE if there are conditions
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY ch.date_charge DESC"

            cursor.execute(query, params)
            return cursor.fetchall()

    def get_charge_by_id(self, charge_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM charges WHERE id = ?"
            result = self.fetch_namedtuple(cursor, query, (charge_id,), "Charge")
            # result is a list of Charge namedtuples
            return result[0] if result else None

    def insert_new_charge(self, date_charge, effectue_par, montant, motif):
        """
        Insert a new charge into the database.
        """
        employe_id = self.get_item_id('employes', 'nom', effectue_par)
        with self.connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO charges (date_charge, effectue_par, montant, motif) VALUES (?, ?, ?, ?)",
                    (date_charge, employe_id, str(montant), motif)
                )
                conn.commit()
                return {'success': True, 'message': "Charge ajoutée avec succès."}
            except sqlite3.Error as e:
                conn.rollback()
                return {'success': False, 'error': str(e)}

    def update_charge_values(self, charge_id, date, effectue_par, montant, motif):
        with self.connect() as conn:
            cursor = conn.cursor()
            query = "UPDATE charges set date_charge = ?, effectue_par = ?, montant = ?, motif = ? WHERE id = ?"
            employe_id = self.get_item_id('employes', 'nom', effectue_par)
            try:
                cursor.execute(query, (date, employe_id, str(montant), motif, charge_id))
                conn.commit()
                return {'success': True, 'message': 'Charge mise à jour avec succès.'}
            except sqlite3.Error as e:
                conn.rollback()
                return {'success': False, 'error': str(e)}

    def update_charge(self, charge_id, column, new_text):
        """
        Update an employe field in the database.
        :emp_id: ID of the employe
        :col: Column to update (e.g., 'nom', 'telephone', 'poste', 'observation')
        :text: New value for the column
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            # Date
            if column == 1:
                cursor.execute("UPDATE charges SET date_charge = ? WHERE id = ?", (new_text, charge_id))
                message = 'Date mis à jour avec succès.'
            # Effectue par
            elif column == 2:
                return {'success': False, 'error': 'Modification de l\'employé non autorisée.'}
            # Montant
            elif column == 3:
                cursor.execute("UPDATE charges SET montant = ? WHERE id = ?", (new_text, charge_id))
                message = 'Montant mis à jour avec succès.'
            # Motif
            elif column == 4:
                cursor.execute("UPDATE charges SET motif = ? WHERE id = ?", (new_text, charge_id))
                message = 'Motif mis à jour avec succès.'
            else:
                return {'success': False, 'error': 'Colonne invalide.'}

            conn.commit()
            return {'success': True, 'message': message}

    def close(self):
        with self.connect() as conn:
            conn.close()


if __name__ == '__main__':
    db = Database()

    result = db.get_sums_operations('2024-08')
    print(result)
    # CREATE DATABASE
    # result = db_handler.create_tables()

    # ADD Emplye | Client
    # from datetime import datetime
    # today = datetime.now().date()
    # result = db.insert_new_employe('Ibrahim', 'Magasinier', '', 40000, today)
    # result = db.insert_new_client('SUP Elmara3i', '0556000000', '')
    # print(result)
    # =======================
    # Dump Emplyes | Clients
    # rows = db.dump_employes()
    # rows = db.dump_clients()
    # print(rows)

    # ===========
    # ADD CREDIT
    # result = db_handler.ajouter_credit(1, '1500', 'Avance')

    # ADD VERSEMENT
    # result = db_handler.ajouter_versement(1, '200')

    # Get Persones Names
    # result = db_handler.persone_names()

    # result = db_handler.get_total_credit()

    # Get CLIENT CREDITES
    # result = db_handler.get_client_credits(1)
    # print(f"Credit for client :ibrahim: {result}")
    # result = db_handler.get_credit_versements(1)
    # print(f"Versement: {result}")

    # Calculate salarie
    # result = db.calculate_salaire_mensuel('2024-08', 1)
    # print(result)
