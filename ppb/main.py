import os
from flask import flash, request, redirect, url_for, render_template, send_file, send_from_directory
from werkzeug.utils import secure_filename

from app import app
from ppb_dataframe import update_ppb_dataframe_post, update_ppb_dataframe_get
from datetime import datetime
import os
from logger.logger import log

# todo have different folder for every file type

image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
video_extensions = {'mov', 'mp4'}


def check_extension(filename, extension_list):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extension_list


@app.route('/')
def upload_form():
    return "<h1>Hello there</h1>"


@app.route('/file/<filename>', methods=['POST', 'GET'])
def upload_image(filename):
    if request.method == 'GET':
        dateStr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")

        update_ppb_dataframe_get(values={'last_get_date': dateStr}, filename=filename)

        if filename.endswith('.pdf'):
            filename = secure_filename(filename)
            return render_template('upload_pdf.html', filename=filename)
        elif check_extension(filename, image_extensions):
            print('getting image!!!')
            filename = secure_filename(filename)
            print(render_template('upload_image.html', filename=filename))
            return render_template('upload_image.html', filename=filename)
        elif check_extension(filename, video_extensions):
            filename = secure_filename(filename)
            return render_template('upload_video.html', filename=filename)
        elif filename.endswith('.zip'):
            # return render_template('upload_zip.html', filename=filename)
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename=filename)
        elif filename.endswith('.csv'):
            import pandas as pd
            # file = open('static/uploads/{}'.format(filename))
            # return render_template('csv_template.html', text=pd.read_csv('static/uploads/{}'.format(filename)).to_html())
            return "<!DOCTYPE html><html>" + pd.read_csv('static/uploads/{}'.format(filename)).to_html() + "</html>"
        else:
            file = open('static/uploads/{}'.format(filename))
            return render_template('upload_text.html', text=file.read())
    elif request.method == 'POST':
        file_path = f'../static/uploads/{filename}'
        ip_address = request.remote_addr
        dateStr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
        filename = request.form.get('filename')
        file = open(file_path)
        file_stats = os.stat(file_path)

        update_ppb_dataframe_post(values={'sender': ip_address, 'upload_date': dateStr, 'filename': filename,
                                          'file_type': filename.split('.')[-1],
                                          'file_size': file_stats.st_size / (1024 * 1024)})

        if filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        elif file and check_extension(filename, image_extensions):
            filename = secure_filename(filename)
            print('uploading image!!!')
            return render_template('upload_image.html', filename=filename)
        elif file and filename.endswith('.pdf'):
            print('uploading pdf!!!')
            filename = secure_filename(filename)
            return render_template('upload_pdf.html', filename=filename)
        elif file and check_extension(filename, video_extensions):
            filename = secure_filename(filename)
            print('upload video!!!')
            return render_template('upload_video.html', filename=filename)
        elif file and filename.endswith('.zip'):
            print('upload_zip!!!')
            filename = secure_filename(filename)
            return redirect(url_for('upload_image',
                                    filename=filename))
        else:
            print('File extention not recognized, uploading as text')
            return render_template('upload_text.html', text=file.read())


@app.route('/display/<filename>')
def display_image(filename):
    print(filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/display/<filename>')
def show_static_pdf():
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'exam_3.pdf'), 'rb') as static_file:
        return send_file(static_file, attachment_filename='file.pdf')


@app.route('/users/<user_id>', methods=['GET', 'POST', 'DELETE'])
def user(user_id):
    if request.method == 'GET':
        """return the information for <user_id>"""
        return 'hello {}'.format(user_id)
    if request.method == 'POST':
        """modify/update the information for <user_id>"""
        # you can use <user_id>, which is a str but could
        # changed to be int or whatever you want, along
        # with your lxml knowledge to make the required
        # changes
        data = request.form.get('data')  # a multidict containing POST data
        return 'The data is {}'.format(data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
    # app.run(debug=True)
