#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Andrew Ivanov <okolefleef@disr.it>
# SPDX-License-Identifier: ISC

# Python-Requires:
#   >= 3.7

import sys
import platform
from pathlib import Path

from config import get_env, Settings


path_workdir = Path(__file__).resolve().parent.parent

try:
    from Crypto.Random import get_random_bytes
except ImportError:
    if platform.system() == "Windows":
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install.cmd)")
    else:
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install)")

    sys.exit(1)



def create():
    settings: Settings = get_env()

    secret_key_path = path_workdir / "data" / settings.SECRETKEYFILE.get_secret_value()

    if not secret_key_path.is_file():
        secret_key_path.write_bytes(get_random_bytes(40))

        print(
            '***' * 15,
            f"\n\n-> Secret key created!\n\t{secret_key_path}\n",
        )


if __name__ == '__main__':
    create()
