import os
import json
import random
import cv2
import numpy
import copy
import math

# Create directories if they don't exist
# os.makedirs("generated_motion_data", exist_ok=True)

# folder_with_new_jsons = "generated_motion_data"
# folder_with_original_jsons = "motion_data_old"


def load_json(file_name, folder_path):
    """
    Load a JSON file from the motion_data_old folder.

    Args:
        file_name (str): The name of the JSON file to load.

    Returns:
        dict: The loaded JSON data.
    """
    with open(os.path.join(folder_path, file_name), "r") as file:
        return json.load(file)


def save_json(data, file_name, output_folder):
    """
    Save a JSON file to the generated_motion_data folder.

    Args:
        data (dict): The JSON data to save.
        file_name (str): The name of the output JSON file.
    """
    with open(os.path.join(output_folder, file_name), "w") as file:
        json.dump(data, file, indent=4)


def shift_position(data, shift_x=0, shift_y=0):
    """
    Shift all landmarks in the JSON data by a given x and y offset.

    Args:
        data (list): The JSON data representing motion frames.
        shift_x (float): The amount to shift landmarks along the x-axis.
        shift_y (float): The amount to shift landmarks along the y-axis.

    Returns:
        list: The modified JSON data with shifted positions.
    """
    for frame in data:
        for landmark in frame['pose']:
            landmark['x'] += shift_x
            landmark['y'] += shift_y
        for hand_landmarks in frame.get('hands', []):
            for landmark in hand_landmarks:
                landmark['x'] += shift_x
                landmark['y'] += shift_y
    return data


def scale_motion(data, scale_factor):
    """
    Scale all landmarks in the JSON data by a given factor.

    Args:
        data (list): The JSON data representing motion frames.
        scale_factor (float): The factor by which to scale the landmarks.

    Returns:
        list: The modified JSON data with scaled positions.
    """
    for frame in data:
        for landmark in frame['pose']:
            landmark['x'] *= scale_factor
            landmark['y'] *= scale_factor
            landmark['z'] *= scale_factor
        for hand_landmarks in frame.get('hands', []):
            for landmark in hand_landmarks:
                landmark['x'] *= scale_factor
                landmark['y'] *= scale_factor
                landmark['z'] *= scale_factor
    return data


def add_noise(data, noise_level):
    """
    Add random noise to all landmarks in the JSON data.

    Args:
        data (list): The JSON data representing motion frames.
        noise_level (float): The maximum amount of random noise to add to each coordinate.

    Returns:
        list: The modified JSON data with added noise.
    """
    const_make_the_noise_smaller = 100
    for frame in data:
        for landmark in frame['pose']:
            landmark['x'] += random.uniform(-noise_level, noise_level / const_make_the_noise_smaller)
            landmark['y'] += random.uniform(-noise_level, noise_level / const_make_the_noise_smaller)
            landmark['z'] += random.uniform(-noise_level, noise_level / const_make_the_noise_smaller)
        for hand_landmarks in frame.get('hands', []):
            for landmark in hand_landmarks:
                landmark['x'] += random.uniform(-noise_level, noise_level / const_make_the_noise_smaller)
                landmark['y'] += random.uniform(-noise_level, noise_level / const_make_the_noise_smaller)
                landmark['z'] += random.uniform(-noise_level, noise_level / const_make_the_noise_smaller)
    return data


def add_up_down_movement(data, shift_y):
    """
    Add vertical movement (up or down) to all landmarks.

    Args:
        data (list): The JSON data representing motion frames.
        shift_y (float): The amount to shift landmarks along the y-axis.

    Returns:
        list: The modified JSON data with vertical movement.
    """
    return shift_position(data, shift_x=0, shift_y=shift_y)


def generate_variations(file_name):
    """
    Generate new variations of the motion JSON data with multiple changes.

    Args:
        file_name (str): The base name of the input JSON file (without .json).
    """
    data = load_json(f"{file_name}.json")
    # Single transformations
    shifted_right = shift_position(copy.deepcopy(data), shift_x=0.1,
                                   shift_y=0.0)  # Shift landmarks slightly to the right
    save_json(shifted_right, f"{file_name}_shifted_right.json")

    shifted_far_right = shift_position(copy.deepcopy(data), shift_x=0.3,
                                       shift_y=0.0)  # Shift landmarks farther to the right
    save_json(shifted_far_right, f"{file_name}_shifted_far_right.json")

    shifted_left = shift_position(copy.deepcopy(data), shift_x=-0.1,
                                  shift_y=0.0)  # Shift landmarks slightly to the left
    save_json(shifted_left, f"{file_name}_shifted_left.json")

    scaled_up = scale_motion(copy.deepcopy(data), scale_factor=1.2)  # Scale up (zoom in)
    save_json(scaled_up, f"{file_name}_scaled_up.json")

    scaled_down = scale_motion(copy.deepcopy(data), scale_factor=0.8)  # Scale down (zoom out)
    save_json(scaled_down, f"{file_name}_scaled_down.json")

    noisy_data = add_noise(copy.deepcopy(data), noise_level=0.01)  # Add very small random noise
    save_json(noisy_data, f"{file_name}_noisy.json")

    moved_up = add_up_down_movement(copy.deepcopy(data), shift_y=0.1)  # Shift landmarks slightly upward
    save_json(moved_up, f"{file_name}_moved_up.json")

    moved_down = add_up_down_movement(copy.deepcopy(data), shift_y=-0.1)  # Shift landmarks slightly downward
    save_json(moved_down, f"{file_name}_moved_down.json")

    # Combined transformations
    combined_1 = add_noise(scale_motion(shift_position(copy.deepcopy(data), shift_x=0.05, shift_y=0.05), 1.1), 0.005)
    save_json(combined_1, f"{file_name}_combined_1.json")  # Slightly shifted, scaled up, and very small noise

    combined_2 = add_noise(scale_motion(shift_position(copy.deepcopy(data), shift_x=-0.05, shift_y=-0.05), 0.9), 0.005)
    save_json(combined_2, f"{file_name}_combined_2.json")  # Slightly shifted, scaled down, and very small noise


def visualize_motion_data(file_name, output_folder):
    """
    Visualize motion data from a JSON file.

    Args:
        file_name (str): The name of the JSON file to visualize.
    """
    json_path = os.path.join(output_folder, file_name)
    with open(json_path, "r") as f:
        motion_data = json.load(f)

    canvas_size = (720, 1280, 3)  # Canvas dimensions (Height, Width, Channels)

    for frame_data in motion_data:
        canvas = numpy.ones(canvas_size, dtype=numpy.uint8) * 255  # White background

        # Draw pose landmarks
        for lm in frame_data.get("pose", []):
            x, y = int(lm["x"] * canvas_size[1]), int(lm["y"] * canvas_size[0])
            cv2.circle(canvas, (x, y), 5, (0, 0, 255), -1)

        # Draw hand landmarks
        for hand_landmarks in frame_data.get("hands", []):
            for lm in hand_landmarks:
                x, y = int(lm["x"] * canvas_size[1]), int(lm["y"] * canvas_size[0])
                cv2.circle(canvas, (x, y), 5, (255, 0, 0), -1)

        # Add title with file name
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(canvas, file_name, (50, 50), font, 1, (0, 0, 0), 2, cv2.LINE_AA)

        # Show frame
        cv2.imshow('Visualizing Motion Data', canvas)
        if cv2.waitKey(100) & 0xFF == ord('q'):  # Adjust delay as needed
            break

    cv2.destroyAllWindows()


def visualize_all_files(input_file_name, output_folder):
    """
    Visualize all generated motion JSON files starting with the input file name.

    Args:
        input_file_name (str): The base name of the input file.
    """
    for file_name in os.listdir(output_folder):
        if file_name.startswith(input_file_name) and file_name.endswith(".json"):
            visualize_motion_data(file_name,output_folder)


# THAT FRESH
def modify_finger_positions(data, max_shift=0.0025):
    """
    Modify finger positions in hand landmarks to simulate natural variations in ISL.

    Args:
        data (list): The JSON data representing motion frames.
        max_shift (float): The maximum amount to shift finger landmarks along x, y, and z axes.

    Returns:
        list: The modified JSON data with adjusted finger positions.
    """
    for frame in data:
        for hand_landmarks in frame.get('hands', []):
            # Apply random shifts to each finger
            for i, landmark in enumerate(hand_landmarks):
                # Slightly shift each landmark's x, y, z within a small range
                landmark['x'] += random.uniform(-max_shift, max_shift)
                landmark['y'] += random.uniform(-max_shift, max_shift)
                landmark['z'] += random.uniform(-max_shift, max_shift)

                # Optional: Apply specific adjustments per finger
                if 4 <= i <= 7:  # Thumb
                    landmark['x'] += random.uniform(-max_shift * 0.5, max_shift * 0.5)
                elif 8 <= i <= 11:  # Index finger
                    landmark['y'] += random.uniform(-max_shift * 0.5, max_shift * 0.5)
                elif 12 <= i <= 15:  # Middle finger
                    landmark['z'] += random.uniform(-max_shift * 0.5, max_shift * 0.5)
                elif 16 <= i <= 19:  # Ring finger
                    landmark['x'] -= random.uniform(-max_shift * 0.5, max_shift * 0.5)
                elif 20 <= i <= 23:  # Pinky
                    landmark['y'] -= random.uniform(-max_shift * 0.5, max_shift * 0.5)
    return data


def adjust_hand_speed(data, speed_factor=2.0):
    """
    Adjust the speed of hand movements in the motion data.

    Args:
        data (list): The JSON data representing motion frames.
        speed_factor (float): Factor to adjust speed (e.g., 0.5 = slower, 2.0 = faster).

    Returns:
        list: Modified JSON data with adjusted hand movement speed.
    """
    if speed_factor < 1.0:
        # Slower movement: interpolate additional frames
        new_data = []
        for i in range(len(data) - 1):
            frame1 = data[i]
            frame2 = data[i + 1]
            new_data.append(frame1)

            # Interpolate frames
            interpolated_frame = interpolate_frames(frame1, frame2, alpha=0.5)
            new_data.append(interpolated_frame)

        new_data.append(data[-1])
        return new_data

    elif speed_factor > 1.0:
        # Faster movement: skip frames
        skip = int(speed_factor)
        return data[::skip]

    return data  # No change if speed_factor == 1.0


def trim_start(data, trim_time=0.3, frame_rate=30):
    """
    Trim the first part of the motion data to start the video after a certain time.

    Args:
        data (list): The JSON data representing motion frames.
        trim_time (float): The amount of time (in seconds) to trim from the start.
        frame_rate (int): The number of frames per second in the video.

    Returns:
        list: Trimmed JSON data.
    """
    # Calculate the number of frames to trim based on trim_time and frame_rate
    frames_to_trim = int(trim_time * frame_rate)

    # Return the trimmed data
    return data[frames_to_trim:]


def interpolate_frames(frame1, frame2, alpha=0.5):
    """
    Interpolate between two frames.

    Args:
        frame1 (dict): First frame data.
        frame2 (dict): Second frame data.
        alpha (float): Interpolation factor (0.0 = frame1, 1.0 = frame2).

    Returns:
        dict: Interpolated frame data.
    """
    interpolated_frame = copy.deepcopy(frame1)
    for key in ['pose', 'hands']:
        if key in frame1 and key in frame2:
            for i in range(len(frame1[key])):
                interpolated_frame[key][i]['x'] = (1 - alpha) * frame1[key][i]['x'] + alpha * frame2[key][i]['x']
                interpolated_frame[key][i]['y'] = (1 - alpha) * frame1[key][i]['y'] + alpha * frame2[key][i]['y']
                interpolated_frame[key][i]['z'] = (1 - alpha) * frame1[key][i]['z'] + alpha * frame2[key][i]['z']
    return interpolated_frame


def nonlinear_speed_adjustment(data, max_speed_factor=2.0, min_speed_factor=0.5):
    """
    Apply non-linear speed adjustment to the motion data.
    Starts slow and gradually speeds up.

    Args:
        data (list): The JSON data representing motion frames.
        max_speed_factor (float): Maximum speed factor (fastest speed at the end).
        min_speed_factor (float): Minimum speed factor (slowest speed at the start).

    Returns:
        list: Modified JSON data with non-linear speed adjustment.
    """
    new_data = []
    total_frames = len(data)

    for i in range(total_frames):
        # Calculate speed factor based on frame position
        alpha = i / total_frames
        speed_factor = min_speed_factor + alpha * (max_speed_factor - min_speed_factor)

        # Decide whether to include this frame
        if random.random() < 1 / speed_factor:
            new_data.append(data[i])

    return new_data


def random_frame_drops(data, drop_percentage=10):
    """
    Randomly drop a percentage of frames from the motion data.

    Args:
        data (list): The JSON data representing motion frames.
        drop_percentage (int): Percentage of frames to drop.

    Returns:
        list: Modified JSON data with random frame drops.
    """
    total_frames = len(data)
    frames_to_drop = int(total_frames * drop_percentage / 100)

    drop_indices = set(random.sample(range(total_frames), frames_to_drop))
    new_data = [frame for i, frame in enumerate(data) if i not in drop_indices]

    return new_data


def rotate_landmarks(data, angle_degrees=5):  # TODO: not sure if working properly
    """
    Rotate landmarks slightly to simulate perspective changes, maintaining the center.

    Args:
        data (list): The JSON data representing motion frames.
        angle_degrees (float): Rotation angle in degrees.

    Returns:
        list: Modified JSON data with rotated landmarks.
    """

    angle_radians = math.radians(angle_degrees)
    cos_theta = math.cos(angle_radians)
    sin_theta = math.sin(angle_radians)

    for frame in data:
        for key in ['pose', 'hands']:
            if key in frame and frame[key]:
                x_coords = []
                y_coords = []

                # Collect x and y coordinates for all landmarks
                for landmark in frame[key]:
                    # Handle nested structures
                    if isinstance(landmark, dict) and 'x' in landmark and 'y' in landmark:
                        x_coords.append(landmark['x'])
                        y_coords.append(landmark['y'])
                    elif isinstance(landmark, dict):
                        # Check for nested 'x' and 'y' within another dictionary
                        nested_x = landmark.get('x', {}).get('value') if isinstance(landmark.get('x'), dict) else None
                        nested_y = landmark.get('y', {}).get('value') if isinstance(landmark.get('y'), dict) else None
                        if nested_x is not None and nested_y is not None:
                            x_coords.append(nested_x)
                            y_coords.append(nested_y)

                # Ensure there are coordinates to calculate the center
                if not x_coords or not y_coords:
                    continue

                # Calculate the center of the landmarks
                center_x = sum(x_coords) / len(x_coords)
                center_y = sum(y_coords) / len(y_coords)

                # Rotate each landmark around the center
                for i, landmark in enumerate(frame[key]):
                    if isinstance(landmark, dict) and 'x' in landmark and 'y' in landmark:
                        x, y = landmark['x'], landmark['y']
                        # Translate to origin
                        x -= center_x
                        y -= center_y
                        # Rotate
                        rotated_x = cos_theta * x - sin_theta * y
                        rotated_y = sin_theta * x + cos_theta * y
                        # Translate back
                        landmark['x'] = rotated_x + center_x
                        landmark['y'] = rotated_y + center_y

    return data

def visualize_folder(folder_path):
    """
    Visualize all motion data files in a folder.

    Args:
        folder_path (str): The path to the folder containing JSON files to visualize.
    """
    # List all JSON files in the folder
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]

    # Visualize each file
    for file_name in json_files:
        print(f"Visualizing {file_name}...")
        visualize_motion_data(file_name)

    print("All files have been visualized.")


def fresh_generate_variations(file_name):
    """
    Generate new variations of the motion JSON data with multiple changes.

    Args:
        file_name (str): The base name of the input JSON file (without .json).
    """
    data = load_json(f"{file_name}.json")
    # Single transformations
    rotated_data10 = rotate_landmarks(data, -5)
    save_json(rotated_data10, f"{file_name}_rotated-10.json")
    rotated_data5 = rotate_landmarks(data)
    save_json(rotated_data5, f"{file_name}_rotated5.json")
    # random_drops = random_frame_drops(data)
    # save_json(random_drops, f"{file_name}_random_drops.json")
    # nonlinear_speed = nonlinear_speed_adjustment(data)
    # save_json(nonlinear_speed, f"{file_name}_nonlinear_speed.json")
    # trim_start_modify = trim_start(data)
    # save_json(trim_start_modify, f"{file_name}_trim_start.json")
    # fingers_modify = modify_finger_positions(data)# Shift landmarks slightly to the right
    # save_json(fingers_modify, f"{file_name}_fingers_modify.json")
    # speed_modify = adjust_hand_speed(data, 2)
    # save_json(speed_modify, f"{file_name}_speed_modify.json")


if __name__ == "__main__":
#     input_file_name = "cell_phone"  # Replace with the desired file name (without .json extension)
#     fresh_generate_variations(input_file_name)
    visualize_all_files("ambu","/Users/raananpevzner/try/sign_language_translation/resources/motion_data_old")
    # visualize_motion_data('/Users/raananpevzner/try/sign_language_translation/resources/motion_data_old/ambulance_14.json')
