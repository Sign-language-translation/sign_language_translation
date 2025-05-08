from utils.video_augmentation import augment_all_files
import shutil
import os
from utils.test_mediapipe import create_original_motion_data
from create_database import create_db, drop_video_data_table
from models.model_3d_cnn_rnn import create_model

# Path settings
MOTION_DATA_FOLDER_PATH = "resources/motion_data"
GENERATED_MOTION_DATA_FOLDER_PATH = "resources/generated_motion_data"
ORIGINAL_VIDEOS_DATA_FOLDER_PATH = "resources/sign_language_videos"
MODELS_FOLDER = 'models'

AMOUNT_OF_VARIATIONS = 15

def create_original_jsons(input_folder_path_original_videos, output_folder_path_motion_data):
    # Ensure the folder exists
    os.makedirs(output_folder_path_motion_data, exist_ok=True)
    os.makedirs(input_folder_path_original_videos, exist_ok=True)
    create_original_motion_data(input_folder_path_original_videos, output_folder_path_motion_data)

def create_augmentations(input_folder_path_motion_data, data_output_folder_path_generated_motion):
    # Ensure the folder exists
    os.makedirs(data_output_folder_path_generated_motion, exist_ok=True)
    print(f"Start creating augmented data at {input_folder_path_motion_data}")
    # Ensure the folder exists
    augment_all_files(AMOUNT_OF_VARIATIONS, input_folder=input_folder_path_motion_data, output_folder=data_output_folder_path_generated_motion)

def delete_folder_content(folder_path):
    # Delete the folder
    try:
        shutil.rmtree(folder_path)
        print(f"Old files were deleted at {folder_path}")
    except OSError as e:
        print(f"Error: {e.strerror}")

def add_data_to_db(folder_path):
    create_db(folder_path)

def drop_db_table():
    drop_video_data_table()

def main():
    pkl_file_name = f"label_encoder_3d_rnn_cnn_{AMOUNT_OF_VARIATIONS}_vpw"
    model_filename = f"3d_rnn_cnn_on_{AMOUNT_OF_VARIATIONS}_vpw"

    # Clear the old data
    delete_folder_content(MOTION_DATA_FOLDER_PATH)
    delete_folder_content(GENERATED_MOTION_DATA_FOLDER_PATH)
    drop_db_table()

    create_original_jsons(ORIGINAL_VIDEOS_DATA_FOLDER_PATH, MOTION_DATA_FOLDER_PATH)
    create_augmentations(MOTION_DATA_FOLDER_PATH, GENERATED_MOTION_DATA_FOLDER_PATH)
    add_data_to_db(GENERATED_MOTION_DATA_FOLDER_PATH)
    create_model(pkl_file_name=pkl_file_name, model_filename=model_filename, models_folder_path=MODELS_FOLDER)
    print("Finished")
    print(pkl_file_name)
    print(model_filename)

    # results_list = classify(pkl_file_name, model_filename, test_original = True)
    # for result in results_list:
    #     print(result)
    # Calculate the maximum width for the "Real label" column
    # max_real_label_length = max(len(real_label) for real_label, _ in results_list)
    #
    # # Print the aligned results
    # for real_label, predicted_label in results_list:
    #     print(f"Real label: {real_label.ljust(max_real_label_length)} | Predicted Label: {predicted_label}")

main()