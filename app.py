from flask import Flask,render_template,request,redirect,url_for,jsonify
import os,time,dotenv,shutil
from flask_cors import CORS
from chatpdf.ask_ollama import main as ask_ollama
from chatpdf.create_db import main as create_db
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/chat", methods=['POST', 'GET'])
def chat():
    if request.method == 'POST':
        if 'chatPdfFile' not in request.files:
            return redirect(url_for('index'))
        file = request.files['chatPdfFile']
        if file.filename == '':
            return redirect(url_for('index'))
        if not allowed_file(file.filename):
            return redirect(url_for('index'))
        
        # Check if the upload directory exists, if not, create it
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        else:
            # Clean the directory
            clean_directory(UPLOAD_FOLDER)
        
        # Add timestamp to the file name to ensure uniqueness
        timestamp = int(time.time())
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        db_response=create_db(f'{file_path}')
        if db_response is False:
            return redirect(url_for('index'))
        return render_template('chat.html', file_path=filename)
    else:
        return render_template('chat.html')

@app.route("/api/chat", methods=['POST'])
def pdfchat():
    print(request.method, request.is_json)
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        if 'prompt' in data:
            prompt = data['prompt']
            response = ask_ollama(prompt)
            return jsonify({"text": response}), 200
        else:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
    else:
        return jsonify({"error": "Invalid request method"}) , 400

if __name__ == "__main__":
    app.run()