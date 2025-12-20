#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException
)

# ======================================================
# CONSTANTS
# ======================================================
BASE_URL = "http://51.255.79.241:8080/trizstock"
LOGIN_URL = f"{BASE_URL}/faces/login.xhtml"
VENTE_URL = f"{BASE_URL}/faces/view/vente/listDetailProduitSortie.xhtml"

DEFAULT_TIMEOUT = 20
DOWNLOAD_DIR = "triz_downloads"


# ======================================================
# DRIVER
# ======================================================
def create_driver(headless: bool = False):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=options, headless=headless)


# ---------- LOGIN ----------
def login(driver, username: str, password: str, timeout: int = DEFAULT_TIMEOUT):
    print("[+] Login...")
    wait = WebDriverWait(driver, timeout)
    driver.get(LOGIN_URL)

    user_input = wait.until(EC.presence_of_element_located((By.ID, "j_username")))
    pass_input = wait.until(EC.presence_of_element_located((By.ID, "j_password")))

    user_input.clear()
    user_input.send_keys(username)

    pass_input.clear()
    pass_input.send_keys(password + Keys.ENTER)
    # Check for error message
    try:
        error_message = wait.until(EC.presence_of_element_located((By.ID, "errorMessages")))
        error_message_text = error_message.find_element(By.CLASS_NAME, 'ui-messages-error-summary').text
        print(f"[✗] Login failed: {error_message_text}")
        return False
    except TimeoutException:
        print("[✓] Login successful.")
        return True


# ---------- DATA PARSING ----------
def parse_products_table(driver, product_list: list):
    """
    This parse the chargemen detail produit sortie
    :product_list: The list to populate with records
    """
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    table = wait.until(
        EC.presence_of_element_located((By.ID, "liste:j_idt613:dataTable2_data"))
    )

    for tr in table.find_elements(By.TAG_NAME, "tr"):
        tds = tr.find_elements(By.TAG_NAME, "td")

        if len(tds) < 10:
            continue

        product_list.append({
            "Famille": tds[0].text,
            "S.Famille": tds[2].text,
            "Produit": tds[3].text,
            "Qte Global": tds[7].text,
            "Total Valeur": tds[9].text
        })


# ----------# Prevendeur Etat #---------- #
def get_product_par_prevendeur(driver, dated, datef, camion):
    """
    Get Products List from Triz Chargement Page Detail Produit Sortie
    :driver: chrome driver ( web client )
    :dated: date debut
    :datef: date de fin
    :camion: camion du livreur
             "8442-0000005"         # WALID
             "8442-0000006"         # MOHAMED
             "8442-0000007"         # FETHI
             "8442-0000010"         # MM
    """
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
    product_list = []

    url = (
        f"{VENTE_URL}"
        f"?camion={camion}&datef={datef}&dated={dated}&type=camion"
    )

    driver.get(url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Page 1
    parse_products_table(driver, product_list)
    print(f"[+] Page 1 parsed → {len(product_list)} products")

    # Pagination detection
    try:
        paginator = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-paginator-pages"))
        )
        total_pages = len(paginator.find_elements(By.TAG_NAME, "span"))
    except TimeoutException:
        print("[!] Single page only")
        return product_list

    # Remaining pages
    for page_index in range(1, total_pages):
        print(f"[+] === Page {page_index + 1} ===")
        # Re-locate paginator evry time
        paginator = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-paginator-pages"))
        )
        pages = paginator.find_elements(By.TAG_NAME, "span")

        try:
            driver.execute_script(
                "arguments[0].click();", pages[page_index]
            )

            wait.until(EC.staleness_of(pages[0]))
            time.sleep(0.5)

            parse_products_table(driver, product_list)
            print(f"[✓] Products so far: {len(product_list)}")

        except StaleElementReferenceException:
            print("[!] Stale detected, retrying page...")
            continue

    return product_list


# ----------# To Excel File #---------- #
def prevendeur_to_excel(product_list, file_path):
    import pandas as pd
    df = pd.DataFrame(product_list)
    # clean some data
    df["Qte Global"] = (df["Qte Global"].str.replace(",", "", regex=False).astype(float, errors="ignore"))
    df["Total Valeur"] = (df["Total Valeur"].str.replace(",", "", regex=False).astype(float, errors="ignore"))
    # Grouping
    grouped = df.groupby("Famille", as_index=False)[["Qte Global", "Total Valeur"]].sum()
    grouped["Qte %"] = grouped["Qte Global"] / grouped["Qte Global"].sum() * 100
    grouped["Valeur %"] = grouped["Total Valeur"] / grouped["Total Valeur"].sum() * 100
    grouped[["Qte %", "Valeur %"]] = grouped[["Qte %", "Valeur %"]].round(2)
    # Save to Excel
    grouped.to_excel(file_path, index=False)
    print(f"[✓] Excel saved → {file_path}")


# ----------# MAIN Function of this Script #---------- #
def etat_prevendeur(username, password, dated, datef, camion, headless=False):
    """
    Etat Mensuel des prevendeur
    This is the main function
    :username: username
    :password: password
    """
    driver = create_driver(headless=headless)
    filename = f"C:\\Users\\ADMIN\\OneDrive\\Desktop\\etat_prevendeur_{camion}_{dated}.xlsx"
    if camion not in ['8442-0000005', '8442-0000006', '8442-0000007', '8442-0000010']:
        print("[✗] Incorrect CAMION.")
        return
    try:
        print("[*] Opening page...")
        if login(driver, username, password):
            product_list = get_product_par_prevendeur(driver, dated, datef, camion)
            prevendeur_to_excel(product_list, filename)
    finally:
        print("\n[✓] Close Browser.")
        driver.quit()


if __name__ == '__main__':
    # import os
    # import dotenv
    # dotenv.load_dotenv(dotenv.find_dotenv())
    # username = os.getenv("triz_username")
    # passwd = os.getenv('triz_password')
    from getpass import getpass
    print('-' * 30)
    username = input("[:] Triz Username: ")
    passwd = getpass("[:] Triz Password: ")
    print()
    camion = input("[:] Camion WALID(8442-0000005), MOHAMED(8442-0000006), FETHI(8442-0000007), MM(8442-0000010): ")
    #
    date_debut = "01-11-2025"
    date_fin = "30-11-2025"
    # camion = (WALID="8442-0000005", MOHAMED = "8442-0000006", FETHI = "8442-0000007", MM = "8442-0000010")
    # file_path = "/home/dabve/Desktop/etat_prevendeur_novembre.xlsx"
    # file_path = "C:\\Users\\ADMIN\\OneDrive\\Desktop\\etat_prevendeur_novembre.xlsx"
    etat_prevendeur(username, passwd, date_debut, date_fin, camion)
