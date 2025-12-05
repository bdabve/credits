#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------
import pandas as pd


def cleaned_data(sheet_df):
    # --- Clean DATE column ---
    sheet_df["DATE"] = pd.to_datetime(sheet_df["DATE"], errors="coerce")

    # --- Numeric columns ---
    fields = ["T. COMMANDE", "T.LOGICIEL", "VERSEMENT", "CHARGE", "DIFF", "Observation"]

    for col in fields:
        # to numeric
        sheet_df[col] = pd.to_numeric(sheet_df[col], errors="coerce")

    clean_df = sheet_df[sheet_df["DATE"].notna()]
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
        return daily_driver.loc[day]
    else:
        return f"No data for {day.date()}"


def etat_journalier(clean_df, fields):
    """
    Total par jour avec ligne des totaux
    :clean_df: clean by date
    :fields: list of fields to sum
    """
    # --- SUM By Date
    daily_stats = clean_df.groupby("DATE")[fields].sum()
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


def terminal(sheet_df, fields):
    """
    sheet_name: DECEMBRE
    """
    clean_df = sheet_df[sheet_df["DATE"].notna()]
    divider = "=" * 40
    # -----------------------------------------------------

    # --- Group by DATE and LIVREUR ---
    # print(f'🚚 Daily driver stats All Data: \n{divider}\n{daily_driver}')

    date = "2025-12-04"
    print(divider)
    print(f'🚚 Daily driver stats for {date}:')
    print(divider)
    print(show_day_details(clean_df, date, fields))                                      # unsorted

    # Printing
    print(divider)
    print("📅 Etat Journalier:")
    print(divider)
    print(etat_journalier(clean_df, fields))

    # print(f"{divider}\n📊 TOTALS: \n{divider}")
    # print(" • Total commande :", daily_stats["T. COMMANDE"].sum())
    # print(" • Total logiciel :", daily_stats["T.LOGICIEL"].sum())
    # print(" • Total versement:", daily_stats["VERSEMENT"].sum())
    # print(" • Total charge   :", daily_stats["CHARGE"].sum())
    # print(" • Total diff     :", daily_stats["DIFF"].sum(), "\n")
    print(divider)
    print("🚚 Total Par Livreur:")
    print(divider)
    print(sum_by_driver(clean_df, fields))


def load_excel(file_path):
    import pandas as pd
    dfs = pd.read_excel(file_path, sheet_name=None)
    sheet = dfs["DECEMBRE"]
    # --- Clean DATE column ---
    sheet["DATE"] = pd.to_datetime(sheet["DATE"], errors="coerce")

    # --- Numeric columns ---
    fields = ["T. COMMANDE", "T.LOGICIEL", "VERSEMENT", "CHARGE", "DIFF", "OBSERVATION"]

    for col in fields:
        # to numeric
        sheet[col] = pd.to_numeric(sheet[col], errors="coerce")

    # clean_df = sheet[sheet["DATE"].notna()]
    return sheet, fields


if __name__ == "__main__":
    file = "../VERSEMENT_LIVREUR_AOUT.xlsx"

        # return pd.read_excel(file_path, sheet_name=None)

    # print(show_day_details(clean_df, "2025-12-04", fields))
    sheet, fields = load_excel(file)
    terminal(sheet, fields)
    # print(sum_by_driver(clean_df, fields))
