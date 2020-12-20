# HK, 17.12.20
import argparse
import configparser
import hashlib
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename

from ppb import log
from ppb.utils import get_unique_str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip_flag', '-zip_flag', action='store_true', dest='zip_flag',
                        help="zip folder and upload it. The folder to be zipped needs to be "
                             "after the flag -z. Example: ppb -z test")
    parser.add_argument('--plain', action='store_true', dest='plain',
                        help="if this flag is set, no syntax highlighting will be added to the file.")
    parser.add_argument('file', type=str, help='file to upload and display')

    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.config/ppb.conf'))
    ppb_target_host = config['ppb_config']['PPB_TARGET_HOST'].replace("'", '')
    ppb_path_on_host = config['ppb_config']['PPB_PATH_ON_HOST'].replace("'", '')
    ppb_http_path = config['ppb_config']['PPB_HTTP_PATH'].replace("'", '')

    flags = parser.parse_args()

    if not ppb_target_host:
        print("ERROR: The PPB_TARGET_HOST variable is unset."
              "Nothing can be uploaded if there is no target host."
              "Please copy the example config file from under \"/etc/ppb.conf\" to \"~/.config/ppb.conf\","
              "and fill in the variable values according to your personal settings.")

    # when running on host, ppb_http_path = ppb_path_on_host
    if not ppb_http_path:
        ppb_http_path = ppb_path_on_host

    file_path = Path(flags.file)
    file_stem = get_unique_str(file_path.stem)
    file_id = hashlib.md5(file_stem.encode('utf-8')).hexdigest()
    dest_file = file_id[:12]
    ext = file_path.suffix

    # if zipping file, add .zip extension
    dest_file += f'{ext}' + '.zip' * flags.zip_flag

    in_file = dest_file

    curl_command = f'curl -X POST --silent --output /dev/null --show-error ' \
                   f'--fail http://109.202.220.6:5000/file/{in_file} -d filename={dest_file}'

    if ppb_target_host == 'local':
        if flags.zip_flag:
            zip_command = f'zip -r {ppb_path_on_host}/{in_file} {file_path}'
            log.info(zip_command)
            os.system(zip_command)
        else:
            dest_path = os.path.join(ppb_path_on_host, dest_file)
            if flags.plain:
                shutil.copyfile(file_path, dest_path)
            else:
                with open(file_path, mode='r') as c:
                    code = c.read()
                with open(dest_path, mode='w') as f:
                    highlight(code, guess_lexer_for_filename(file_path, c), HtmlFormatter(linenos=True, full=True),
                              outfile=f)
                log.info(f'Highlighted {file_path}.')
    else:

        with tempfile.TemporaryDirectory() as tmpdirname:
            tempfile_path = os.path.join(tmpdirname, in_file)
            if flags.zip_flag:
                log.info(f'zipping {file_path} to {tempfile_path}')
                zipfile.ZipFile(f'{tempfile_path}', mode='w').write(f'{file_path}')
                file_path = tempfile_path

            elif not flags.plain:
                with open(file_path, mode='r') as c:
                    code = c.read()
                with open(tempfile_path, mode='w') as f:
                    lexer = guess_lexer_for_filename(file_path, c)
                    # todo recomended to use css: https://pygments.org/docs/formatters/?highlight=htmlformatter#HtmlFormatter
                    highlight(code, lexer, HtmlFormatter(linenos=True, full=True), outfile=f)
                file_path = tempfile_path
                log.info(f'Highlighted {file_path} with lexer {lexer}.')

            rsync_command = f'rsync -avP {file_path} {ppb_target_host}:{ppb_path_on_host}/{dest_file}'
            log.info(rsync_command)
            os.system(rsync_command)

    log.info(curl_command)
    os.system(curl_command)


if __name__ == '__main__':
    sys.exit(main())
