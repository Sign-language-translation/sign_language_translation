import cv2
import os


def get_video_length(file_path):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    if fps > 0:
        return frame_count / fps
    return None


def analyze_video_lengths(folder_path):
    video_lengths = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            full_path = os.path.join(folder_path, filename)
            length = get_video_length(full_path)
            if length is not None:
                video_lengths.append((filename, length))

    if video_lengths:
        # Find min and max
        shortest_video = min(video_lengths, key=lambda x: x[1])
        longest_video = max(video_lengths, key=lambda x: x[1])
        avg_length = sum(length for _, length in video_lengths) / len(video_lengths)

        print(f"Shortest video: {shortest_video[0]} ({shortest_video[1]:.2f} seconds)")
        print(f"Longest video: {longest_video[0]} ({longest_video[1]:.2f} seconds)")
        print(f"Average length: {avg_length:.2f} seconds")
    else:
        print("No valid videos found.")


# Example usage
analyze_video_lengths("../resources/sign_language_videos")
