#!/usr/bin/env python3

# Copyright 2022 Andrew Ivanov <okolefleef@disr.it>
# All rights reserved

# Python-Requires:
#   >= 3.7

import os
import json
import platform
import sys
import asyncio
import hashlib
from pathlib import Path
from gzip import compress


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


def decode(private_key, plaintext):
    cipher = ChaCha20.new(key=private_key)
    ciphertext = cipher.encrypt(compress(plaintext))

    return {'nonce': cipher.nonce, 'ciphertext': ciphertext}


def write_binary_file(pathfile_bin: Path, nonce: bytes, ciphertext: bytes) -> None:
    with open(pathfile_bin, 'wb') as file:
        file.write(nonce)
        file.write(ciphertext)


def filename_hashing(filename_input: str) -> str:
    sha = hashlib.sha1(filename_input.encode())
    sha1_filename_output = sha.hexdigest() + os.urandom(3).hex() + ".bin"

    with open(path_workdir / "data" / "files.json", "r") as file_local:
        json_files = json.loads(file_local.read())

    json_files[sha1_filename_output] = filename_input
    json_files = json.dumps(json_files)

    with open(path_workdir / "data" / "files.json", "w") as file_local:
        file_local.write(json_files)

    return sha1_filename_output


async def upload_binary_file(filename_output: Path):
    client: Client = Client(
        name=f"{path_workdir}/data/{settings.SESSION_NAME}",
        api_id=settings.TG_APP_ID,
        api_hash=settings.TG_APP_HASH.get_secret_value()
    )

    async with client:
        me = await client.get_me()
        print(f"The client ({me.id}) is authorized!")

        filename_output_name = filename_output.name
        messages = []
        async for message in client.get_chat_history(settings.CID_CHANNEL):
            if message.document:
                messages.append(message.document.file_name)

        if filename_output_name in messages:
            while True:
                query = input(
                    "The file has been found in the repository.\n" +
                    "Are you sure you want to download it again?\n [y/n] -> "
                )
                if query == "n":
                    print("Operation aborted by user")
                    return None
                if query == "y":
                    break
                else:
                    print()
                    continue

        print(f"Uploading file to https://t.me/{settings.CID_CHANNEL}...")
        message = await client.send_document(
            chat_id=settings.CID_CHANNEL,
            protect_content=True,
            document=str(filename_output),
        )
        print(f"File uploaded successfully! Link: {message.link}")
        os.remove(filename_output)
        print(f"The local file has been deleted. ({filename_output})")


def main():
    filename_input = input("Enter the full path to the file:\n -> ")

    try:
        with open(filename_input, "rb") as file:
            plaintext = file.read()
    except (PermissionError, FileNotFoundError, IsADirectoryError) as ex:
        print("", "***" * 20, ex, "***" * 20, sep="\n")
        sys.exit(0)

    filename_output = filename_hashing(filename_input)

    with open(path_workdir / "data" / settings.SECRETKEYFILE.get_secret_value(), 'rb') as file:
        private_key = file.read()
        result = decode(private_key, plaintext)

    filename_output_full = path_workdir / "tmp/" / filename_output
    write_binary_file(
        filename_output_full,
        result["nonce"],
        result["ciphertext"]
    )

    asyncio.run(upload_binary_file(filename_output_full))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
