from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import uuid
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip, concatenate_videoclips
from flask import url_for

# Add the parent directory of the backend folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from resources.test_mediapipe import extract_motion_data
from classification import load_label_mapping,classify_json_file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the folder where the word videos are stored
VIDEO_FOLDER = 'videos'  


# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['video']
    mode = request.form.get('mode', 'sentence') 

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"Video uploaded: {file_path}, Mode: {mode}")

        # Extract keypoints
        data_frames = extract_motion_data("backend/"+ UPLOAD_FOLDER + "/" + filename)

        # Process with appropriate model based on mode
        result = translate_sign_language(data_frames, mode)

        return jsonify({"translation": result}), 200
    else:
        return jsonify({"error": "Invalid file format"}), 400

# Example function to simulate translation
def translate_sign_language(data_frames, mode='sentence'):
    try:
        if mode == 'word':
            model_filename = os.path.join(os.path.dirname(__file__), '../models/3d_rnn_cnn_on_50_vpw.keras')
            label_encoder_path = os.path.join(os.path.dirname(__file__), '../models/label_encoder_3d_rnn_cnn.pkl')
        elif mode == 'sentence':
            model_filename = os.path.join(os.path.dirname(__file__), '../models/sentence_model.keras')
            label_encoder_path = os.path.join(os.path.dirname(__file__), '../models/sentence_label_encoder.pkl')
        else:
            return f"Unknown mode: {mode}"


        # Load the label encoder
        label_encoder = load_label_mapping(label_encoder_path)

        # Get the classification result
        predicted_label = classify_json_file(model_filename, data_frames, label_encoder)
        print(f"[{mode}] Predicted label: {predicted_label}")

        return predicted_label

    except FileNotFoundError as e:
        return f"File not found: {e}"
    except Exception as e:
        return f"An error occurred: {e}"
    
@app.route('/generate_video', methods=['POST'])
def generate_video():
    try:
        # Get the text from the request
        data = request.get_json()
        print("📥 Received data:", data)
        text = data.get('text', '')
        print("✏️ Text to convert:", text)

        if not text.strip():
            return jsonify({"error": "No text provided"}), 400

        # Format filename from text
        safe_filename = text.strip().lower().replace(" ", "_") + ".mp4"
        output_folder = os.path.join("static", "generated_videos")
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, safe_filename)

        # If video already exists, return it
        if os.path.exists(output_path):
            print(f"📦 Found existing video for: {text}")
            video_url = url_for('static',filename=f"generated_videos/{safe_filename}", _external=True)
            return jsonify({ "video_url": video_url })

        # Split the text into words
        words = text.strip().lower().split()

        # Prepare a list to store video clips
        video_clips = []

        for word in words:
            video_path = os.path.join(VIDEO_FOLDER, f"{word}.mp4")
            
            # Check if the video file exists
            if os.path.exists(video_path):
                clip = VideoFileClip(video_path)
                video_clips.append(clip)
            else:
                print(f"⚠️ Warning: Video for word '{word}' not found at {video_path}")

        if not video_clips:
            return jsonify({
            "error": "No translation found for the given text.",
            "missing_words": words
        }), 400

        # Concatenate all video clips
        final_clip = concatenate_videoclips(video_clips, method="compose")

        # Write the final video
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

        # Close clips
        for clip in video_clips:
            clip.close()
        final_clip.close()

        # return send_file(output_path, as_attachment=True)
        video_url = url_for('static', filename=f"generated_videos/{safe_filename}", _external=True)

        return jsonify({ "video_url": video_url })

    except Exception as e:
        print("❌ Error during video generation:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
