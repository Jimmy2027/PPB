# HK, 17.12.20
import argparse
import configparser
import hashlib
import os
import sys
from pathlib import Path
import json
from ppb import log
from ppb.utils import get_unique_str
from ppb.upload_files import upload_file_remote, upload_file_local


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

    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.config/ppb.conf'))
    ppb_target_host = config['ppb_config']['PPB_TARGET_HOST'].replace("'", '')
    ppb_path_on_host = config['ppb_config']['PPB_PATH_ON_HOST'].replace("'", '')
    ppb_http_path = config['ppb_config']['PPB_HTTP_PATH'].replace("'", '')
    sender_name = config['other']['SENDER_NAME'].replace("'", '')

    flags = parser.parse_args()

    if not ppb_target_host:
        print("ERROR: The PPB_TARGET_HOST variable is unset."
              "Nothing can be uploaded if there is no target host."
              "Please copy the example config file from under \"/etc/ppb.conf\" to \"~/.config/ppb.conf\","
              "and fill in the variable values according to your personal settings.")

    # when running on host, ppb_http_path = ppb_path_on_host
    if not ppb_http_path:
        ppb_http_path = ppb_path_on_host

    file_path = Path(flags.file.replace(" ", "\\ "))
    file_stem = get_unique_str(file_path.stem)
    file_id = hashlib.md5(file_stem.encode('utf-8')).hexdigest()
    dest_file = file_id[:12]
    ext = file_path.suffix

    # if zipping file, add .zip extension
    dest_file += f'{ext}' + '.zip' * flags.zip_flag
    dest_file = Path(dest_file)

    in_file = dest_file

    curl_command = f'curl -X POST --silent --output /dev/null --show-error ' \
                   f'--fail {ppb_http_path}/{in_file} -d filename={dest_file} '

    metadata = {
        'lifetime': flags.lifetime,
        'description': flags.description,
        'orig_filename': str(file_path.stem) + ext,
        'sender': sender_name
    }

    # send file to where it will be read by flask app
    if ppb_target_host == 'local':
        upload_file_local(dest_file, file_path, flags, in_file, ppb_path_on_host, metadata)
    else:
        upload_file_remote(dest_file, ext, file_path, flags, in_file, ppb_path_on_host, ppb_target_host,
                           metadata=metadata)

    log.info(curl_command)
    os.system(curl_command)
    log.info(f'Uploaded to {ppb_http_path}/{in_file}')


if __name__ == '__main__':
    sys.exit(main())
