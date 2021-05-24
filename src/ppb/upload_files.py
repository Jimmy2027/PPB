import configparser
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.shell import BashLexer

from ppb import log
from utils import check_extension, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, COMPRESSION_EXTENSIONS
from utils import get_unique_str


def upload(file_path: Path, zip_flag: bool = False, plain: bool = False, description: str = None, lifetime: int = 20):
    """Upload file to ppb server."""
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.config/ppb.conf'))
    ppb_target_host = config['ppb_config']['PPB_TARGET_HOST'].replace("'", '')
    ppb_path_on_host = config['ppb_config']['PPB_PATH_ON_HOST'].replace("'", '')
    ppb_http_path = config['ppb_config']['PPB_HTTP_PATH'].replace("'", '')
    sender_name = config['other']['SENDER_NAME'].replace("'", '')

    if not ppb_target_host:
        print("ERROR: The PPB_TARGET_HOST variable is unset."
              "Nothing can be uploaded if there is no target host."
              "Please copy the example config file from under \"/etc/ppb.conf\" to \"~/.config/ppb.conf\","
              "and fill in the variable values according to your personal settings.")

    # when running on host, ppb_http_path = ppb_path_on_host
    if not ppb_http_path:
        ppb_http_path = ppb_path_on_host

    file_stem = get_unique_str(file_path.stem)
    file_id = hashlib.md5(file_stem.encode('utf-8')).hexdigest()
    dest_file = file_id[:12]
    ext = file_path.suffix

    # if zipping file, add .zip extension
    dest_file += f'{ext}' + '.zip' * zip_flag
    dest_file = Path(dest_file)

    in_file = dest_file

    file_url = f'{ppb_http_path}/{in_file}'
    curl_command = f'curl -X POST --silent --output /dev/null --show-error ' \
                   f'--fail {file_url} -d filename={dest_file} '

    metadata = {
        'lifetime': lifetime,
        'description': description,
        'orig_filename': str(file_path.stem) + ext,
        'sender': sender_name
    }

    # send file to where it will be read by flask app
    if ppb_target_host == 'local':
        upload_file_local(dest_file, file_path, zip_flag, plain, in_file, ppb_path_on_host, metadata)
    else:
        upload_file_remote(dest_file, ext, file_path, zip_flag, plain, in_file, ppb_path_on_host, ppb_target_host,
                           metadata=metadata)

    log.info(curl_command)
    os.system(curl_command)
    log.info(f'Uploaded to {file_url}')

    return file_url


def upload_file_remote(dest_file: Path, ext: str, file_path: Path, zip_flag, plain, in_file, ppb_path_on_host,
                       ppb_target_host,
                       metadata: dict) -> None:
    """
    dest_file: destination filename + extension (example: 77a80349869f.png)
    ext: file extension, like dest_file.suffix
    file_path: path to input file.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        send_metadata(dest_file, metadata, ppb_path_on_host, ppb_target_host, tmpdirname)
        tempfile_path = os.path.join(tmpdirname, in_file)
        if zip_flag:

            zip_command = f'zip -r {tempfile_path} {file_path}'
            log.info(zip_command)
            os.system(zip_command)
            file_path = tempfile_path

        elif not plain and not check_extension(ext, {
            *IMAGE_EXTENSIONS,
            *VIDEO_EXTENSIONS,
            *COMPRESSION_EXTENSIONS,
            '',
            'pdf'
        }):
            with open(file_path, mode='r') as c:
                code = c.read()
            with open(tempfile_path, mode='w') as f:
                if ext == '.log':
                    lexer = BashLexer()
                else:
                    try:
                        lexer = guess_lexer_for_filename(file_path, c)
                    except Exception as e:
                        print(e)
                try:
                    highlight(code, lexer, HtmlFormatter(linenos=True, full=True), outfile=f)
                except:
                    # if pygments fails to find a lexer, continue without highlighting
                    tempfile_path = file_path
                    lexer = None
            file_path = tempfile_path
            log.info(f'Highlighted {file_path} with lexer {lexer}.')

        rsync_command = f'rsync -avP {file_path} {ppb_target_host}:{ppb_path_on_host}/{dest_file}'
        log.info(rsync_command)
        os.system(rsync_command)


def send_metadata(dest_file, metadata: dict, ppb_path_on_host, ppb_target_host, tmpdirname):
    """
    Sends metadata json file to ppb host.
    """
    out_metadata_filename = dest_file.stem + '.json'
    metadata_file_path = os.path.join(tmpdirname, out_metadata_filename)
    with open(metadata_file_path, 'w') as outfile:
        json.dump(metadata, outfile)
    rsync_metadata_command = f'rsync -avP {metadata_file_path} {ppb_target_host}:{ppb_path_on_host}/{out_metadata_filename}'
    log.info(rsync_metadata_command)
    os.system(rsync_metadata_command)


def upload_file_local(dest_file, file_path, zip_flag, plain, in_file, ppb_path_on_host, metadata: dict) -> None:
    if zip_flag:
        zip_command = f'zip -r {ppb_path_on_host}/{in_file} {file_path}'
        log.info(zip_command)
        os.system(zip_command)
    else:
        dest_path = os.path.join(ppb_path_on_host, dest_file)
        if plain:
            shutil.copyfile(file_path, dest_path)
        else:
            with open(file_path, mode='r') as c:
                code = c.read()
            with open(dest_path, mode='w') as f:
                highlight(code, guess_lexer_for_filename(file_path, c), HtmlFormatter(linenos=True, full=True),
                          outfile=f)
            log.info(f'Highlighted {file_path}.')
