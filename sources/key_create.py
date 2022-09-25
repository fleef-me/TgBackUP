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

    secret_key_path = path_workdir / "data" / settings.SECRETKEYFILE.get_secret_value()

    if not secret_key_path.is_file():
        secret_key_path.write_bytes(get_random_bytes(32))

        print("\n", "***" * 20, f"Secret key created! \n -> ({secret_key_path})", "***" * 20, sep="\n")


if __name__ == '__main__':
    create()
