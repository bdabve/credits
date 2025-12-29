#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :

import uuid
import hashlib
import subprocess

from strg import save_machine_id, load_machine_id


def get_machine_id():
    try:
        cmd = "wmic csproduct get uuid"
        uuid_str = subprocess.check_output(cmd, shell=True).decode().split("\n")[1].strip()
    except Exception:
        uuid_str = str(uuid.getnode())

    raw = uuid_str + str(uuid.getnode())
    return hashlib.sha256(raw.encode()).hexdigest()


def init_machine():
    saved = load_machine_id()

    if saved:
        return saved

    mid = get_machine_id()
    save_machine_id(mid)
    return mid


if __name__ == '__main__':
    machine_id = init_machine()
    print(machine_id)
