import os
from flask import Flask, request, render_template, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename
from ultility.predict import yolo 
from PIL import Image
import io

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'files')
OUTPUT_FOLDER = os.path.join(APP_ROOT, 'static/output_files')
INPUT_FOLDER = os.path.join(APP_ROOT, 'static/input_files')

def check_file_extension(filename: str, allow_extensions={'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allow_extensions

def printMsg(*args):
    app.logger.info(msg=args)

@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == 'GET':
        return render_template('uploadpage.html', error=None, fileUrl=None)

    if len(request.files.getlist("file")) != 1:
        return render_template('uploadpage.html', error="Invalid number of files!", fileUrl=None)

    uploadFile = request.files["file"]
    filename = uploadFile.filename

    if not filename:
        filename = "blank_file.jpg"

    i = 0
    filename = secure_filename(filename)
    _file, _extension = os.path.splitext(filename)

    if not os.path.isdir(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)

    while os.path.isfile(os.path.join(OUTPUT_FOLDER, f"{_file}-{i}{_extension}")):
        i += 1

    filename = f"{_file}-{i}{_extension}"

    im_bytes = uploadFile.read()
    im = Image.open(io.BytesIO(im_bytes))
    input_path = os.path.join(INPUT_FOLDER, filename)
    im.save(input_path)
    yolo(os.path.join(APP_ROOT, "yolo", "bests.pt"), im, os.path.join(OUTPUT_FOLDER, filename))

    fileInput = url_for('static', filename=f"input_files/{filename}")
    fileUrl = url_for('static', filename=f"output_files/{filename}")

    return render_template('uploadpage.html', error=None, fileUrl=fileUrl, fileInput=fileInput)

@app.route("/")
def upload_page():
    return render_template('uploadpage.html', error=None, fileUrl=None)

app.run(debug=True)
