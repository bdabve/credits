#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os
from platformdirs import user_data_dir

APP_NAME = "soldes"
# APP_AUTHOR = "YourCompany"  # optional


def _base_path():
    path = user_data_dir(APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def save_machine_id(machine_id):
    with open(os.path.join(_base_path(), "machine.json"), "w") as f:
        json.dump({"machine_id": machine_id}, f)


def load_machine_id():
    path = os.path.join(_base_path(), "machine.json")
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return json.load(f).get("machine_id")
