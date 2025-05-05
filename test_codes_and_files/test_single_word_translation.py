import time
import os
from codes_translation.translate_single_word import classify_single_word
import shutil
from datetime import datetime

INPUT_FOLDER_PATH_OF_VIDEOS = 'single_word_videos'
TEMP_FOLDER_PATH_OF_JSONS = 'single_word_videos/jsons'
AMOUNT_OF_VARIATIONS = 30
MODEL_FILE_PATH = f'../models/3d_rnn_cnn_on_{AMOUNT_OF_VARIATIONS}_vpw.keras'
LABEL_ENCODER_FILE_PATH = f'../models/label_encoder_3d_rnn_cnn_{AMOUNT_OF_VARIATIONS}_vpw.pkl'
LOG_SINGLE_WORD_FOLDER = 'logs/logs_single_word'

# Add filenames here if not running all files
PREDEFINED_FILES = [
    "saturday_5.mp4",
    "you_3.mp4",
    "angry_4.mp4",
    "far_6.mp4"
]

def extract_expected_result(filename):
    return filename.split('_')[0]

def get_test_cases(run_all_files=False):
    if run_all_files:
        video_files = [f for f in os.listdir(INPUT_FOLDER_PATH_OF_VIDEOS) if f.endswith('.mp4')]
    else:
        video_files = PREDEFINED_FILES

    test_cases = [
        {
            "video_filename": f,
            "expected_result": extract_expected_result(f)
        }
        for f in video_files
    ]
    return test_cases

def delete_the_json_folder(folder_path):
    # Delete the folder
    try:
        shutil.rmtree(folder_path)
        print(f"Old files were deleted at {folder_path}")
    except OSError as e:
        print(f"Error: {e.strerror}")

def log(message, log_lines, enable_logging):
    print(message)
    if enable_logging:
        log_lines.append(message)

def create_log_file(log_folder, model_file_path, amount_of_test_cases, string_type_of_test):
    os.makedirs(log_folder, exist_ok=True)
    model_name = os.path.basename(model_file_path).replace('.keras', '')
    today_str = datetime.now().strftime('%d-%m-%Y')
    time_str = datetime.now().strftime('%H-%M')
    log_filename = f"test_{model_name}__{amount_of_test_cases}_{string_type_of_test}__{today_str}__{time_str}.txt"
    log_path = os.path.join(log_folder, log_filename)

    return log_path

def test_single_word_classification(run_all_files=False, enable_logging=True):
    test_cases = get_test_cases(run_all_files)
    all_results = []
    log_lines = []
    log_path = None

    # Ensure the folder exists
    os.makedirs(TEMP_FOLDER_PATH_OF_JSONS, exist_ok=True)
    os.makedirs(LOG_SINGLE_WORD_FOLDER, exist_ok=True)


    # Prepare log file name if logging is on
    if enable_logging:
        log_path = create_log_file(LOG_SINGLE_WORD_FOLDER, MODEL_FILE_PATH, len(test_cases), "words")

    for test_case in test_cases:
        video_filename = test_case["video_filename"]
        expected_result = test_case["expected_result"]

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

    delete_the_json_folder(TEMP_FOLDER_PATH_OF_JSONS)

    log("\n=== Single Word Test Summary ===", log_lines, enable_logging)
    total_tests = len(all_results)
    passed_tests = 0

    for idx, res in enumerate(all_results, 1):
        video = res["video"]
        received = res["received_result"]
        expected = res["expected_result"]
        elapsed = res["elapsed_time"]

        log(f"\nTest {idx}/{total_tests} — {video}", log_lines, enable_logging)
        log(f"Time taken: {elapsed:.2f} seconds", log_lines, enable_logging)

        if received == expected:
            log("✅ Test passed", log_lines, enable_logging)
            passed_tests += 1
        else:
            log("❌ Test failed", log_lines, enable_logging)
            log(f"Expected: {expected}", log_lines, enable_logging)
            log(f"Received: {received}", log_lines, enable_logging)

        # Final summary
        success_rate = (passed_tests / total_tests) * 100
        log(f"\n=== Conclusion: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%) ===", log_lines,
            enable_logging)

        if enable_logging:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_lines))
            print(f"\n📝 Log saved to {log_path}")

if __name__ == "__main__":
    test_single_word_classification(run_all_files=True)
