import os
from moviepy import *
from moviepy.editor import *
from PIL import Image
import numpy as np

def crop_video(video_name, x, y, width, height):
    try:
        # Define folder paths
        base_folder = os.path.dirname(__file__)  # Get the current script's directory
        input_folder = os.path.join(base_folder, "original_videos")
        output_folder = os.path.join(base_folder, "cropped_videos")

        # Build input and output file paths
        input_path = os.path.join(input_folder, video_name)
        output_path = os.path.join(output_folder, f"cropped_{video_name}")

        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Load video
        video_clip = VideoFileClip(input_path)

        # Crop the video
        # cropped_clip = video_clip.crop(x1=x, y1=y, width=width, height=height)
        cropped_clip = video_clip.crop(x1=x, y1=y, x2=x + width, y2=y + height)

        # Write the cropped video to the output path
        cropped_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        print(f"Video successfully cropped and saved at: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def corp_simulation(video_path, x, y, width, height, output_image_path):
    try:
        # Load the video
        video = VideoFileClip(video_path)

        # Calculate 1/3 of the video duration
        third_duration = video.duration / 3

        # Extract a frame at 1/3 of the duration
        frame = video.get_frame(third_duration)

        # Create a mask: blacken everything except the specified rectangle
        masked_frame = np.zeros_like(frame)  # Blacken entire frame
        masked_frame[y:y + height, x:x + width, :] = frame[y:y + height, x:x + width, :]  # Add the visible rectangle

        # Save the masked frame as an image
        image = Image.fromarray(masked_frame)
        image.save(output_image_path)

        print(f"Masked image saved to {output_image_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def extract_frames(input_directory):
    try:
        # Create output directory if it doesn't exist
        base_directory = os.path.dirname(input_directory)
        output_directory = os.path.join(base_directory, "sim_frames")
        os.makedirs(output_directory, exist_ok=True)

        # Loop through all files in the directory
        for filename in os.listdir(input_directory):
            if filename.endswith(".mp4"):  # Check if it's an MP4 file
                video_path = os.path.join(input_directory, filename)
                output_image_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0]}_frame.png")

                print(f"Processing: {filename}")

                # Load the video
                video = VideoFileClip(video_path)

                # Calculate 1/3 of the video duration
                third_duration = video.duration / 3

                # Extract a frame at 1/3 of the duration
                frame = video.get_frame(third_duration)

                # Save the frame as an image
                image = Image.fromarray(frame)
                image.save(output_image_path)

                print(f"Saved frame to: {output_image_path}")

        print(f"All videos processed. Frames saved in {output_directory}")

    except Exception as e:
        print(f"An error occurred: {e}")

#
# input_directory = "/Users/raananpevzner/PycharmProjects/sign_language_translation/original_videos"  # Replace with your directory path
# extract_frames(input_directory)


if __name__ == "__main__":
    # Define folder paths
    base_folder = os.path.dirname(__file__)
    input_folder = os.path.join(base_folder, "original_videos")

    # Get video name from user
    video_name = "video1.mp4"
    input_path = os.path.join(input_folder, video_name)

    # print(input_path)
    try:
        # Load the video to get its size
        video_clip = VideoFileClip(input_path)
        width = video_clip.size[0]
        height = video_clip.size[1]
        print(f"Video duration: {video_clip.duration} seconds")
        print(f"Original video size: {width}x{height} pixels")
    except Exception as e:
        print(f"Could not load video: {e}")
        exit()

    # Get cropping parameters from user (or set default values)
    x = 10
    y = 30
    width_crop = 200
    height_crop = 300

    # Crop the video
    crop_video('video1.mp4',308,200,755,605)
    # corp_simulation(input_path, 308,200,755,605,"sim.png")