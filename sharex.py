#!/usr/bin/python
# encoding: utf-8

import os
import sys
import io
import hashlib
import tempfile
from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from conf import UPLOAD_FOLDER, IMG_UPLOAD_FOLDER, FILE_UPLOAD_FOLDER, TEXT_UPLOAD_FOLDER, ALLOWED_EXT, HOST, PORT, DEBUG, APP_HOST

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# TOOLS

def hash_file(file):
    return hashlib.sha1(file.read()).hexdigest()

# random file name
def get_name(filename, prefix):
    tmp = tempfile.NamedTemporaryFile(prefix=prefix, suffix='.' + filename.rsplit('.', 1)[1].lower())
    name = str(tmp.name).rsplit('/', 1)[1]
    tmp.close()
    return str(name)

#check filename validity
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

#check and save file and return url
def get_file(folder, prefix, ret_func):
    if ('Content-Type' not in request.headers and request.headers['Content-Type'] != 'multipart/form-data') or 'file' not in request.files:
        return jsonify(status='fail'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(status='failed', reason='no file'), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        stock_filename = get_name(filename, prefix)
        file.save(os.path.join(folder, stock_filename))
        return jsonify(status='OK', link=APP_HOST + url_for(ret_func, filename=stock_filename))
    return jsonify(status='KO'), 400

## HOME

@app.route('/', methods=['GET'])
def home():
    return ';)', 200

## IMG

@app.route('/upload-img/', methods=['POST'])
def upload_img():
    return get_file(IMG_UPLOAD_FOLDER, 'IMG', 'img')

@app.route('/img/<string:filename>', methods=['GET'])
def img(filename):
    return send_from_directory(IMG_UPLOAD_FOLDER, filename)

## FILES

@app.route('/upload-file/', methods=['POST'])
def upload_file():
    return get_file(FILE_UPLOAD_FOLDER, 'Fi', 'files')

@app.route('/files/<string:filename>', methods=['GET'])
def files(filename):
    return send_from_directory(FILE_UPLOAD_FOLDER, filename)

## TEXT

@app.route('/upload-text/', methods=['POST'])
def upload_text():
    if 'Content-Type' not in request.headers and request.headers['Content-Type'] != 'application/x-www-form-urlencoded':
        return jsonify(status='KO'), 400
    name = get_name('ex.txt', 'TXT')
    with open(os.path.join(TEXT_UPLOAD_FOLDER, name), 'wb+') as f:
        f.write(request.form['text'])
    return jsonify(status='OK', link=APP_HOST + url_for('txt', filename=name)), 200

@app.route('/text/<string:filename>', methods=['GET'])
def txt(filename):
    return send_from_directory(TEXT_UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
