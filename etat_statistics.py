#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------
import pandas as pd
from logger import logger


def load_excel(file_path, sheet_name):
    """
    Load an Excel sheet and clean its data.

    The function:
    - Reads all sheets from an Excel file
    - Selects the requested sheet
    - Converts the DATE column to datetime
    - Converts numeric columns to proper numeric types
    - Removes rows without a valid DATE (e.g. subtotal rows)

    Parameters
    ----------
    file_path   : Path to the Excel file.
    sheet_name  :  Name of the sheet to load.

    Returns
    -------
    pandas.DataFrame: Cleaned DataFrame with valid dates and numeric values.
    str             : Error message if the file or sheet cannot be loaded.
    None            : If the DATE column cannot be processed.
    """
    try:
        # sheets = pd.read_excel(file_path, sheet_name=None, usecols="A:H", nrows=243)
        sheets = pd.read_excel(file_path, sheet_name=None, nrows=243)
        df = sheets[sheet_name]     # Select the requested sheet
    except Exception as err:
        logger.error(f"Load Excel File: {err}")
        return None

    # --- Clean DATE column ---
    try:
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    except Exception as err:
        logger.error(f"Load Excel File: {err}")
        return None

    # --- Convert numeric columns ---
    numeric_columns = [
        "T. COMMANDE",
        "T.LOGICIEL",
        "VERSEMENT",
        "CHARGE",
        "DIFF",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove rows without a valid DATE (e.g. subtotal / footer rows)
    clean_df = df[df["DATE"].notna()]
    return clean_df


# ==========================================
# --- Day Details
# ==========================================
def show_day_details(clean_df, day, fields):
    """
    Show details for a specific day
    :clean_df: DataFrame
    :day: str or datetime [YYYY-MM-DD]
    :fields: list of fields to sum
    """
    daily_details = clean_df.groupby(["DATE", "LIVREUR"])[fields].sum()
    daily_details = daily_details.sort_values(by="T.LOGICIEL", ascending=False)

    daily_details["OBSERVATION"] = daily_details["OBSERVATION"].astype("string")
    # Convert input to datetime
    day = pd.to_datetime(day).normalize()

    if day in daily_details.index.get_level_values("DATE"):
        return daily_details.loc[day].reset_index()
    else:
        return "No data"


# ==========================================
# --- Etat jouralier
# ==========================================
def etat_journalier(clean_df, fields):
    """
    Total par jour avec ligne des totaux
    :clean_df: clean by date
    :fields: list of fields to sum
    """
    # --- SUM By Date
    daily_stats = clean_df.groupby("DATE")[fields[:-1]].sum()       # without observation
    daily_stats = daily_stats.sort_values(by="DATE", ascending=True)
    daily_stats.index = daily_stats.index.date  # Convert to date only

    # Create totals row
    total_row = pd.DataFrame(daily_stats.sum()).T
    total_row.index = ["TOTAL"]
    # Append totals inside table
    etat_journalier = pd.concat([daily_stats, total_row])
    return etat_journalier.reset_index()


# ==========================================
# --- Livreur
# ==========================================
def sum_by_driver(clean_df, fields):
    """
    ETAT TOTAL BY LIVREUR
    clean_df: DataFrame
    fields: list of fields to sum
    """
    # --- TOTAL PAR LIVREUR SUMMARY ---
    # driver_stats = clean_df.groupby("LIVREUR", as_index=False)[fields].sum()      # as_index=False == reset_index()
    driver_stats = clean_df.groupby("LIVREUR")[fields].sum()
    driver_stats = driver_stats.sort_values(by="VERSEMENT", ascending=False)
    return driver_stats.reset_index()


def etat_excel_like_db(clean_df):
    """
    this function return
    ["ACCOMTE", "CREDIT", "VERSEMENT CREDIT", "CHARGE"] to display in QLabel Excel Etat
    """
    charges = clean_df.groupby(["DATE"])[["CHARGE"]].sum()
    charges = charges["CHARGE"].sum()

    # --- Sum VERSEMENT by LIVREUR ---
    vers_by_livreur = clean_df.groupby("LIVREUR", as_index=False)["VERSEMENT"].sum()
    livreur = vers_by_livreur[vers_by_livreur["LIVREUR"].isin(["ACCOMPTE", "CREDIT", "VERS. CREDIT"])]
    livreur = livreur.set_index("LIVREUR")
    # Extract values safely
    etat_excel = {
        "ACCOMPTE": float(livreur["VERSEMENT"].get("ACCOMPTE", 0)),
        "CREDIT": float(livreur["VERSEMENT"].get("CREDIT", 0)),
        "VERS. CREDIT": float(livreur["VERSEMENT"].get("VERS. CREDIT", 0)),
        "CHARGES": float(charges),
    }
    return etat_excel


# ==========================================
# --- Ploting LIVREUR Purentage
# ==========================================
def plot_driver_percentages(canvas, clean_df, fields):
    import matplotlib.pyplot as plt
    ax = canvas.ax
    ax.clear()

    # Filter drivers & create a real copy => removes warnings
    livreur = ["AMINE", "TOUFIK", "REDA", "MOHAMED"]
    driver_stats = clean_df.groupby("LIVREUR")[fields].sum()
    driver_stats = driver_stats.sort_values(by="VERSEMENT", ascending=True).reset_index()
    df = driver_stats[driver_stats["LIVREUR"].isin(livreur)].copy()

    # Percentages based on VERSEMENT
    total_livraison = df["VERSEMENT"].sum()
    df["LIVRAISON %"] = (df["VERSEMENT"] / total_livraison) * 100

    # Plot
    bars = plt.bar(df["LIVREUR"], df["LIVRAISON %"])

    # Increase bottom margin for money text
    plt.subplots_adjust(bottom=0.18)

    # Add labels
    for bar, pct, amount in zip(bars, df["LIVRAISON %"], df["VERSEMENT"]):
        x = bar.get_x() + bar.get_width() / 2

        # % above bar
        plt.text(
            x, bar.get_height(),
            f"{pct:.1f}%",
            ha='center', va='bottom', fontsize=11
        )

        # Money BELOW the x-axis labels
        plt.text(
            x, -5,  # lower value = lower under the name
            f"{amount:,.0f} DA",
            ha='center', va='top', fontsize=10
        )

    plt.title("LIVRAISON (%) par LIVREUR", fontsize=14)
    plt.ylabel("Pourcentage (%)")
    plt.xlabel("LIVREUR")
    plt.xticks(rotation=0)

    # Make sure we have space below
    plt.ylim(-10, df["LIVRAISON %"].max() + 10)

    plt.tight_layout()
    plt.show()


def plot_driver_percentages_pyqt(canvas, df, allowed_livreur, fields, metric):
    ax = canvas.ax
    ax.clear()

    # Drivers to keep
    driver_stats = df.groupby("LIVREUR")[fields].sum()
    driver_stats = driver_stats.sort_values(by=metric, ascending=True).reset_index()
    df = driver_stats[driver_stats["LIVREUR"].isin(allowed_livreur)].copy()

    # If all values empty or df empty → display message
    if df.empty or df[metric].isna().all():
        ax.text(0.5, 0.5, "Aucune donnée disponible",
                ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        canvas.draw()
        return

    # Replace NaN by 0
    df[metric] = df[metric].fillna(0)

    total = df[metric].sum()
    if total == 0:
        ax.text(0.5, 0.5, f"{metric} = 0 pour tous les livreurs",
                ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        canvas.draw()
        return

    pct_col = f"{metric} %"
    df[pct_col] = (df[metric] / total) * 100

    # Bar chart
    bars = ax.bar(df["LIVREUR"], df[pct_col])

    ax.set_title(f"{metric} (%) par LIVREUR")
    # ax.set_ylabel("Pourcentage (%)")
    # ax.set_xlabel("LIVREUR")

    # Add labels
    for bar, pct, amount in zip(bars, df[pct_col], df[metric]):
        x = bar.get_x() + bar.get_width() / 2

        ax.text(x, bar.get_height(), f"{pct:.1f}%",
                ha="center", va="bottom", fontsize=10)

        ax.text(x, -5, f"{amount:,.0f}",
                ha="center", va="top", fontsize=9)

    # Safe Y limit
    ymax = df[pct_col].max()
    if pd.isna(ymax) or ymax == 0:
        ymax = 10

    ax.set_ylim(-10, ymax + 10)

    canvas.fig.subplots_adjust(bottom=0.22)
    canvas.draw()


# ==========================================
# --- Livreur Obs
# ==========================================
def driver_observations(clean_df):
    """
    Generate observations for each driver based on their performance.
    :clean_df: DataFrame
    """
    driver_obs = clean_df.groupby(["LIVREUR"])["OBSERVATION"].sum()
    return driver_obs.reset_index()


# ==========================================
# --- Retour Livreur
# ==========================================
def driver_retour(clean_df):
    """
    Calculate the difference between 'T. COMMANDE' and 'T.LOGICIEL'
    and return detailed rows + sum grouped by livreur.
    """
    df = clean_df.copy()
    df["RETOUR"] = df["T. COMMANDE"] - df["T.LOGICIEL"]

    retour = df[["DATE", "LIVREUR", "T. COMMANDE", "T.LOGICIEL", "RETOUR"]].dropna().copy()
    # Format DATE
    retour["DATE"] = retour["DATE"].dt.strftime("%d/%m/%Y")

    # === TOTAL ROW ===
    total_row = {
        "DATE": "",
        "LIVREUR": "TOTAL",
        "T. COMMANDE": retour["T. COMMANDE"].sum(),
        "T.LOGICIEL": retour["T.LOGICIEL"].sum(),
        "RETOUR": retour["RETOUR"].sum(),
    }

    # Append total row
    retour = pd.concat([retour, pd.DataFrame([total_row])], ignore_index=True)

    sum_retour_by_driver = (
        retour.groupby("LIVREUR")["RETOUR"]
        .sum()
        .reset_index()
    )

    return retour, sum_retour_by_driver


def plot_driver_retour_pyqt(canvas, clean_df, allowed_livreur):
    ax = canvas.ax
    ax.clear()

    # Filter only allowed drivers
    df = clean_df.copy()
    df = df[df["LIVREUR"].isin(allowed_livreur)].copy()

    # If empty → avoid crash
    if df.empty:
        canvas.ax.text(0.5, 0.5, "Aucune donnée", ha='center')
        canvas.draw()
        return

    # Compute percentages
    total_retour = df["RETOUR"].sum()

    if total_retour == 0:
        canvas.axes.text(0.5, 0.5, "Total Retour = 0", ha='center')
        canvas.draw()
        return

    df["RETOUR %"] = df["RETOUR"] / total_retour * 100

    # Plot
    bars = canvas.ax.bar(df["LIVREUR"], df["RETOUR %"])

    # Add labels
    for bar, pct, amount in zip(bars, df["RETOUR %"], df["RETOUR"]):
        x = bar.get_x() + bar.get_width() / 2

        # percentage
        canvas.ax.text(x, bar.get_height(), f"{pct:.1f}%", ha="center", va="bottom", fontsize=11)

        # absolute amount under x-axis
        canvas.ax.text(x, -5, f"{amount:,.0f} DA", ha="center", va="top", fontsize=10)

    # Formatting
    canvas.ax.set_title("RETOURS (%) par LIVREUR")
    # canvas.ax.set_ylabel("Pourcentage (%)")
    # canvas.ax.set_xlabel("LIVREUR")

    # Good margin for under-money text
    canvas.ax.set_ylim(-10, df["RETOUR %"].max() + 10)

    canvas.draw()


# ==========================================
# --- The terminal logger
# ==========================================
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


def reminder(file_name):
    df = pd.read_excel(file_name, sheet_name="DECEMBRE")
    divider = "-" * 30
    # ----
    # print("[+] Head: ")
    # print(df.head())
    # # ---
    # print("[+] Tail: ")
    # print(df.tail(3))
    # ---
    print("[+] Info: ")
    print(df.info())
    # ---
    print("[+] Dtypes: ")
    print(df.dtypes)
    # ---
    print("[+] Description: ")
    print(df.describe(include='all'))
    # ---
    print("[+] Columns: ")
    print(df.columns)
    # ---
    print("[+] Index: ")
    print(df.index)
    print(divider)
    # ----------------------------------------
    # --- Selecting Data
    print("[+] Dates: ")
    print(df["DATE"].unique())
    print("[+] A Given Day: ")
    print(df[df["DATE"] == "2025-12-04"])
    print(divider)
    # --- Filtering
    print("[+] Commande = 0")
    print(df[df["T. COMMANDE"].isna() | (df["T. COMMANDE"] == 0)].head(4))
    print(divider)
    # ---
    print("[+] Livreur is in [AMINE, TOUFIK]")
    print(df[df["LIVREUR"].isin(["AMINE", "TOUFIK"])].head(4))
    print(divider)
    # ----------------------------------------
    # --- Drop Duplicates
    print("[+] Drop Duplicates based on DATE & LIVREUR")
    df_no_dup = df.drop_duplicates(subset=["LIVREUR"])
    print(df_no_dup.head(4))
    print(divider)
    # --- Drop Null on Values
    df_date_clean = df[df["DATE"].notna()]
    print("[+] Drop Null based on DATE")
    print(df_date_clean.head(10))

    # --- Stats
    print(divider)
    print("[+] Group by LIVREUR and sum VERSEMENT")
    driver_stats = df_date_clean.groupby("LIVREUR")["VERSEMENT"].sum().reset_index()
    print(driver_stats)
    print(divider)
    print("[+] Filter LIVREUR in [ACCOMPTE, CREDIT, VERS. CREDIT]")
    print(driver_stats[driver_stats["LIVREUR"].isin(["ACCOMPTE", "CREDIT", "VERS. CREDIT"])])
    print(divider)


# ==========================================
# --- Mohamed Functions
# ==========================================
def achat_mohamed(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=2, usecols="A:I")
    clean_df = df[~df["Prix achat"].astype(str).str.contains("TOTAL", na=False)]
    clean_df = clean_df.dropna(subset=["Nom"])
    cols = ["Qte Carton", "Collisage", "Qte (Pièce)", "Qte Global", "Prix achat", "Total", "REMISE 2%", "TOTAL AVEC REMISE"]
    for col in cols:
        clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")

    cols_to_use = ["Nom", "Qte Global", "Prix achat", "Total"]
    clean_df = clean_df.loc[:, cols_to_use]
    recape = clean_df.groupby("Nom", as_index=False).agg({
        "Qte Global": "sum",
        "Prix achat": "first",
        "Total": "sum",
    })
    # recape["Total Achat"] = recape["Qte Global"] * recape["Prix achat"]
    # TODO: Add Remise
    # Save to Excel
    output_file = f"C:\\Users\\ADMIN\\OneDrive\\Desktop\\ADMIN\\achat_mohamed_recape_{sheet_name}.xlsx"
    recape.to_excel(output_file, index=False)
    print(f"Saving Achat Mohamed recap to: {output_file}")
    return recape


def categorize(des):
    d = des.lower()

    # --- Linge 1.5L ---
    if d.startswith("linge 1.5l"):
        if d.startswith("linge 1.5l bebe"): return "Linge 1.5L Bebe"
        elif d.startswith("linge 1.5l bicarbonate"): return "Linge 1.5L Bicarbonate"
        else: return "Linge 1.5L"
    # --- Linge 3L ---
    elif d.startswith("linge 3l"):
        if d.startswith("linge 3l plus"): return "Linge 3L Plus"
        elif d.startswith("linge 3l noir"): return "Linge 3L Noir"
        elif d.startswith("linge 3l bebe"): return "Linge 3L Bebe"
        elif d.startswith("linge 3l anti - bacterien"): return "Linge 3L Anti-Bacterien"
        else: return "Linge 3L"
    # --- Linge 4.5L ---
    elif d.startswith("linge 4.5l"): return "Linge 4.5L"
    # --- Linge 10L ---
    elif d.startswith("linge 10l"): return "Linge 10L"
    # --- Assouplissant ---
    elif d.startswith("assouplissant 1l"): return "Assouplissant 1L"
    elif d.startswith("assouplissant 3l"): return "Assouplissant 3L"
    # --- Lave-Sol ---
    elif d.startswith("lave sol"): return "Lave Sole"
    # --- Sanibon ---
    elif d.startswith("désodorisant"): return "Sanibon"
    # --- Lave-Main 2.5L ---
    elif d.startswith("lave main 2.5l"): return "Lave main 2.5L"
    # --- Lave-Main 400ML ---
    elif d.startswith("lave main 400ml"): return "Lave main 400ML"
    # --- Javel 5L ---
    elif d.startswith("javel 5l"): return "Javel 5L"
    # --- Diffusseur ---
    elif d.startswith("diffuseur"): return "Diffuseur de Parfum"
    elif d.startswith("brume"): return "Brume"
    elif d.startswith("gel douche"): return "Gel Douche"
    else: return des


def recapepdf_to_text(pdf_file):
    import pdfplumber
    # path = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\FICHE CHARGEMEN\\12-DECEMBRE\\MOH-17.pdf"

    # ---- 1. Extract all tables from all pages ----
    tables = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                for t in page.extract_tables():
                    df = pd.DataFrame(t)
                    tables.append(df)
    except FileNotFoundError:
        logger.error(f"PDF File not found: {pdf_file}")
        return None

    # ---- 2. Clean header for each table ----
    clean_tables = []
    for df in tables:
        df.columns = df.iloc[0]   # first row = header
        df = df[1:]               # remove header row
        clean_tables.append(df)

    # ---- 3. Merge all pages into one table ----
    df = pd.concat(clean_tables, ignore_index=True)

    # ---- 4. Clean quantities ----
    df["Qnt_piece"] = (
        df["Qnt pièce"]
        .str.replace(",", ".", regex=False)
    )

    df = df[df["Qnt_piece"].str.match(r"^\d+(\.\d+)?$")]
    df["Qnt_piece"] = df["Qnt_piece"].astype(float)

    # --- GROUPING LOGIC ---
    df["Category"] = df["Désignation"].apply(categorize)

    # ---- 6. Final grouped result ----
    result = (
        df.groupby("Category", as_index=False)["Qnt_piece"]
        .sum()
        .sort_values("Category")
    )
    return result


if __name__ == "__main__":
    # file = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\ADMIN\\VERSEMENT_LIVREUR.xlsx"
    # file = "~/Desktop/ADMIN/VERSEMENT_LIVREUR.xlsx"

    # fields = ["T. COMMANDE", "T.LOGICIEL", "VERSEMENT", "CHARGE", "DIFF", "OBSERVATION"]
    # sheet_name = "DECEMBRE"
    # df = load_excel(file, sheet_name)
    # terminal(sheet, fields)
    # print(les_retour)
    # print(sum_retour)
    # driver_stats = sum_by_driver(sheet, fields)
    # print(driver_stats)
    # plot_driver_percentages(sheet, fields)

    # --- Etat Excel Like DB
    # print(etat_excel_like_db(df))
    # Reminder
    # reminder(file)
    # ---------------------------------------------------
    # ----------- Achat Mohamed ----------------
    # ---------------------------------------------------
    # file_path = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\ADMIN\\ACHAT_MOHAMED_2025.xlsx"
    # achat_mohamed = achat_mohamed(file_path, "DECEMBRE")
    # print(achat_mohamed.head(20))
    # print('-' * 30)
    # print(achat_mohamed.tail(20))
    # -------------------------------------------------
    # PDF CHARGEMENT RECAPE MOHAMED
    # -----------------------------
    pdf_file_path = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\FICHE CHARGEMEN\\01-JANVIER\\MOH-17.pdf"
    # pdf_file_path = "/home/dabve/Desktop/FICHE_CHARGEMENT_18-12-2025.pdf"
    pdf_recape = recapepdf_to_text(pdf_file_path)
    if pdf_recape is not None:
        print("Recape Journee Mohamed: ")
        print(pdf_recape)
        print(f"\n==== Total Article: {len(pdf_recape)} =====")
