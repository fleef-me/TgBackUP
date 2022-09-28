#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Andrew Ivanov <okolefleef@disr.it>
# SPDX-License-Identifier: ISC

# Python-Requires:
#   >= 3.7

import json
import platform
import sys
import asyncio
import shutil
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


async def get_cloud_files(client: Client):
    messages = []
    async for message in client.get_chat_history(settings.CID_CHANNEL):
        if message.document:
            messages.append(message)

    return messages


async def uploading_file_storage(client, json_files, cloud_files, cloud_files_name) -> list:
    c = 0
    cloud_binary_files = []
    pretty_text = ""
    for value, key in json_files.items():
        if value in cloud_files_name:
            for cf in cloud_files:
                if cf.document.file_name == value:
                    cloud_binary_files.append(cf)
                    pretty_text += f"[{c}]: {key} ({cf.document.date})\n"
                    c += 1

    print(f"Select the file to be decrypted: \n{pretty_text}")
    range_c = list(range(c))
    range_c.append("exit")
    try:
        ask_user = input(f"[{', '.join(map(str, range_c))}] -> ")
        if ask_user == "exit":
            print("Operation aborted by user")
            sys.exit(1)

        index_file = int(ask_user)
        file_binary = cloud_binary_files[index_file]
    except (IndexError, ValueError):
        print("", "***" * 10, f"Write a number from {range_c[0]} to {range_c[-1]}", "***" * 10, sep="\n")
        sys.exit(1)

    print(f"Selected: {file_binary.document.file_name}")

    buffer = await file_binary.download(in_memory=True)
    buffer.seek(0)

    return buffer


async def main():
    path_workdir_data = path_workdir / "data"
    client: Client = Client(
        name=str(path_workdir_data / settings.SESSION_NAME),
        api_id=settings.TG_APP_ID,
        api_hash=settings.TG_APP_HASH.get_secret_value()
    )

    async with client:
        me = await client.get_me()
        print(f"The client ({me.id}) is authorized!\n")

        cloud_files = await get_cloud_files(client)
        cloud_files_name = [cf.document.file_name for cf in cloud_files]

        json_files = json.loads((path_workdir_data / "files.json").read_text())

        if not cloud_files:
            print("File not found in cloud storage")
            sys.exit(1)

        buffer = await uploading_file_storage(client, json_files, cloud_files, cloud_files_name)

    private_key = (path_workdir_data / settings.SECRETKEYFILE.get_secret_value()).read_bytes()
    value_path = Path(json_files[buffer.name])

    if value_path.drive:
        value_parts = [value_path.drive.rstrip(":")]
    else:
        value_parts = []

    value_parts += value_path.relative_to(value_path.anchor).parts

    original_filename = path_workdir / "results" / "+".join(value_parts)

    with codec.open(buffer, 'rb', private_key) as input_file:
        with open(original_filename, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)

    print(f"\nThe file was successfully created on the path:\n -> {original_filename}")
    print(f"Original filename: \n -> {json_files[buffer.name]}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)
