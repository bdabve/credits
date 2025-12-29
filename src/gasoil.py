#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import json, os, datetime
from platformdirs import user_data_dir
from strg import load_machine_id

APP_NAME = "soldes"


def license_path():
    return os.path.join(
        user_data_dir(APP_NAME),
        "license.json"
    )


def load_license():
    if not os.path.exists(license_path()):
        return None

    with open(license_path(), "r") as f:
        return json.load(f)


def check_license():
    lic = load_license()
    if not lic:
        return {"success": False, "message": "License not found"}

    if lic["machine_id"] != load_machine_id():
        print("[+] LIC MACHINE ID: ", lic["machine_id"])
        print("[+] LOADED MACHINE ID: ", load_machine_id())
        return {"success": False, "message": "License not for this machine"}

    today = datetime.date.today()
    expires = datetime.date.fromisoformat(lic["expires_at"])

    if today > expires:
        return {"success": False, "message": "License expired"}

    return {"success": True, "message": "License valid"}


if __name__ == '__main__':
    ok = check_license()
    print(ok)
