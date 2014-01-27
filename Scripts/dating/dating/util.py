__author__ = 'Alejandro'

# Python Imports
import os
import hashlib


def get_file_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def get_file_size_bytes(file_path):
    size = 0
    with open(file_path, 'rb') as f:
        f.seek(0, 2)    # Move the cursor to the end of the file
        size = f.tell()
    return size