from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import uuid
from werkzeug.utils import secure_filename

# Add the parent directory of the backend folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from resources.test_mediapipe import extract_motion_data
from classification import load_label_mapping,classify_json_file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['video']
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"Video uploaded: {file_path}")

        data_frames = extract_motion_data("backend/"+ UPLOAD_FOLDER + "/" + filename)

        # Here, you would process the video with your ML model
        result = translate_sign_language(data_frames)

        return jsonify({"translation": result}), 200
    else:
        return jsonify({"error": "Invalid file format"}), 400

# Example function to simulate translation
def translate_sign_language(data_frames):
    try:
        # Define paths to model and label encoder
        model_filename = os.path.join(os.path.dirname(__file__), '../models/3d_rnn_cnn_on_50_vpw.keras')
        label_encoder_path = os.path.join(os.path.dirname(__file__), '../models/label_encoder_3d_rnn_cnn.pkl')


        # Load the label encoder
        label_encoder = load_label_mapping(label_encoder_path)

        # Get the classification result
        predicted_label = classify_json_file(model_filename, data_frames, label_encoder)

        print("label: "  + predicted_label)

        return predicted_label

    except FileNotFoundError as e:
        return f"File not found: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(port=3000, debug=True)
