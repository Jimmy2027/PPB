import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename

from app import app
from src.ppb import log
from utils import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, check_extension
from ppb_dataframe import update_ppb_dataframe_post, update_ppb_dataframe_get

image_extensions = IMAGE_EXTENSIONS
video_extensions = VIDEO_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('root_template.html')


@app.route('/<filename>', methods=['POST', 'GET'])
def upload_image(filename):
    if request.method == 'GET':
        dateStr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
        ip_address = request.remote_addr

        update_ppb_dataframe_get(values={'last_get_date': dateStr}, filename=filename, ip_address=ip_address)
        log.info(f"reading static/uploads/{filename}")
        if filename.endswith('.pdf'):
            return redirect(f'static/uploads/{filename}', code=301)

        elif check_extension(filename, image_extensions):
            filename = secure_filename(filename)
            return render_template('upload_image.html', filename=filename)
        elif check_extension(filename, video_extensions):
            filename = secure_filename(filename)
            return render_template('upload_video.html', filename=filename)
        elif filename.endswith('.zip'):
            log.info(f'Getting {app.config["UPLOAD_FOLDER"]}/{filename}')
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename=filename)
        elif filename.endswith('.csv'):
            log.info('Uploading as csv.')
            return render_template('upload_csv.html', text=pd.read_csv('static/uploads/{}'.format(filename)).to_html())
            # return "<!DOCTYPE html><html>"  + pd.read_csv(
            #     'static/uploads/{}'.format(filename)).to_html() + "</html>"

        else:
            with open(f'static/uploads/{filename}', 'r') as f:
                file = f.read()
            return render_template('upload_text.html', text=file)

    elif request.method == 'POST':
        file_path = Path(__file__).parent / f'static/uploads/{filename}'
        if file_path.exists():
            ip_address = request.remote_addr
            dateStr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
            filename = request.form.get('filename')
            file_stats = os.stat(file_path)

            log.debug(f'Uploading file {filename}.')
            update_ppb_dataframe_post(values={'sender': ip_address, 'upload_date': dateStr, 'filename': filename,
                                              'file_type': filename.split('.')[-1],
                                              'file_size': file_stats.st_size / (1024 * 1024)}, file_path=file_path)
            return 'sure thing'
        else:
            return 'File not found.'


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=2096)
    # app.run(debug=True)
