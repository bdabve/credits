#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import json, os, datetime
from platformdirs import user_data_dir
from src.strg import load_machine_id
# from strg import load_machine_id

APP_NAME = "soldes"


def license_path():
    return os.path.join(user_data_dir(APP_NAME), "license.json")


def load_license():
    """
    Load the license data from storage. Return None if not found.
    """
    if not os.path.exists(license_path()):
        return None

    with open(license_path(), "r") as f:
        return json.load(f)


def check_license():
    """
    Check if the license is valid for this machine and not expired.
    Return a dict with success status and message.
    """
    lic = load_license()
    if not lic:
        return {"success": False, "message": "License not found"}

    if lic["machine_id"] != load_machine_id():
        return {"success": False, "message": "License not for this machine"}

    today = datetime.date.today()
    expires = datetime.date.fromisoformat(lic["expires_at"])

    if today > expires:
        return {"success": False, "message": "License expired"}

    return {"success": True, "message": "License valid until " + lic["expires_at"]}


def update_license(date):
    """
    Update the license expiration date by adding 6 months from today.
    This can be used for renewing the license.
    usage:
        $ update_licence = gsl.update_license("12-03-2026")
    """
    lic = load_license()
    if not lic:
        return {"success": False, "message": "License not found"}

    # today = datetime.date.today()
    # plus_six_month = today + datetime.timedelta(days=180)
    # format the date
    date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
    date_to = date.strftime("%Y-%m-%d")
    lic["expires_at"] = str(date_to)

    with open(license_path(), "w") as f:
        json.dump(lic, f)

    return {"success": True, "message": "License updated", "expires_at": lic["expires_at"]}


if __name__ == '__main__':
    licence = load_license()
    print(licence)
    update_licence = update_license("12-12-2026")
    ok = check_license()
    print(ok)
