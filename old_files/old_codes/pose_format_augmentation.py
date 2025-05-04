import os
from pose_format import Pose
from pose_format.numpy import NumPyPoseBody
import numpy as np
import json
import cv2
import random

def mediapipe_json_to_pose_file(file_path):
    """
    Processes a single JSON file and returns a Pose object.

    Parameters:
    - file_path (str): Path to the input JSON file.

    Returns:
    - Pose: A Pose object representing the landmarks in the JSON file.
    """
    pose_data = []  # To store frames for the current video

    with open(file_path, 'r') as f:
        data = json.load(f)

    # Handle multiple frames (each frame has a "pose" key with landmarks)
    for frame in data:
        if "pose" in frame:
            landmarks = frame["pose"]
            # Normalize landmarks (assume image dimensions: width=1, height=1)
            normalized_landmarks = [
                [lm["x"], lm["y"], lm["z"]] for lm in landmarks
            ]
            pose_data.append(normalized_landmarks)

    # Convert to NumPy array (frames, landmarks, 3D)
    pose_data = np.array(pose_data)

    # Confidence scores (default to 1 for all landmarks)
    confidence = np.ones((pose_data.shape[0], pose_data.shape[1], 1))

    # Create and return Pose-Format body
    pose_body = NumPyPoseBody(data=pose_data, confidence=confidence, fps=30)
    return Pose(header=None, body=pose_body)

def mediapipe_json_to_pose_directory(directory):
    """Processes all JSON files in a directory and returns a list of Pose objects."""
    poses = []  # List to store Pose objects

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # Ensure we only process JSON files
        if file_path.endswith(".json"):
            pose_data = []  # To store frames for the current video
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Handle multiple frames (each frame has a "pose" key with landmarks)
            for frame in data:
                if "pose" in frame:
                    landmarks = frame["pose"]
                    # Normalize landmarks (assume image dimensions: width=1, height=1)
                    normalized_landmarks = [
                        [lm["x"], lm["y"], lm["z"]] for lm in landmarks
                    ]
                    pose_data.append(normalized_landmarks)

            # Convert to NumPy array (frames, landmarks, 3D)
            pose_data = np.array(pose_data)

            # Confidence scores (default to 1 for all landmarks)
            confidence = np.ones((pose_data.shape[0], pose_data.shape[1], 1))

            # Create Pose-Format body and append to the list
            pose_body = NumPyPoseBody(data=pose_data, confidence=confidence, fps=30)
            poses.append(Pose(header=None, body=pose_body))

    return poses

def draw_pose_on_frame(frame, pose, frame_idx):
    """Draws the pose landmarks on the given frame."""
    for landmark in pose.body.data[frame_idx]:
        x = int(landmark[0] * frame.shape[1])  # Scale x-coordinate to canvas width
        y = int(landmark[1] * frame.shape[0])  # Scale y-coordinate to canvas height

        # Ensure the points are within the canvas
        if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # Green circles for landmarks
    return frame

def visualize_pose(pose, canvas_size=(720, 1280), fps=30):
    """Visualizes the pose data as a video on a blank canvas."""
    frame_delay = int(1000 / fps)  # Delay between frames in milliseconds
    for i in range(len(pose.body.data)):
        frame = np.zeros((canvas_size[0], canvas_size[1], 3), dtype=np.uint8)  # Blank canvas
        frame = draw_pose_on_frame(frame, pose, i)
        cv2.imshow("Pose Visualization", frame)

        # Wait for the frame_delay and break if 'q' is pressed
        if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def random_augment_pose(pose, rotation_std=2, shear_std=2, scale_std=2, flip_prob=0.5):
    """Applies random augmentations to a Pose object."""
    # Apply 2D augmentations
    pose.augment2d(
        rotation_std=random.uniform(0, rotation_std),
        shear_std=random.uniform(0, shear_std),
        scale_std=random.uniform(1 - scale_std, 1 + scale_std)
    )

    # Random horizontal flip
    if random.random() < flip_prob:
        pose.body.data[:, :, 0] *= -1  # Flip x-coordinates

    # Clip the data to valid ranges
    pose.body.data[:, :, 0] = np.clip(pose.body.data[:, :, 0], 0, 1)  # x in [0, 1]
    pose.body.data[:, :, 1] = np.clip(pose.body.data[:, :, 1], 0, 1)  # y in [0, 1]

    return pose


def pose_to_mediapipe_json(pose, output_file):
    """Converts a Pose object to MediaPipe-style JSON output."""
    mediapipe_output = []
    for frame_idx in range(len(pose.body.data)):
        frame_data = {"pose": []}
        for landmark in pose.body.data[frame_idx]:
            frame_data["pose"].append({
                "x": float(landmark[0]),
                "y": float(landmark[1]),
                "z": float(landmark[2]),
                "visibility": 1.0
            })
        mediapipe_output.append(frame_data)
    with open(output_file, 'w') as f:
        json.dump(mediapipe_output, f, indent=4)

def generate_augmented_json_files(input_folder, number_of_versions):
    """Generates augmented JSON files for all poses in the input folder."""
    output_folder = "pose_format_augmentation"
    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(input_folder, file_name)
            pose = mediapipe_json_to_pose_file(file_path)

            base_name = os.path.splitext(file_name)[0]
            for index in range(number_of_versions):
                # Apply random augmentation
                augmented_pose = random_augment_pose(pose)

                # Save as MediaPipe JSON
                output_file = os.path.join(output_folder, f"{base_name}_{index}_pose-format.json")
                pose_to_mediapipe_json(augmented_pose, output_file)

                print(f"Saved: {output_file}")

# Example usage
if __name__ == "__main__":
    input_folder = "test_videos/yanoos_json"  # Replace with your input folder path
    number_of_versions = 10  # Number of augmented versions to generate per file
    generate_augmented_json_files(input_folder, number_of_versions)
    # p = mediapipe_json_to_pose_file("motion_data/sister.json")
    #
    # visualize_pose(p)