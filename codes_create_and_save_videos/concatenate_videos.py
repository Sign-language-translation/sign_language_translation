import cv2
import os


def concatenate_videos(video_names, output_name):
    input_folder = r"C:\Users\yaelm\Documents\4th_year_project\sign_language_translation\resources\sign_language_videos"
    output_folder = r"C:\Users\yaelm\Documents\4th_year_project\sign_language_translation\test_codes_and_files\sentence_videos"

    output_path = os.path.join(output_folder, f"{output_name}.mp4")
    slow_output_path = os.path.join(output_folder, f"{output_name}_0_75_speed.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    all_frames = []
    first_frame_size = None
    fps = 30  # Default FPS

    # Collect all frames from all videos
    for name in video_names:
        video_path = os.path.join(input_folder, f"{name}.mp4")
        if not os.path.exists(video_path):
            print(f"Warning: {video_path} not found. Skipping.")
            continue

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"Error opening video file: {video_path}")
            continue

        if first_frame_size is None:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or fps
            first_frame_size = (width, height)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame.shape[1::-1] != first_frame_size:
                frame = cv2.resize(frame, first_frame_size)
            all_frames.append(frame)

        cap.release()

    if not all_frames:
        print("No valid videos were processed.")
        return

    # Save normal speed video
    # out_normal = cv2.VideoWriter(output_path, fourcc, fps, first_frame_size)
    # for frame in all_frames:
    #     out_normal.write(frame)
    # out_normal.release()
    # print(f"Regular speed video saved to: {output_path}")

    # Save 0.75x speed video (lower FPS)
    slow_fps = fps * 0.75
    out_slow = cv2.VideoWriter(slow_output_path, fourcc, slow_fps, first_frame_size)
    for frame in all_frames:
        out_slow.write(frame)
    out_slow.release()
    print(f"0.75x speed video saved to: {slow_output_path}")


def main():
    # video_list = ["I_1", "hungry_1", "saturday_1"]
    # output_video_name = "I_hungry_saturday_yanoos"
    # concatenate_videos(video_list, output_video_name)

    video_sets = [
        (["I_6", "walk_7", "far_6"], "I_walk_far_test"),
        (["when_3", "you_3", "come_7"], "when_you_come_test"),
        (["you_3", "welcome_6"], "you_welcome_test"),
        (["when_6", "you_3", "hungry_5"], "when_you_hungry_test"),
        (["I_5", "no_7", "walk_8"], "I_no_walk_test"),
        (["you_2", "walk_7", "far_6", "saturday_8"], "you_walk_far_saturday_test"),
        (["I_6", "no_7", "angry_4"], "I_no_angry_test"),
        (["I_5", "no_7", "far_6"], "I_no_far_test"),
    ]

    for video_list, output_video_name in video_sets:
        concatenate_videos(video_list, output_video_name)


main()
