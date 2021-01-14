# HK, 17.12.20
from typing import Set

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
