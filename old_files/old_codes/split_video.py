from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def split_video(input_path, output_dir, segment_length, overlap):
    """
    Splits a video into smaller segments with specified length and overlap.

    Parameters:
        input_path (str): Path to the input video.
        output_dir (str): Directory to save the output video segments.
        segment_length (float): Length of each video segment in seconds.
        overlap (float): Overlap duration between consecutive segments in seconds.

    Returns:
        None
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video = VideoFileClip(input_path)
    video_duration = video.duration

    start_time = 0
    segment_number = 1

    while start_time < video_duration:
        end_time = min(start_time + segment_length, video_duration)

        segment = video.subclip(start_time, end_time)
        output_path = os.path.join(output_dir, f"segment_{segment_number}.mp4")
        segment.write_videofile(output_path, codec="libx264", audio_codec="aac")

        start_time += segment_length - overlap
        segment_number += 1

    video.close()

# Example usage
input_video_path = r"C:\Users\lenan\Videos\video_clip.mp4"
output_directory = "output_segments"
segment_duration = 10  # seconds
overlap_duration = 2  # seconds

split_video(input_video_path, output_directory, segment_duration, overlap_duration)
