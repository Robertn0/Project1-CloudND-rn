import os
import logging
from flask import Flask, redirect, request, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
from google.cloud import storage

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Google Cloud Storage settings
BUCKET_NAME = "proj1-rn"
PROJECT_ID = "project-roberto-napoles"
storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)

# Ensure the directory exists
local_directory = os.path.join('files', BUCKET_NAME)
os.makedirs(local_directory, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def index():
    files = list_files()
    index_html = """
    <form method="post" enctype="multipart/form-data" action="/upload">
      <div>
        <label for="file">Choose file to upload (JPEG only)</label>
        <input type="file" id="file" name="form_file" accept="image/jpeg">
      </div>
      <div>
        <button>Submit</button>
      </div>
    </form>
    <ul>
    """
    for file in files:
        index_html += f"<li>{file} - <a href='/files/{file}'>View</a> | <a href='/delete/{file}'>Delete</a></li>"
    index_html += "</ul>"
    return index_html

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files['form_file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(local_directory, filename)
        file.save(file_path)
        upload_to_bucket(file_path, filename)
        return redirect(url_for('index'))
    return 'Invalid file type or upload failed', 400

@app.route('/files/<filename>')
def get_file(filename):
    try:
        logging.debug(f'Attempting to send file: {filename}')
        return send_from_directory(local_directory, filename)
    except Exception as e:
        logging.error(f'Failed to send file with error: {e}')
        abort(500, description=f"Internal Server Error: {e}")

@app.route('/delete/<filename>')
def delete(filename):
    try:
        file_path = os.path.join(local_directory, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            delete_from_bucket(filename)
            return redirect(url_for('index'))
        else:
            abort(404, description="File not found")
    except Exception as e:
        logging.error(f'Failed to delete file with error: {e}')
        abort(500, description=f"Internal Server Error: {e}")

def list_files():
    return [f for f in os.listdir(local_directory) if f.lower().endswith(('.jpeg', '.jpg'))]

def upload_to_bucket(file_path, filename):
    blob = bucket.blob(filename)
    blob.upload_from_filename(file_path)

def delete_from_bucket(filename):
    blob = bucket.blob(filename)
    blob.delete()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpeg', 'jpg'}

if __name__ == '__main__':
    app.run(debug=True)

