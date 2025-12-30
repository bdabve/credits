#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :

import uuid
import hashlib
import subprocess
import strg as storage


def get_machine_id():
    """
    Generate a unique machine ID based on hardware information.
    """
    try:
        cmd = "wmic csproduct get uuid"
        uuid_str = subprocess.check_output(cmd, shell=True).decode().split("\n")[1].strip()
    except Exception:
        uuid_str = str(uuid.getnode())

    raw = uuid_str + str(uuid.getnode())
    return hashlib.sha256(raw.encode()).hexdigest()


def init_machine():
    """
    Initialize machine ID. Load from storage or generate and save if not found.
    This must be called once at the start of the application.
    """
    saved = storage.load_machine_id()

    if saved:
        print("Loaded existing machine ID.")
        return saved

    mid = get_machine_id()
    print("Generated new machine ID.")
    storage.save_machine_id(mid)
    return mid


if __name__ == '__main__':
    machine_id = init_machine()
    print(machine_id)
