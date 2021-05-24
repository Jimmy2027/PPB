# -*- coding: utf-8 -*-
from pathlib import Path

from src.ppb import upload


def test_upload():
    test_file = Path(__file__).parent / 'test_file.txt'
    url = upload(file_path=test_file)
    print(f'This is my url: {url}')


if __name__ == '__main__':
    test_upload()
