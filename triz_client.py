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
            "download.directory_upgrade": True,
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

    url = "http://51.255.79.241:8080/trizstock/faces/view/vente/listDetailProduitSortie.xhtml?datef=17-12-2025&dated=17-12-2025&type=camion"
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


def get_prevendeur_vente(driver, dated, datef, camion):
    """
    datef = datefin
    dated = datedebut
    camion = 8442-0000005 -> WALID
    """
    url = f"http://51.255.79.241:8080/trizstock/faces/view/vente/listDetailProduitSortie.xhtml?camion={camion}&datef={datef}&dated={dated}&type=camion"

    driver.get(url)
    excel_btn = driver.find_element(By.ID, 'liste:j_idt613:j_idt618')
    excel_btn.click()


if __name__ == '__main__':
    client = client()
    username = 'a.brahim'
    passwd = '18111986'
    login = login(client, username, passwd)
    date_begin = "01-11-2025"
    date_end = "30-11-2025"
    camion = "8442-0000005"     # WALID
    get_prevendeur_vente(client, date_begin, date_end, '')
