# -*- coding: utf-8 -*-
from pathlib import Path

from ppb import upload


def test_upload():
    test_file = Path(__file__).parent / 'test_file.txt'
    upload(file_path=test_file)


if __name__ == '__main__':
    test_upload()
