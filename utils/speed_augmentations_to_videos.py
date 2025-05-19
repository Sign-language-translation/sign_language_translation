import os
import cv2

def create_speed_augmentations_to_videos(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    # Read defective names from the log file
    # defective_log_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'defective_json_log.txt'))
    #
    # if not os.path.exists(defective_log_path):
    #     print(f"Defective log file not found: {defective_log_path}")
    #     return

    # with open(defective_log_path, 'r') as f:
    #     defective_names = set(line.strip().replace('.json', '') for line in f if line.strip())

    speed_factors = [0.85, 0.9, 1.0, 1.1, 1.15]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    for filename in os.listdir(input_folder):
        if not filename.endswith(".mp4"):
            continue

        video_name = os.path.splitext(filename)[0]

        # if video_name in defective_names:
        #     print(f"Skipped defective video: {video_name}")
        #     continue

        input_path = os.path.join(input_folder, filename)

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error opening video file: {input_path}")
            continue

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (width, height)

        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        cap.release()

        if not frames:
            print(f"No frames found in {filename}")
            continue

        for speed in speed_factors:
            new_fps = fps * speed
            speed_str = str(speed).replace('.', '_')
            out_filename = f"{video_name}_speed_{speed_str}.mp4"
            output_path = os.path.normpath(os.path.join(output_folder, out_filename))

            out = cv2.VideoWriter(output_path, fourcc, new_fps, frame_size)
            for frame in frames:
                out.write(frame)
            out.release()
            # print(f"Saved: {output_path}")
