#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Andrew Ivanov <okolefleef@disr.it>
# SPDX-License-Identifier: ISC

from pathlib import Path
from textwrap import dedent


def main():
    dirs = ("bin", "data", "results", "tmp", "sources/__pycache__")

    while True:
        query = input(
            f"The following directories will be cleared ({', '.join(dirs)}).\n" +
            "Are you sure?\n [y/n] -> "
        )
        if query == "n":
            print("Operation aborted by user")
            return None
        if query == "y":
            break
        else:
            continue

    path_workdir = Path(__file__).resolve().parent.parent

    for directory in dirs:
        path_dir = path_workdir / directory
        if path_dir.is_dir():
            for path in path_dir.iterdir():
                path.unlink()

    (path_workdir / "data" / "files.json").write_text(dedent("""\
        {}
    """))

    (path_workdir / "data" / ".env").write_text(dedent("""\
        TG_APP_ID=
        SESSION_NAME=""
        DEBUG=False
        CID_CHANNEL=""
        SECRETKEYFILE=""
        TG_APP_HASH=""
    """))

    (path_workdir / "data" / ".env-example").write_text(dedent("""\
        TG_APP_ID=999
        SESSION_NAME="session"
        DEBUG=False
        CID_CHANNEL="mydatabackup"
        SECRETKEYFILE="SecretKey.bin"
        TG_APP_HASH="fdkfdkfdkfd"
        
        # TG_APP_HASH & TG_APP_ID:
        # # https://core.telegram.org/api/obtaining_api_id
        # SESSION_NAME & SECRETKEYFILE - any
        # CID_CHANNEL - your chat or channel in Telegram.
    """))


if __name__ == "__main__":
    main()
