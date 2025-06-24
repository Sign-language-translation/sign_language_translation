from flask import Flask, request, jsonify
import sys
import os
import uuid
from werkzeug.utils import secure_filename
from flask import url_for
from openai import AzureOpenAI
import cv2
from flask import send_from_directory
from flask_cors import CORS

# Add the parent directory of the backend folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codes_translation.translate_sentence import translate_video_to_text
from codes_translation.translate_single_word import classify_single_word

AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

TEMP_FOLDER_PATH_OF_JSONS = 'json_files'

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

        # # Extract keypoints
        # data_frames = extract_motion_data("backend/"+ UPLOAD_FOLDER + "/" + filename)

        # Process with appropriate model based on mode
        result = translate_sign_language(filename, file_path, mode)

        return jsonify({"translation": result}), 200
    else:
        return jsonify({"error": "Invalid file format"}), 400

# Example function to simulate translation
def translate_sign_language(filename, file_path, mode='sentence'):
    try:
        model_filename = os.path.join(os.path.dirname(__file__), '../models/model-5_14000_vpw.keras')
        label_encoder_path = os.path.join(os.path.dirname(__file__), '../models/label_encoder_model-5_14000_vpw.pkl')

        if mode == 'word':
            result = classify_single_word(UPLOAD_FOLDER, filename, TEMP_FOLDER_PATH_OF_JSONS, model_filename, label_encoder_path)
        elif mode == 'sentence':

            result = translate_video_to_text(file_path, model_filename, label_encoder_path)
        else:
            return f"Unknown mode: {mode}"


        # # Load the label encoder
        # label_encoder = load_label_mapping(label_encoder_path)

        # # Get the classification result
        # predicted_label = classify_json_file(model_filename, data_frames, label_encoder)
        # print(f"[{mode}] Predicted label: {predicted_label}")

        return result

    except FileNotFoundError as e:
        return f"File not found: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


def convert_sentence_to_list_of_existing_words_using_gpt(sentence):
    endpoint = os.getenv("ENDPOINT_URL", "https://isl-translation.openai.azure.com/")
    deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY", AZURE_OPENAI_API_KEY)

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2024-05-01-preview",
    )

    prompt = f"""
    Given the following sentence in Hebrew:

    "{sentence}"

    And a list of allowed Hebrew words with their English meanings:
    And a list of allowed Hebrew words with their English meanings:
    hello: שלום, thanks: תודה, need: צריך, now: עכשיו, when: מתי, why: למה, appointment: תור,
    schedule: לקבוע, arrive: להגיע, station: תחנה, bus: אוטובוס, phone: טלפון, place: מקום,
    help: לעזור, name: שם, no: לא, go: ללכת, come: לבוא, I: אני, you: אתה, home: בית,
    ticket: כרטיס, later: אחר כך, doctor: רופא, idCard: תעודת זהות, ambulance: אמבולנס,
    clinic: קופת חולים, tomorrow: מחר, yesterday: אתמול, youreWelcome: בבקשה,
    how: איך, can: יכול, time: שעה, 1: אחד, 2: שתיים, 3: שלוש, 4: ארבע,
    5: חמש, 6: שש, 7: שבע, 8: שמונה, 9: תשע, 10: עשר,
    11: אחת עשרה, 12: שתים עשרה, 13: שלוש עשרה, 14: ארבע עשרה,
    15: חמש עשרה, 16: שש עשרה, 17: שבע עשרה, 18: שמונה עשרה,
    19: תשע עשרה, 20: עשרים

    Your task is to:
    1. Extract the words from the sentence that match (or closely match) the Hebrew words in the list. 
       - Convert conjugated, inflected, or gendered forms to the base form in the list  
         (e.g. 'ארצה' will become 'אני רוצה'
            'תרצה' will become 'אתה רוצה'
            'צריכה' will become 'צריך')
       - Remove common prefixes such as 'ב', 'ל', 'כ', 'ש', 'ה'  
         (e.g. 'לתחנת' → 'תחנה', 'באוטובוס' → 'אוטובוס')

    2. For each matched Hebrew word, replace it with its English equivalent using the list above.

    Important: Only use the exact English translations from the list provided above. Do not add any extra words such as "to", "the", or anything that is not part of the list. Maintain the original word order from the sentence.

    Output only the final result as a space-separated list of English words. Do not include any Hebrew, explanations, or punctuation.
    """

    chat_prompt = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    completion = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        temperature=0.7,
        max_tokens=256
    )

    # return completion.choices[0].message.content.strip()
    return completion.choices[0].message.content

@app.route('/generate_video', methods=['POST'])
def generate_video():
    # Prepare a list to store video clips
    video_clips = []
    final_clip = None

    try:
        # Get the text from the request
        data = request.get_json()
        print("📥 Received data:", data)
        text = data.get('text', '')
        print("✏️ Text to convert:", text)

        if not text.strip():
            return jsonify({"error": "No text provided"}), 400

        text = convert_sentence_to_list_of_existing_words_using_gpt(text)
        print("sentence after gpts work = " + text)
        # Format filename from text
        safe_filename = text.strip().lower().replace(" ", "_") + ".mp4"
        output_folder = os.path.join("static", "generated_videos")
        # output_folder = os.path.abspath(os.path.join("static", "generated_videos"))
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, safe_filename)

        # safe_filename = text.strip().lower().replace(" ", "_") + ".mp4"
        # base_dir = os.path.dirname(os.path.abspath(__file__))
        # output_folder = os.path.join(base_dir, "static", "generated_videos")
        # os.makedirs(output_folder, exist_ok=True)
        # output_path = os.path.join(output_folder, safe_filename)



        # If video already exists, return it
        if os.path.exists(output_path):
            print(f"📦 Found existing video for: {text}")
            video_url = url_for('static',filename=f"generated_videos/{safe_filename}", _external=True)
            return jsonify({ "video_url": video_url })

        # Split the text into words
        words = text.strip().lower().split()

        video_paths = []
        missing_words = []

        # for word in words:
        #     # video_path = os.path.abspath(os.path.join(VIDEO_FOLDER, f"{word}.mp4"))
        #
        #     # Always resolve relative to the location of app.py
        #     base_dir = os.path.dirname(os.path.abspath(__file__))
        #     video_folder = os.path.join(base_dir, "videos")
        #
        #     # Now build the full path safely
        #     video_path = os.path.join(video_folder, f"{word}.mp4")
        #
        #     print("video_path = " + video_path)
        #     if os.path.exists(video_path):
        #         video_paths.append(video_path)
        #     else:
        #         print(f"⚠️ Video for word '{word}' not found.")
        #         missing_words.append(word)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        video_folder = os.path.join(base_dir, "videos")

        for word in words:
            video_path = os.path.join(video_folder, f"{word}.mp4")
            print("video_path = " + video_path)
            if os.path.exists(video_path):
                video_paths.append(video_path)
            else:
                print(f"⚠️ Video for word '{word}' not found.")
                missing_words.append(word)

        if not video_paths:
            return jsonify({
                "error": "No valid word videos found.",
                "missing_words": missing_words
            }), 400

        success = concatenate_videos(video_paths, output_path)
        if not success:
            return jsonify({"error": "Video processing failed"}), 500

        # return send_file(output_path, as_attachment=True)
        video_url = url_for('static', filename=f"generated_videos/{safe_filename}", _external=True)

        return jsonify({"video_url": video_url})

    except Exception as e:
        print("❌ Error during video generation:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/static/generated_videos/<path:filename>')
def serve_generated_video(filename):
    return send_from_directory('static/generated_videos', filename)

def concatenate_videos(video_paths, output_path, fps=30):
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # More browser-compatible than 'mp4v'
    all_frames = []
    frame_size = None

    for video_path in video_paths:
        if not os.path.exists(video_path):
            print(f"⚠️ Warning: {video_path} not found. Skipping.")
            continue

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Error opening video file: {video_path}")
            continue

        if frame_size is None:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or fps
            frame_size = (width, height)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame.shape[1::-1] != frame_size:
                frame = cv2.resize(frame, frame_size)
            all_frames.append(frame)

        cap.release()

    if not all_frames:
        print("🚫 No valid frames found.")
        return False

    # Write all frames to a new video
    out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
    for frame in all_frames:
        out.write(frame)
    out.release()
    print(f"✅ Final video written to: {output_path}")
    return True



if __name__ == '__main__':
    app.run(debug=True, port=3000)
