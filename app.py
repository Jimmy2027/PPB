from flask import Flask
import configparser
import os

config_file = configparser.RawConfigParser()
config_file.read(os.path.expanduser('~/.config/ppb.conf'))
UPLOAD_FOLDER = config_file['ppb_config']['PPB_PATH_ON_HOST'].replace("'", '')

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_url_path = UPLOAD_FOLDER
