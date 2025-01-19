import os
from flask import Flask, redirect, request, send_from_directory, url_for, render_template_string

# Ensure the directory exists
os.makedirs('files', exist_ok=True)

app = Flask(__name__)

@app.route('/')
def index():
    # Generate HTML form and list existing files with view and delete options
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
    files = list_files()
    for file in files:
        index_html += f"<li>{file} - <a href='/files/{file}'>View</a> | <a href='/delete/{file}'>Delete</a></li>"
    index_html += "</ul>"
    return index_html

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files['form_file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('./files', filename)
        file.save(file_path)
        return redirect(url_for('index'))
    return 'Invalid file type or upload failed', 400

@app.route('/files')
def list_files():
    return [f for f in os.listdir('./files') if f.lower().endswith(('.jpeg', '.jpg'))]

@app.route('/files/<filename>')
def get_file(filename):
    return send_from_directory('./files', filename)

@app.route('/delete/<filename>')
def delete(filename):
    file_path = os.path.join('./files', filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for('index'))
    return 'File not found', 404

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpeg', 'jpg'}

def secure_filename(filename):
    """Use Werkzeug's secure_filename to sanitize the file name."""
    from werkzeug.utils import secure_filename
    return secure_filename(filename)

if __name__ == '__main__':
    app.run(debug=True)
