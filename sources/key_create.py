#!/usr/bin/env python3

# Copyright 2022 Andrew Ivanov <okolefleef@disr.it>
# All rights reserved

# Python-Requires:
#   >= 3.7

import sys
import os
import platform
from pathlib import Path

path_workdir = Path(__file__).resolve().parent.parent

try:
    from Crypto.Random import get_random_bytes
except ImportError:
    if platform.system() == "Windows":
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install.cmd)")
    else:
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install)")

    sys.exit(1)


from config import get_env, Settings


def create():
    settings: Settings = get_env()

    fullpath_secretkey = path_workdir / "data" / settings.SECRETKEYFILE.get_secret_value()
    is_file_exists = os.path.exists(fullpath_secretkey)

    if not is_file_exists:
        key = get_random_bytes(32)
        with open(fullpath_secretkey, 'wb') as file:
            file.write(key)

        print("\n", "***" * 20, f"Secret key created! \n -> ({fullpath_secretkey})", "***" * 20, sep="\n")


if __name__ == '__main__':
    create()
