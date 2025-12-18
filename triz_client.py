#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


def client():
    options = uc.ChromeOptions()
    DOWNLOAD_DIR = 'triz_downloads'
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True,   # auto “Keep”
            "safebrowsing.disable_download_protection": True
        },
    )

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    client = uc.Chrome(
        options=options,
        headless=False,   # test visible first
    )
    client.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": DOWNLOAD_DIR,
        },
    )

    return client


def login(driver, username: str, password: str, timeout: int = 20):
    """
    Perform login using provided Selenium driver.

    :param driver: Selenium / undetected_chromedriver instance
    :param username: login username
    :param password: login password
    :param timeout: wait timeout in seconds
    """

    url = "http://51.255.79.241:8080/trizstock/faces/login.xhtml"
    driver.get(url)

    wait = WebDriverWait(driver, timeout)

    # Wait for username field
    user_input = wait.until(
        EC.presence_of_element_located((By.ID, "j_username"))
    )
    user_input.clear()
    user_input.send_keys(username)

    # Wait for password field
    pass_input = wait.until(
        EC.presence_of_element_located((By.ID, "j_password"))
    )
    pass_input.clear()
    pass_input.send_keys(password + Keys.ENTER)


def parse_products_table(driver, product_list):
    wait = WebDriverWait(driver, 20)
    table = wait.until(
        EC.presence_of_element_located((By.ID, "liste:j_idt613:dataTable2_data"))
    )
    trs = table.find_elements(By.TAG_NAME, 'tr')
    for tr in trs:
        tds = tr.find_elements(By.TAG_NAME, 'td')
        item = {
            "Famille": tds[0].text,
            "S.Famille": tds[2].text,
            "Produit": tds[3].text,
            "Qte Global": tds[7].text,
            "Total Valeur": tds[9].text
        }
        print(item)
        print("-" * 30)
        product_list.append(item)

    print("[+] === The Hole Data ===")
    print(product_list)
    print(f"[+] Len Data: {len(product_list)}")

    return product_list


def get_prevendeur_vente(driver, dated, datef, camion):
    """
    datef = datefin
    dated = datedebut
    camion = 8442-0000005 -> WALID
    """
    import time
    url = f"http://51.255.79.241:8080/trizstock/faces/view/vente/listDetailProduitSortie.xhtml?camion={camion}&datef={datef}&dated={dated}&type=camion"

    wait = WebDriverWait(driver, 20)
    driver.get(url)

    paginator = driver.find_element(By.CLASS_NAME, "ui-paginator-pages")
    pages = paginator.find_elements(By.TAG_NAME, 'span')
    product_list = list()
    parse_products_table(driver, product_list)  # first page
    for page in pages[1:]:  # skip the first page
        print(page.text)
        page.click()
        time.sleep(50)
        parse_products_table(driver, product_list)

    print(f"[+] === After second page Len (Products List) {len(products_list)}")
    # print("\n==== [+] Finding Excel Button and click ====")
    # excel_btn = driver.find_element(By.ID, 'liste:j_idt613:j_idt618')       # liste:j_idt613:j_idt618
    # excel_btn.click()
    input('\n[:] Press Any Key: \n')
    driver.quit()


if __name__ == '__main__':
    client = client()
    username = 'a.brahim'
    passwd = '18111986'
    login = login(client, username, passwd)
    date_begin = "01-11-2025"
    date_end = "30-11-2025"
    camion = "8442-0000005"     # WALID
    get_prevendeur_vente(client, date_begin, date_end, '')
