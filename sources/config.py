#!/usr/bin/env python3

# Copyright 2022 Andrew Ivanov <okolefleef@disr.it>
# All rights reserved

import sys
import json
import platform
from textwrap import dedent
from pathlib import Path


path_workdir = Path(__file__).resolve().parent.parent

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
        env_file = path_workdir / "data/.env"


def get_env() -> Settings:
    try:
        return Settings()
    except ValidationError as error:
        message_json = json.loads(error.json())[0]
        no_set_param = message_json["loc"][0]
        message_error = message_json["msg"]

        print(dedent(f"WARNING:\n -> [{no_set_param}]: {message_error}\n"))

        sys.exit(1)


__all__ = ["get_env", "Settings"]
