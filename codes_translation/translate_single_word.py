import numpy as np
import os
from tensorflow.keras.models import load_model
import pickle
from utils.conver_json_to_vector import create_feature_vector
import json
from utils.test_mediapipe import extract_motion_data, motion_data_to_json

def read_json_file(file_path):
    """
    Reads a JSON file and returns its content.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The parsed JSON content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_content = json.load(file)
        return json_content
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON. {e}")
    return None


def load_label_mapping(file_path):
    """Load the label encoder from a file."""
    with open(file_path, 'rb') as f:
        label_encoder = pickle.load(f)
    print(f"Label encoder loaded from {file_path}")
    return list(label_encoder.classes_)

def classify_json_file(model_filename ,json_content, label_mapping):
    """
    Classifies a dummy matrix using a pre-trained model.

    Args:
        model_filename (str): Path to the saved model.
        input_shape (tuple): Shape of the input data (e.g., (50, 75, 3)).
        label_mapping (dict): Mapping of class indices to labels.

    Returns:
        str: Predicted class label.
    """
    # Load the saved model
    model = load_model(model_filename)

    input_matrix = create_feature_vector(json_content)
    # Assuming `input_data` is your input of shape (32, 75, 3)
    reshaped_data = input_matrix.reshape((1, 50, 75, 3))  # Add batch and time steps dimensions

    # Pass reshaped_data to the model
    predictions = model.predict(reshaped_data)
    predicted_class = np.argmax(predictions, axis=-1)[0]  # Get the predicted class index

    # Map the predicted index to the corresponding label
    predicted_label = label_mapping[predicted_class]

    return predicted_label

# def classify(input_folder_path_of_videos, temp_folder_path_of_jsons, model_file_path, label_encoder_file_path):
#
#     for file_name in os.listdir(input_folder_path_of_videos):
#         if file_name.split('.')[1] == "mp4":
#             classify_single_word(input_folder_path_of_videos + "/" + file_name, input_folder_path_of_videos, model_file_path, label_encoder_file_path)

def classify_single_word(input_video_folder_name, video_file_name, temp_folder_path_of_jsons, model_file_path, label_encoder_file_path, log_folder_path=None):
    file_path = os.path.join(input_video_folder_name, video_file_name)
    if not os.path.exists(file_path):
        print(f"❌ File does not exist: {file_path}")
        return None

    if video_file_name.split('.')[-1] == "mp4":
        file_name = video_file_name.split('.')[0]

        trim_data = extract_motion_data(file_name, folder_name=input_video_folder_name)
        motion_data_to_json(trim_data, file_name, folder_name=temp_folder_path_of_jsons, log_folder_path=log_folder_path)

        json_content = read_json_file(f"{temp_folder_path_of_jsons}/{file_name}.json")

        # Check if JSON content is empty
        if not json_content:
            print(f"Skipped {file_name}: JSON content is empty.")
            return None

        # Define a label mapping
        label_encoder = load_label_mapping(label_encoder_file_path)

        # Get the classification result
        predicted_label = classify_json_file(model_file_path, json_content, label_encoder)
        print(f"Real label: {file_name}, Predicted Label: {predicted_label}")

        return predicted_label

    return None

# Example usage
if __name__ == "__main__":
    input_folder_path_of_videos = 'single_word_videos/videos'
    temp_folder_path_of_jsons = 'single_word_videos/jsons'
    model_file_name = 'models/3d_rnn_cnn_on_30_vpw.keras'
    label_encoder_file_name = 'models/label_encoder_3d_rnn_cnn_30_vpw.pkl'
    # classify(input_folder_path_of_videos, temp_folder_path_of_jsons, model_file_name, label_encoder_file_name)