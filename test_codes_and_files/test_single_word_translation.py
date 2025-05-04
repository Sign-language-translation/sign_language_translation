import time
from codes_translation.translate_single_word import classify_single_word

INPUT_FOLDER_PATH_OF_VIDEOS = 'single_word_videos'
TEMP_FOLDER_PATH_OF_JSONS = 'single_word_videos/jsons'
MODEL_FILE_PATH = '../models/3d_rnn_cnn_on_30_vpw.keras'
LABEL_ENCODER_FILE_PATH = '../models/label_encoder_3d_rnn_cnn_30_vpw.pkl'

def test_single_word_classification():
    test_cases = [
        {
            "video_filename": "saturday_5.mp4",
            "expected_result": "saturday"
        },
        {
            "video_filename": "you_3.mp4",
            "expected_result": "you"
        },
        {
            "video_filename": "angry_4.mp4",
            "expected_result": "angry"
        },
        {
            "video_filename": "far_6.mp4",
            "expected_result": "far"
        }
    ]

    all_results = []

    for test_case in test_cases:
        video_filename = test_case["video_filename"]
        expected_result = test_case["expected_result"]
        # video_path = f"{INPUT_FOLDER_PATH_OF_VIDEOS}/{video_filename}"

        print(f"\n--- Running test for: {video_filename} ---")
        start_time = time.time()
        result = classify_single_word(INPUT_FOLDER_PATH_OF_VIDEOS, video_filename, TEMP_FOLDER_PATH_OF_JSONS, MODEL_FILE_PATH, LABEL_ENCODER_FILE_PATH)
        elapsed_time = time.time() - start_time

        all_results.append({
            "video": video_filename,
            "received_result": result,
            "expected_result": expected_result,
            "elapsed_time": elapsed_time
        })

    print("\n=== Single Word Test Summary ===")
    total_tests = len(all_results)
    for idx, res in enumerate(all_results, 1):
        video = res["video"]
        received = res["received_result"]
        expected = res["expected_result"]
        elapsed = res["elapsed_time"]

        print(f"\nTest {idx}/{total_tests} — {video}")
        print(f"Time taken: {elapsed:.2f} seconds")

        if received == expected:
            print("✅ Test passed")
        else:
            print("❌ Test failed")
            print(f"Expected: {expected}")
            print(f"Received: {received}")

if __name__ == "__main__":
    test_single_word_classification()
