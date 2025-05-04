import os
import random
import copy
import csv
import json
from utils.generate_motion_data import (
    load_json,
    save_json,
    shift_position,
    scale_motion,
    add_noise,
    add_up_down_movement,
    modify_finger_positions,
    adjust_hand_speed,
    trim_start,
    nonlinear_speed_adjustment,
    random_frame_drops,
    rotate_landmarks
)

# AMOUNT_OF_VARIATIONS = 23

# Path settings
# original_folder = "motion_data"
augmented_folder = "generated_motion_data"
csv_file_path = "augmented_data_summary.csv"  # Output CSV file



def apply_random_augmentations(data):
    """
    Apply a random combination of augmentations to the given data.

    Args:
        data (list): The original motion data.

    Returns:
        tuple: (augmented_data, applied_augmentations), where
               augmented_data is the modified motion data,
               and applied_augmentations is a list of augmentation names.
    """
    augmentations = {
        "shift": lambda d: shift_position(d, shift_x=random.uniform(-0.1, 0.1), shift_y=random.uniform(-0.1, 0.1)),
        "scale": lambda d: scale_motion(d, scale_factor=random.uniform(0.8, 1.2)),
        "noise": lambda d: add_noise(d, noise_level=random.uniform(0.001, 0.005)),
        "up_down": lambda d: add_up_down_movement(d, shift_y=random.uniform(-0.05, 0.05)),
        "finger_mod": lambda d: modify_finger_positions(d, max_shift=random.uniform(0.001, 0.003)),
        "speed": lambda d: adjust_hand_speed(d, speed_factor=random.uniform(1.0, 2.0)),
        "trim": lambda d: trim_start(d, trim_time=random.uniform(0.2, 0.8), frame_rate=30),
        "nonlinear_speed": lambda d: nonlinear_speed_adjustment(d, max_speed_factor=random.uniform(1.5, 2.5), min_speed_factor=random.uniform(0.5, 1.0)),
        "frame_drops": lambda d: random_frame_drops(d, drop_percentage=random.randint(5, 15)),
        "rotate": lambda d: rotate_landmarks(d, angle_degrees=random.uniform(-6, 6))
    }

    # Randomly select and apply 3-6 augmentations
    selected_augmentations = random.sample(list(augmentations.items()), random.randint(6, 9))
    applied_augmentations = []
    for name, augment in selected_augmentations:
        data = augment(data)
        applied_augmentations.append(name)

    return data, applied_augmentations

def augment_all_files(amount_of_variations, input_folder, output_folder):
    """
    Augment all JSON files in the motion_data folder with random combinations of augmentations.
    """
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".json"):
            file_base_name = os.path.splitext(file_name)[0]
            data = load_json(file_name, folder_path=input_folder)

            # Generate multiple augmented versions
            for i in range(amount_of_variations):  # Generate 10 variations per file
                augmented_data, applied_augmentations = apply_random_augmentations(copy.deepcopy(data))
                # Create a descriptive file name
                augmentations_str = "_".join(applied_augmentations)
                # output_file_name = f"{file_base_name}_augmented_{i}_{augmentations_str}.json"
                output_file_name = f"{file_base_name}_{i}.json"

                save_json(augmented_data, output_file_name, output_folder)

    print("All files have been augmented!")



def write_to_csv(folder, csv_file):
    """
   Write the file names and Mediapipe JSON data to a CSV file with separate features.

   Args:
       folder (str): The folder containing the augmented JSON files.
       csv_file (str): The path to the output CSV file.
   """
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Header definition
        headers = ["File Name"]
        for i in range(33):  # Assuming 33 pose landmarks
            headers.extend([f"pose_{i}x", f"pose{i}y", f"pose{i}z", f"pose{i}_visibility"])
        for i in range(21):  # Assuming 21 hand landmarks per hand
            headers.extend([f"left_hand_{i}x", f"left_hand{i}y", f"left_hand{i}_z"])
            headers.extend([f"right_hand_{i}x", f"right_hand{i}y", f"right_hand{i}_z"])

        writer.writerow(headers)

        for file_name in os.listdir(folder):
            if file_name.endswith(".json"):
                file_base_name = file_name.split("_")[0]
                file_path = os.path.join(folder, file_name)

                with open(file_path, "r") as json_file:
                    try:
                        json_data = json.load(json_file)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file_name}: {e}")
                        continue

                for frame in json_data:
                    row = [file_base_name]

                    # Pose landmarks
                    for landmark in frame.get("pose", []):
                        row.extend([landmark.get("x", 0), landmark.get("y", 0), landmark.get("z", 0),
                                    landmark.get("visibility", 0)])

                    # Fill in zeros if less than 33 pose landmarks
                    row.extend([0] * (33 * 4 - len(frame.get("pose", [])) * 4))

                    # Initialize empty hand data
                    left_hand = [0] * (21 * 3)
                    right_hand = [0] * (21 * 3)

                    hands_data = frame['hands']

                    if len(hands_data) > 0:
                        if len(hands_data) == 1:
                            # Only one hand present, assume it's the right hand
                            landmarks = hands_data[0]  # Assuming hands_data[0] is a dictionary with landmarks
                            right_hand = [coord for lm in landmarks for coord in
                                          (lm.get("x", 0), lm.get("y", 0), lm.get("z", 0))]
                        elif len(hands_data) == 2:
                            # Two hands present
                            # First hand is right hand, second hand is left hand
                            right_hand_landmarks = hands_data[
                                0]  # Assuming hands_data[0] is a dictionary with landmarks
                            left_hand_landmarks = hands_data[1]  # Assuming hands_data[1] is a dictionary with landmarks
                            right_hand = [coord for lm in right_hand_landmarks for coord in
                                          (lm.get("x", 0), lm.get("y", 0), lm.get("z", 0))]
                            left_hand = [coord for lm in left_hand_landmarks for coord in
                                         (lm.get("x", 0), lm.get("y", 0), lm.get("z", 0))]

                            # Ensure hand landmarks are padded to 21 landmarks
                    row.extend(left_hand + [0] * (21 * 3 - len(left_hand)))
                    row.extend(right_hand + [0] * (21 * 3 - len(right_hand)))

                    writer.writerow(row)

    print(f"Data successfully written to {csv_file}")


#
if __name__ == "__main__":
    # Perform augmentations on all files
    augment_all_files(input_folder="resources/motion_data", output_folder="resources/generated_motion_data")
    # visualize_folder(augmented_folder)
    # write_to_csv(augmented_folder, csv_file_path)
    print("Augmentations complete! Check the generated_motion_data folder.")