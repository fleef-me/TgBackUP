#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Andrew Ivanov <okolefleef@disr.it>
# SPDX-License-Identifier: ISC

# Python-Requires:
#   >= 3.7

import json
import platform
import sys
import os
import asyncio
from typing import Tuple
from pathlib import Path
from gzip import decompress


path_workdir = Path(__file__).resolve().parent.parent

try:
    from pyrogram import Client
    from Crypto.Cipher import ChaCha20
except ImportError:
    if platform.system() == "Windows":
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install.cmd)")
    else:
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install)")

    sys.exit(1)


from config import get_env, Settings
from key_create import create


settings: Settings = get_env()
create()

if settings.DEBUG:
    import logging

    logging.basicConfig(level=logging.DEBUG)


def encode(private_key, nonce, ciphertext):
    try:
        cipher = ChaCha20.new(key=private_key, nonce=nonce)
        plaintext_local = decompress(cipher.decrypt(ciphertext))

        return plaintext_local

    except (ValueError, KeyError):
        raise RuntimeError("Incorrect decryption")


def read_binary_file(pathfile_bin: str) -> Tuple[bytes, bytes]:
    with open(pathfile_bin, 'rb') as file:
        nonce = file.read(8)
        ciphertext = file.read()

    return nonce, ciphertext


async def get_cloud_files(client: Client):
    async with client:
        me = await client.get_me()
        print(f"The client ({me.id}) is authorized!")
        messages = []
        async for message in client.get_chat_history(settings.CID_CHANNEL):
            if message.document:
                messages.append(message.document)  # .file_name

        return messages


async def uploading_file_storage(client, json_files, cloud_files, cloud_files_name) -> list:
    c = 0
    cloud_binary_files = []
    pretty_text = ""
    for value, key in json_files.items():
        if value in cloud_files_name:
            for cf in cloud_files:
                if cf.file_name == value:
                    cloud_binary_files.append(value)
                    pretty_text += f"[{c}]: {key} ({cf.date})\n"
                    c += 1

    print(f"Select the file to be decrypted: \n{pretty_text}")
    range_c = list(range(c))
    try:
        index_file = int(input(f"{range_c} -> "))
        file_binary = cloud_binary_files[index_file]
    except (IndexError, ValueError):
        print(
            "", "***" * 10,
            f"Write a number from {range_c[0]} to {range_c[-1]}",
            "***" * 10,
            sep="\n"
        )
        sys.exit(0)

    print(f"Selected: {file_binary}")
    cloud_binary_file = json_files[file_binary]

    for cf in cloud_files:
        if cf.file_name == cloud_binary_file:
            file_binary = cf
            break

    messages = []
    async with client:
        async for message in client.search_messages(
                                                    chat_id=settings.CID_CHANNEL,
                                                    query=file_binary,
                                                    limit=10):
            if message.document and message.document.file_name == file_binary:
                messages.append(message)

        files_binary = []
        for file_message in messages:
            file_binary = f"{str(path_workdir)}/bin/{file_binary}"
            await file_message.download(file_name=file_binary)

            files_binary.append(file_binary)

    return files_binary


async def main():
    client: Client = Client(
        name=f"{path_workdir}/data/{settings.SESSION_NAME}",
        api_id=settings.TG_APP_ID,
        api_hash=settings.TG_APP_HASH.get_secret_value()
    )
    cloud_files = await get_cloud_files(client)
    cloud_files_name = [cf.file_name for cf in cloud_files]

    with open(path_workdir / "data" / "files.json", "r") as file_local:
        json_files = json.loads(file_local.read())

    if not cloud_files:
        print("File not found in cloud storage")
        sys.exit(0)

    files_binary = await uploading_file_storage(client, json_files, cloud_files, cloud_files_name)

    with open(path_workdir / "data" / settings.SECRETKEYFILE.get_secret_value(), 'rb') as file:
        private_key = file.read()

    for file_binary in files_binary:
        result = read_binary_file(file_binary)
        plaintext_encode = encode(
            private_key=private_key, nonce=result[0], ciphertext=result[1]
        )
        with open(path_workdir / "data" / "files.json", "r") as file_local:
            json_files = json.loads(file_local.read())

        for key, value in json_files.items():
            if key == file_binary.split("/")[-1]:
                found = True
                break

            found = False

        if not found:
            print(
                f"File not found in data/files.json. " +
                "I can't find the original filename. Text: \n\n{plaintext_encode}"
            )
        elif found:
            original_filename = str(path_workdir) + "/results/" + value.replace("/", "+")
            with open(original_filename, "wb") as file:
                file.write(plaintext_encode)

            print(
                f"\nThe file was successfully created and placed on the path: \n -> "
                + original_filename
                + f"\nOriginal filename: \n -> {value}\n")

        os.remove(file_binary)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
