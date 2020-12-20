import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename

from app import app
from ppb import log
from ppb_dataframe import update_ppb_dataframe_post, update_ppb_dataframe_get

image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
video_extensions = {'mov', 'mp4'}


def check_extension(filename, extension_list):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extension_list


@app.route('/file/<filename>', methods=['POST', 'GET'])
def upload_image(filename):
    if request.method == 'GET':
        dateStr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")

        update_ppb_dataframe_get(values={'last_get_date': dateStr}, filename=filename)
        log.info(f"reading static/uploads/{filename}")
        if filename.endswith('.pdf'):
            filename = secure_filename(filename)
            return render_template('upload_pdf.html', filename=filename)
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
            return "<!DOCTYPE html><html>" + pd.read_csv('static/uploads/{}'.format(filename)).to_html() + "</html>"

        else:
            with open(f'static/uploads/{filename}', 'r') as f:
                file = f.read()
            return "<!DOCTYPE html><html>" + file + "</html>"

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
                                              'file_size': file_stats.st_size / (1024 * 1024)})
            return 'sure thing'
        else:
            return 'File not found.'


@app.route('/display/<filename>')
def display_image(filename):
    print(filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
    # app.run(debug=True)
