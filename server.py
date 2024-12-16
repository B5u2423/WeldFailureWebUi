import os
from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
from ultility.predict import yolo 
from PIL import Image
import io

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(APP_ROOT, 'static/output_files')
INPUT_FOLDER = os.path.join(APP_ROOT, 'static/input_files')

# Image from get request will be temporarily saved to INPUT_FOLDER.
# Defects dectecion image will be temporarily saved to OUTPUT_FOLDER.
# All will be deleted upon exiting the program.
@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == 'GET':
        return render_template('uploadpage.html', error=None, fileUrl=None)

    # Allow only 1 image at a time
    if len(request.files.getlist("file")) != 1:
        return render_template('uploadpage.html', error="Invalid number of files!", fileUrl=None)

    uploadFile = request.files["file"]
    filename = uploadFile.filename
    if not filename:
        filename = "blank_file.jpg"

    i = 0
    filename = secure_filename(filename)
    _file, _extension = os.path.splitext(filename)

    # create output and input folder if not found
    if not os.path.isdir(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)
    if not os.path.isdir(INPUT_FOLDER):
        os.mkdir(INPUT_FOLDER)

    while os.path.isfile(os.path.join(OUTPUT_FOLDER, f"{_file}-result-{i}{_extension}")):
        i += 1

    input_filename = f"{_file}-{i}{_extension}"
    output_filename = f"{_file}-result-{i}{_extension}"

    im_bytes = uploadFile.read()
    im = Image.open(io.BytesIO(im_bytes))
    input_path = os.path.join(INPUT_FOLDER, input_filename)
    im.save(input_path)
    yolo(os.path.join(APP_ROOT, "yolo", "bests.pt"), im, os.path.join(OUTPUT_FOLDER, output_filename))

    fileInput = url_for('static', filename=f"input_files/{input_filename}")
    fileUrl = url_for('static', filename=f"output_files/{output_filename}")

    return render_template('uploadpage.html', error=None, fileUrl=fileUrl, fileInput=fileInput)

@app.route("/")
def upload_page():
    return render_template('uploadpage.html', error=None, fileUrl=None)

# delete all temp input and output files
def clean_folder(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try: 
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting files {e}")

app.run(debug=True)
clean_folder(OUTPUT_FOLDER)
clean_folder(INPUT_FOLDER)
