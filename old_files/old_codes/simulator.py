from old_files.old_codes.video_cropper import extract_frames

import os
import cv2
import csv

# Global variables for mouse callback
drawing = False  # True if the mouse is pressed
ix, iy = -1, -1  # Initial coordinates
rectangle = None  # Stores the rectangle details


def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, rectangle

    # Start drawing when the left mouse button is pressed
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    # Update rectangle dimensions while dragging
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            rectangle = (ix, iy, x - ix, y - iy)

    # Finish drawing when the left mouse button is released
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rectangle = (ix, iy, x - ix, y - iy)


def process_frames(frames_directory, csv_output_path,create_frames=False):
    global rectangle
    if create_frames:
        extract_frames("/Users/raananpevzner/PycharmProjects/sign_language_translation/original_videos")
    # Initialize CSV file
    with open(csv_output_path, mode="w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Frame Name", "X", "Y", "Width", "Height"])  # Header

        # Iterate through all frame images in the directory
        for frame_name in sorted(os.listdir(frames_directory)):
            if frame_name.endswith(".png"):  # Process only PNG files
                frame_path = os.path.join(frames_directory, frame_name)

                # Load the frame
                frame = cv2.imread(frame_path)
                if frame is None:
                    print(f"Skipping {frame_name}, not a valid image.")
                    continue

                # Create a clone for displaying and drawing
                clone = frame.copy()
                rectangle = None

                # Set up OpenCV window and mouse callback
                cv2.namedWindow("Frame")
                cv2.setMouseCallback("Frame", draw_rectangle)

                print(f"Processing: {frame_name}")
                while True:
                    display_frame = clone.copy()

                    # Draw the rectangle if it exists
                    if rectangle:
                        x, y, w, h = rectangle
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    cv2.imshow("Frame", display_frame)
                    key = cv2.waitKey(1) & 0xFF

                    # Press 's' to save rectangle and move to next frame
                    if key == ord("s"):
                        if rectangle:
                            x, y, w, h = rectangle
                            csv_writer.writerow([frame_name, x, y, abs(w), abs(h)])
                        break

                    # Press 'n' to skip without saving
                    elif key == ord("n"):
                        print(f"Skipping {frame_name}")
                        break

                    # Press 'q' to quit the program
                    elif key == ord("q"):
                        print("Exiting...")
                        cv2.destroyAllWindows()
                        return

                # Close the current frame window
                cv2.destroyWindow("Frame")

    print(f"Results saved to {csv_output_path}")


# Example usage:
frames_directory = "/Users/raananpevzner/PycharmProjects/sign_language_translation/sim_frames"
csv_output_path = "/Users/raananpevzner/PycharmProjects/sign_language_translation/sim_results.csv"
process_frames(frames_directory, csv_output_path)
