import os
import json
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from keras.layers import TFSMLayer
from utils.conver_json_to_vector import create_feature_vector
from utils.test_mediapipe import extract_motion_data, motion_data_to_json

# -----------------------------------------------------------------------------
# Helpers: force CPU, load JSON, load labels
# -----------------------------------------------------------------------------
# 1) Force TF to CPU-only (no GPU / XLA)
tf.config.set_visible_devices([], "GPU")
tf.config.optimizer.set_jit(False)

def read_json_file(file_path):
    """Reads a JSON file and returns its content (or None on error)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ JSON load error at {file_path}: {e}")
        return None

def load_label_mapping(file_path):
    """Load and return list(label_encoder.classes_) from a .pkl file."""
    with open(file_path, 'rb') as f:
        le = pickle.load(f)
    print(f"Label encoder loaded from {file_path}")
    return list(le.classes_)

# -----------------------------------------------------------------------------
# Model loader: .keras/.h5 or SavedModel → returns a Keras model or TFSMLayer
# -----------------------------------------------------------------------------
def _load_model_cpu_only(model_path: str):
    """
    Load either a native Keras .keras/.h5 file, or wrap a TF SavedModel
    directory in a TFSMLayer (inference-only).
    """
    if model_path.endswith(('.keras', '.h5')):
        # native Keras format
        return load_model(model_path, compile=False)
    else:
        # assume TF SavedModel directory
        # serving_default is the standard signature name; adjust if needed
        return TFSMLayer(model_path, call_endpoint="serving_default")

# -----------------------------------------------------------------------------
# Core classification functions
# -----------------------------------------------------------------------------
def classify_json_file(model_path, json_content, label_mapping):
    """
    Given your loaded model path, a precomputed JSON dict, and the
    list of class labels, return the predicted label string.
    """
    model = _load_model_cpu_only(model_path)

    # build the feature‐vector (T×H×W×C) from your JSON
    input_matrix = create_feature_vector(json_content)

    # reshape into batch of length 1
    # adjust (50,75,3) if your model expects a different shape
    reshaped = input_matrix.reshape((1, *input_matrix.shape))

    preds = model.predict(reshaped)
    class_idx = int(np.argmax(preds, axis=-1)[0])
    return label_mapping[class_idx]

def classify_single_word(input_video_folder, video_filename,
                         temp_json_folder, model_path, label_encoder_path):
    """
    1) trim + extract motion → JSON (via your MediaPipe helper)
    2) load that JSON, run classify_json_file, print & return
    """
    video_path = os.path.join(input_video_folder, video_filename)
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return None

    name = os.path.splitext(video_filename)[0]
    # 1) extract motion & write JSON
    trim = extract_motion_data(name, folder_name=input_video_folder)
    motion_data_to_json(trim, name, folder_name=temp_json_folder)

    # 2) read JSON back
    json_content = read_json_file(os.path.join(temp_json_folder, f"{name}.json"))
    if json_content is None:
        return None

    # 3) load labels & classify
    labels = load_label_mapping(label_encoder_path)
    pred = classify_json_file(model_path, json_content, labels)

    print(f"Real: {name} → Predicted: {pred}")
    return pred

def classify(input_folder_of_videos, temp_json_folder,
             model_path, label_encoder_path):
    """
    Batch‐classify every .mp4 in a folder.
    """
    for fn in os.listdir(input_folder_of_videos):
        if fn.lower().endswith(".mp4"):
            classify_single_word(input_folder_of_videos, fn,
                                 temp_json_folder, model_path, label_encoder_path)

# -----------------------------------------------------------------------------
# If run as a script
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    INPUT_FOLDER = 'single_word_videos'
    TEMP_JSON    = 'single_word_videos/jsons'
    MODEL_FILE   = '../models/local_models/3d_gcn_rnn_on_6_vpw.keras'
    LABEL_FILE   = '../models/local_models/label_encoder_3d_gcn_rnn_6_vpw.pkl'

    os.makedirs(TEMP_JSON, exist_ok=True)
    classify(INPUT_FOLDER, TEMP_JSON, MODEL_FILE, LABEL_FILE)