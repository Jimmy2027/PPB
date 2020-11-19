import os
from flask import flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename

from app import app

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
    if request.method == 'POST':
        filename = request.form.get('filename')
        file = open('../static/uploads/{}'.format(filename))
        print(filename)
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
            print(os.getcwd(), 'hallo')
            return render_template('upload_text.html', text=file.read())

    if request.method == 'GET':
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
            return render_template('upload_zip.html', filename=filename)
        else:
            file = open('static/uploads/{}'.format(filename))
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