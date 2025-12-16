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
    try:
        dfs = pd.read_excel(file_path, sheet_name=None)
        sheet = dfs[sheet_name]
    except Exception as err:
        # no data for selected month
        return f"Error: {err}"
    else:
        # --- Clean DATE column ---
        sheet["DATE"] = pd.to_datetime(sheet["DATE"], errors="coerce")

        # --- Numeric columns ---
        fields = ["T. COMMANDE", "T.LOGICIEL", "VERSEMENT", "CHARGE", "DIFF"]

        for col in fields:
            # to numeric
            sheet[col] = pd.to_numeric(sheet[col], errors="coerce")

        clean_df = sheet[sheet["DATE"].notna()]     # clean by date to remove the SUBTOTAL rows
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
    daily_driver = clean_df.groupby(["DATE", "LIVREUR"])[fields].sum()

    # Convert input to datetime
    day = pd.to_datetime(day).normalize()

    if day in daily_driver.index.get_level_values("DATE"):
        return daily_driver.loc[day].reset_index()
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
    daily_stats = clean_df.groupby("DATE")[fields[:-1]].sum()
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
    Sum by driver
    clean_df: DataFrame
    fields: list of fields to sum
    """
    # --- TOTAL PAR LIVREUR SUMMARY ---
    driver_stats = clean_df.groupby("LIVREUR")[fields].sum()
    driver_stats = driver_stats.sort_values(by="T. COMMANDE", ascending=False)
    return driver_stats.reset_index()


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


if __name__ == "__main__":
    # file = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\ADMIN\\VERSEMENT_LIVREUR.xlsx"
    file = "~/Desktop/OneDrive_1_12-4-2025/ADMIN/VERSEMENT_LIVREUR_AOUT.xlsx"

    fields = ["T. COMMANDE", "T.LOGICIEL", "VERSEMENT", "CHARGE", "DIFF", "OBSERVATION"]
    sheet_name = "DECEMBRE"
    sheet = load_excel(file, sheet_name)
    # terminal(sheet, fields)
    # print(les_retour)
    # print(sum_retour)
    # driver_stats = sum_by_driver(sheet, fields)
    # print(driver_stats)
    # plot_driver_percentages(sheet, fields)

    # Reminder
    # reminder(file)
