#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------
import pandas as pd


def load_excel(file_path, sheet_name):
    """
    This will return converted numeric values
    """
    import pandas as pd
    dfs = pd.read_excel(file_path, sheet_name=None)
    sheet = dfs[sheet_name]
    # --- Clean DATE column ---
    sheet["DATE"] = pd.to_datetime(sheet["DATE"], errors="coerce")

    # --- Numeric columns ---
    fields = ["T. COMMANDE", "T.LOGICIEL", "VERSEMENT", "CHARGE", "DIFF"]

    for col in fields:
        # to numeric
        sheet[col] = pd.to_numeric(sheet[col], errors="coerce")

    clean_df = sheet[sheet["DATE"].notna()]     # clean by date to remove the SUBTOTAL rows
    return clean_df


def show_day_details(clean_df, day, fields):
    """
    Show details for a specific day
    :clean_df: DataFrame
    :day: str or datetime [YYYY-MM-DD]
    :fields: list of fields to sum
    """
    daily_driver = clean_df.groupby(["DATE", "LIVREUR"])[fields].sum()   # print(f"📅 Today's stats: {today_stats}\n")

    # Convert input to datetime
    day = pd.to_datetime(day).normalize()

    if day in daily_driver.index.get_level_values("DATE"):
        return daily_driver.loc[day].reset_index()
    else:
        return f"No data for {day.date()}"


def etat_journalier(clean_df, fields):
    """
    Total par jour avec ligne des totaux
    :clean_df: clean by date
    :fields: list of fields to sum
    """
    # --- SUM By Date
    daily_stats = clean_df.groupby("DATE")[fields[:-1]].sum()
    daily_stats = daily_stats.sort_values(by="DATE", ascending=True)

    # Create totals row
    total_row = pd.DataFrame(daily_stats.sum()).T
    total_row.index = ["TOTAL"]
    # Append totals inside table
    etat_journalier = pd.concat([daily_stats, total_row])
    return etat_journalier.reset_index()


def sum_by_driver(clean_df, fields):
    """
    Sum by driver
    clean_df: DataFrame
    fields: list of fields to sum
    """
    # --- TOTAL PAR LIVREUR SUMMARY ---
    driver_stats = clean_df.groupby("LIVREUR")[fields].sum()
    driver_stats = driver_stats.sort_values(by="T. COMMANDE", ascending=False)
    return driver_stats.reset_index()


def driver_observations(clean_df):
    """
    Generate observations for each driver based on their performance.
    :clean_df: DataFrame
    """
    driver_obs = clean_df.groupby(["LIVREUR", "DATE"])["OBSERVATION"].sum()
    return driver_obs.reset_index()


def difference_commande_logiciel(df):
    """
    Calculate the difference between 'T. COMMANDE' and 'T.LOGICIEL' for each row.
    :df: DataFrame
    """
    df["RETOUR"] = df["T. COMMANDE"] - df["T.LOGICIEL"]
    les_retour = df[["DATE", "LIVREUR", "T. COMMANDE", "T.LOGICIEL", "RETOUR"]].dropna(subset=["RETOUR"])
    sum_retour_by_driver = les_retour.groupby("LIVREUR")["RETOUR"].sum().reset_index()
    return les_retour, sum_retour_by_driver


def terminal(clean_df, fields):
    """
    sheet_name: DECEMBRE
    """
    divider = "=" * 40
    # -----------------------------------------------------

    # --- Group by DATE and LIVREUR ---
    date = "2025-12-04"
    print(divider)
    print(f'🚚 Daily driver stats for {date}:')
    print(divider)
    print(show_day_details(clean_df, date, fields))                                      # unsorted

    # =======================================
    print(divider)
    print("📅 Etat Journalier:")
    print(divider)
    print(etat_journalier(clean_df, fields))
    # =======================================
    print(divider)
    print("🚚 Total Par Livreur:")
    print(divider)
    print(sum_by_driver(clean_df, fields))
    # =======================================
    print(divider)
    print("🚚 Livreur Observation:")
    print(divider)
    print(driver_observations(clean_df))


if __name__ == "__main__":
    file = "~/Desktop/OneDrive_1_12-4-2025/ADMIN/VERSEMENT_LIVREUR_AOUT.xlsx"

        # return pd.read_excel(file_path, sheet_name=None)

    # print(show_day_details(clean_df, "2025-12-04", fields))
    fields = ["T. COMMANDE", "T.LOGICIEL", "VERSEMENT", "CHARGE", "DIFF", "OBSERVATION"]
    sheet_name = "DECEMBRE"
    sheet = load_excel(file, sheet_name)
    # terminal(sheet, fields)
    les_retour, sum_retour = difference_commande_logiciel(sheet)
    print(les_retour)
    print(sum_retour)
