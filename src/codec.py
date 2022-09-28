#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Andrew Ivanov <okolefleef@disr.it>
# SPDX-License-Identifier: ISC

# Python-Requires:
#   >= 3.7

import sys
import builtins
import platform

from io import BytesIO
from os import PathLike
from gzip import GzipFile
from contextlib import contextmanager
from pathlib import Path


path_workdir = Path(__file__).resolve().parent.parent


try:
    from Crypto.Cipher import ChaCha20
except ImportError:
    if platform.system() == "Windows":
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install.cmd)")
    else:
        print(f"You forgot to run the installer.\n -> ({path_workdir}/install)")

    sys.exit(1)


class EncryptedFile:
    __slots__ = [
        'fileobj',
        'cipher'
    ]

    def __init__(self, fileobj, key):
        self.fileobj = fileobj

        with memoryview(key) as data:
            if len(data) not in (40, 44, 56):
                raise ValueError('key must be 40, 44 or 56 bytes')

            self.cipher = ChaCha20.new(key=data[:32], nonce=data[32:])

    def read(self, size=-1):
        return self.cipher.decrypt(self.fileobj.read(size))

    def write(self, data):
        count = self.fileobj.write(self.cipher.encrypt(data))

        if count != len(data):
            self.cipher.seek(self.fileobj.tell())

        return count

    def flush(self):
        self.fileobj.flush()


@contextmanager
def open(file, mode, key):
    if isinstance(file, (str, bytes, PathLike)):
        with builtins.open(file, mode) as file:
            with open(file, mode, key) as xfile:
                yield xfile
    elif hasattr(file, 'read') or hasattr(file, 'write'):
        with GzipFile(fileobj=EncryptedFile(file, key), mode=mode) as xfile:
            yield xfile
    else:
        raise TypeError('file must be a str or bytes object, or a file')


def decode(data, key):
    with BytesIO(data) as buffer:
        with open(buffer, 'rb', key) as file:
            return file.read()


def encode(data, key):
    with BytesIO() as buffer:
        with open(buffer, 'wb', key) as file:
            file.write(data)

        return buffer.getvalue()
