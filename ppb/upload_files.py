# HK, 05.01.21
import os
import shutil
import tempfile
import zipfile

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.shell import BashLexer

from ppb import log
from ppb.utils import check_extension, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, COMPRESSION_EXTENSIONS


def upload_file_remote(dest_file, ext, file_path, flags, in_file, ppb_path_on_host, ppb_target_host) -> None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        tempfile_path = os.path.join(tmpdirname, in_file)
        if flags.zip_flag:

            zip_command = f'zip -r {tempfile_path} {file_path}'
            log.info(zip_command)
            os.system(zip_command)
            file_path = tempfile_path

        elif not flags.plain and not check_extension(ext, {
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


def upload_file_local(dest_file, file_path, flags, in_file, ppb_path_on_host) -> None:
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
