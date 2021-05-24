import os
import tempfile
from pathlib import Path
from typing import Set

from src.ppb import log

IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
VIDEO_EXTENSIONS = {'mov', 'mp4'}
COMPRESSION_EXTENSIONS = {'zip', 'tar', 'gz'}

GIT_ICON_HTML = '<head><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css"><style type="text/css">.fa_custom {color: #000000;}</style></head><body><a href="https://github.com/Jimmy2027/PPB"><i class="fa fa-github fa-3x" style="float:right"></i></a></body>'


def check_extension(filename: str, extension_list: Set[str]) -> bool:
    """
    Returns true if the file extension is found in the extension list.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extension_list


def get_unique_str(prefix: str = '') -> str:
    from datetime import datetime
    dateTimeObj = datetime.now()
    dateStr = dateTimeObj.strftime("%Y_%m_%d_%H_%M_%S_%f")
    if prefix:
        return '_'.join([prefix, dateStr])
    else:
        return dateStr


def maybe_getfrom_ppb(download_url: str, out_path: Path):
    """Download from ppb and extract to out_path if not already there."""
    filename = Path(download_url).stem
    if not out_path.exists():
        out_path.mkdir()
        log.info(f'{out_path} does not exist. Downloading...')
        with tempfile.TemporaryDirectory() as tmpdirname:
            wget_command = f'wget {download_url} -P {tmpdirname}/'
            log.info(f'Getting {download_url}.')
            os.system(wget_command)

            unzip_command = f'unzip {tmpdirname}/{filename + ".zip"} -d {out_path}/'
            os.system(unzip_command)
    else:
        log.info(f'{out_path} exists. Skipping...')


if __name__ == '__main__':
    maybe_getfrom_ppb('https://ppb.hendrikklug.xyz/4959123face8.zip', Path('~/polymnistmodels').expanduser())
