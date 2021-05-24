import argparse
import sys
from pathlib import Path

from src.ppb import upload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip_flag', '-zip_flag', action='store_true', dest='zip_flag',
                        help="zip folder and upload it. The folder to be zipped needs to be "
                             "after the flag -z. Example: ppb -z test")
    parser.add_argument('--plain', action='store_true', dest='plain',
                        help="if this flag is set, no syntax highlighting will be added to the file.")
    parser.add_argument('--lifetime', default=20,
                        help="Time in days after which the file is deleted. Set -1 to never delete de file.")
    parser.add_argument('--description', '-d', default='', type=str, help="Description stored in the ppb dataframe.")
    parser.add_argument('file', type=str, help='file to upload and display')

    flags = parser.parse_args()

    file_path = Path(flags.file.replace(" ", "\\ "))

    upload(file_path=file_path, zip_flag=flags.zip_flag, plain=flags.plain, description=flags.description,
           lifetime=flags.lifetime)


if __name__ == '__main__':
    sys.exit(main())
