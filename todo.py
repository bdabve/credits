#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------

"""
def etat_journalier(self):
    queries = {
        "accompte": "SELECT date, SUM(montant) FROM operations GROUP BY date",
        "credit": "SELECT date_credit, SUM(montant) FROM credit GROUP BY date_credit",
        "paiement": "SELECT date_versement, SUM(montant) FROM paiement GROUP BY date_versement",
        "charges": "SELECT date_charge, SUM(montant) FROM charges GROUP BY date_charge"
    }

    with self.connect() as conn:
        cursor = conn.cursor()

        daily = {}

        # Collect data from each query
        for key, query in queries.items():
            cursor.execute(query)
            rows = cursor.fetchall()     # (date, sum)

            for d, total in rows:
                if d not in daily:
                    daily[d] = {
                        "accompte": 0,
                        "credit": 0,
                        "paiement": 0,
                        "charges": 0
                    }
                daily[d][key] = total or 0

        # Sort dates
        sorted_dates = sorted(daily.keys())

        # Convert to list of rows (QTableWidget friendly)
        final_result = []

        for d in sorted_dates:
            row = [
                str(d),
                daily[d]["accompte"],
                daily[d]["credit"],
                daily[d]["paiement"],
                daily[d]["charges"]
            ]
            final_result.append(row)

        return final_result


def dump_payments(self, by_date=False):
    with self.connect() as conn:
        cursor = conn.cursor()
        if by_date:
            payments_fields = ["p.date_versement", "IFNULL(SUM(p.montant), 0)"]
            query = f\"\""
                SELECT {', '.join(payments_fields)}
                FROM paiement p
                GROUP BY p.date_versement
                ORDER BY p.id DESC
            \"\"\"
        else:
            query = f\"\""
                SELECT {', '.join(self.payments_fields)}
                FROM paiement p
                JOIN clients c ON p.client_id = c.id
                ORDER BY p.id DESC
            \"\""
        cursor.execute(query)
        return cursor.fetchall()
"""
