#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os
import datetime
from platformdirs import user_data_dir

APP_NAME = "soldes"


def _base_path():
    """
    Get or create the base path for storing application data.
    """
    path = user_data_dir(APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def save_machine_id(machine_id):
    """
    Save the machine ID and create a license file with expiration date.
    """
    with open(os.path.join(_base_path(), "machine.json"), "w") as f:
        # Save machine ID
        json.dump({"machine_id": machine_id}, f)
    with open(os.path.join(_base_path(), "license.json"), "w") as f:
        # Save license with expiration date
        today = datetime.date.today()
        plus_six_month = today + datetime.timedelta(days=180)
        data = {"app_name": APP_NAME, "machine_id": machine_id, "expires_at": str(plus_six_month)}
        json.dump(data, f)


def load_machine_id():
    """
    Load the machine ID from storage. Return None if not found.
    """
    path = os.path.join(_base_path(), "machine.json")
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return json.load(f).get("machine_id")


if __name__ == '__main__':
    pass
    # today = datetime.date.today()
    # plus_six_month = today + datetime.timedelta(days=180)
    # print("Six months from today:", plus_six_month)
    # print("Today's date:", today)