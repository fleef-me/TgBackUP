#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Andrew Ivanov <okolefleef@disr.it>
# SPDX-License-Identifier: ISC

# Python-Requires:
#   >= 3.7

import json
import platform
import sys
import asyncio
import hashlib
import shutil
from io import BytesIO
from pathlib import Path

import codec
from config import get_env, Settings
from key_create import create


path_workdir = Path(__file__).resolve().parent.parent

try:
    from pyrogram import Client
except ImportError:
    if platform.system() == "Windows":
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install.cmd)")
    else:
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install)")

    sys.exit(1)


settings: Settings = get_env()
create()

if settings.DEBUG:
    import logging

    logging.basicConfig(level=logging.DEBUG)


def progress(current, total):
    print(end=f"\rFile upload: {(current * 100 / total):.2f}%", flush=True)


def filename_hashing(filename_input: str) -> str:
    path_workdir_fj = path_workdir / "data" / "files.json"
    json_files = json.loads(path_workdir_fj.read_bytes())

    sha = hashlib.sha1(filename_input.encode())
    sha1_filename_output = sha.hexdigest() + ".bin"
    json_files[sha1_filename_output] = filename_input

    path_workdir_fj.write_text(json.dumps(json_files))

    return sha1_filename_output


async def upload_binary_file(buffer: BytesIO):
    client: Client = Client(
        name=str(path_workdir / "data" / settings.SESSION_NAME),
        api_id=settings.TG_APP_ID,
        api_hash=settings.TG_APP_HASH.get_secret_value()
    )

    async with client:
        me = await client.get_me()

        print(f"The client ({me.id}) is authorized!\n")
        print(f"Uploading file to https://t.me/{settings.CID_CHANNEL}...")

        message = await client.send_document(
            chat_id=settings.CID_CHANNEL,
            protect_content=True,
            document=buffer,
            progress=progress
        )

        print(f"\nFile uploaded successfully! Link: {message.link}\n")


def main():
    filename = input("Enter the full path to the file:\n -> ")
    private_key = (path_workdir / "data" / settings.SECRETKEYFILE.get_secret_value()).read_bytes()

    with BytesIO() as buffer:
        buffer.name = filename_hashing(filename)

        try:
            with open(filename, 'rb') as input_file:
                with codec.open(buffer, 'wb', private_key) as output_file:
                    shutil.copyfileobj(input_file, output_file)
        except OSError as ex:
            print("", "***" * 20, ex, "***" * 20, sep="\n")
            sys.exit(0)

        asyncio.run(upload_binary_file(buffer))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
