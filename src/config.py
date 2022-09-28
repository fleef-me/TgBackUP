#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Andrew Ivanov <okolefleef@disr.it>
# SPDX-License-Identifier: ISC

import sys
import json
import platform
from textwrap import dedent
from pathlib import Path


path_workdir = Path(__file__).resolve().parent.parent
path_workdir_fj = path_workdir / "data" / "files.json"
path_workdir_env = path_workdir / "data" / ".env"

try:
    from pydantic import BaseSettings, SecretStr, ValidationError
except ImportError:
    if platform.system() == "Windows":
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install.cmd)")
    else:
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install)")

    sys.exit(1)


class Settings(BaseSettings):
    DEBUG: bool = False
    TG_APP_ID: int
    TG_APP_HASH: SecretStr
    CID_CHANNEL: str
    SESSION_NAME: str
    SECRETKEYFILE: SecretStr

    class Config:
        env_file = path_workdir_env


def get_env() -> Settings:
    if not path_workdir_fj.is_file():
        path_workdir_fj.write_text(dedent("""\
            {}
        """))

    if not path_workdir_env.is_file():
        path_workdir_env.write_text(dedent("""\
            TG_APP_ID=
            SESSION_NAME=""
            DEBUG=False
            CID_CHANNEL=""
            SECRETKEYFILE=""
            TG_APP_HASH=""
        """))
    try:
        return Settings()
    except ValidationError as error:
        print('ERROR: .env file is incorrect:')

        for entry in json.loads(error.json()):
            print(f"\t{' -> '.join(map(str, entry['loc']))}:")
            print(f"\t\t{entry['msg']}")

        sys.exit(1)


__all__ = ["get_env", "Settings"]
