import time
import os
from datetime import datetime
from codes_translation.translate_sentence import translate_video_to_text
from test_single_word_translation import log, create_log_file

VIDEOS_FOLDER = "sentence_videos/"
LOG_SENTENCE_FOLDER = 'logs/logs_sentence/'
AMOUNT_OF_VARIATIONS = 10
# MODEL_FILE_PATH = f'../models/3d_rnn_cnn_on_{AMOUNT_OF_VARIATIONS}_vpw.keras'
# LABEL_ENCODER_FILE_PATH = f'../models/label_encoder_3d_rnn_cnn_{AMOUNT_OF_VARIATIONS}_vpw.pkl'
# model 4
# MODEL_FILE_PATH = '..\\models\\attn-4_666_vpw.keras'
# LABEL_ENCODER_FILE_PATH = '..\\models\\label_encoder_attn-4_666_vpw.pkl'
# model 5
MODEL_FILE_PATH = '..\\models\\model-5_14000_vpw.keras'
LABEL_ENCODER_FILE_PATH = '..\\models\\label_encoder_model-5_14000_vpw.pkl'

def test_split_a_sentence(enable_logging=True):

    test_cases = [
        {
            "input_video": "I_arrive_clinic_later_yanoos_2.mp4",
            "expected_result": ["I", "arrive", "clinic", "later"],
            "hebrew_translation": "אני מגיע לקופת חולים אחר כך"
        },
        {
            "input_video": "I_arrive_clinic_later_yanoos_1.mp4",
            "expected_result": ["I", "arrive", "clinic", "later"],
            "hebrew_translation": "אני מגיע לקופת חולים אחר כך"
        },
        {
            "input_video": "why_I_need_phone_yanoos_2.mp4",
            "expected_result": ["why", "I", "need", "phone"],
            "hebrew_translation": "למה אני צריך טלפון"
        },
        {
            "input_video": "why_I_need_phone_yanoos_1.mp4",
            "expected_result": ["why", "I", "need", "phone"],
            "hebrew_translation": "למה אני צריך טלפון"
        },
        {
            "input_video": "when_schedule_appointment_yanoos_2.mp4",
            "expected_result": ["when", "schedule", "appointment"],
            "hebrew_translation": "מתי לקבוע תור"
        },
        {
            "input_video": "when_schedule_appointment_yanoos_1.mp4",
            "expected_result": ["when", "schedule", "appointment"],
            "hebrew_translation": "מתי לקבוע תור"
        },
        {
            "input_video": "thanks_I_no_need_ticket_yanoos_2.mp4",
            "expected_result": ["thanks", "I", "no", "need", "ticket"],
            "hebrew_translation": "תודה אני לא צריך כרטיס"
        },
        {
            "input_video": "thanks_I_no_need_ticket_yanoos_1.mp4",
            "expected_result": ["thanks", "I", "no", "need", "ticket"],
            "hebrew_translation": "תודה אני לא צריך כרטיס"
        },
        {
            "input_video": "hello_I_need_doctor_yanoos_1.mp4",
            "expected_result": ["hello", "I", "need", "doctor"],
            "hebrew_translation": "שלום אני צריך רופא"
        },
        {
            "input_video": "I_go_station_bus_yanoos_2.mp4",
            "expected_result": ["I", "go", "station", "bus"],
            "hebrew_translation": "אני הולך לתחנת אוטובוס"
        },
        {
            "input_video": "I_go_station_bus_yanoos_1.mp4",
            "expected_result": ["I", "go", "station", "bus"],
            "hebrew_translation": "אני הולך לתחנת אוטובוס"
        },
        {
            "input_video": "when_come_ambulance_yanoos_2.mp4",
            "expected_result": ["when", "come", "ambulance"],
            "hebrew_translation": "מתי יגיע האמבולנס"
        },
        {
            "input_video": "when_come_ambulance_yanoos_1.mp4", # the first word is translated to why even that it appears only once!
            "expected_result": ["when", "come", "ambulance"],
            "hebrew_translation": "מתי יגיע האמבולנס"
        },
        {
            "input_video": "I_need_go_home_yanoos_2.mp4",
            "expected_result": ["I", "need", "go", "home"],
            "hebrew_translation": "אני צריך ללכת הביתה"
        },
        {
            "input_video": "I_need_go_home_yanoos_1.mp4",
            "expected_result": ["I", "need", "go", "home"],
            "hebrew_translation": "אני צריך ללכת הביתה"
        },
        {
            "input_video": "when_come_appointment_yanoos_2.mp4",
            "expected_result": ["when", "come", "appointment"],
            "hebrew_translation": "מתי יגיע התור"
        },
        {
            "input_video": "when_come_appointment_yanoos_1.mp4",
            "expected_result": ["when", "come", "appointment"],
            "hebrew_translation": "מתי יגיע התור"
        },
        {
            "input_video": "you_need_idCard_yanoos_1.mp4",
            "expected_result": ["you", "need", "idCard"],
            "hebrew_translation": "אתה צריך תעודת זהות"
        },
        {
            "input_video": "you_need_idCard_yanoos_2.mp4", # inaccurate!
            "expected_result": ["you", "need", "idCard"],
            "hebrew_translation": "אתה צריך תעודת זהות"
        },
        {
            "input_video": "I_need_doctor_yanoos_1.mp4", # Accurately translated
            "expected_result": ["I", "need", "doctor"],
            "hebrew_translation": "אני צריך רופא"
        },
        {
            "input_video": "I_need_doctor_yanoos_2.mp4", # inaccurate!
            "expected_result": ["I", "need", "doctor"],
            "hebrew_translation": "אני צריך רופא"
        }
    ]

    all_received_results = []
    log_lines = []
    log_path = None

    # Prepare log file name if logging is on
    if enable_logging:
        log_path = create_log_file(LOG_SENTENCE_FOLDER, MODEL_FILE_PATH, len(test_cases), "sentences")

    for test_case in test_cases:
        videos_name = test_case["input_video"]
        expected_result = test_case["expected_result"]
        videos_full_path = VIDEOS_FOLDER + videos_name

        print(f"\n--- Running test for: {videos_name} ---")
        start_time = time.time()
        received_result = translate_video_to_text(videos_full_path, MODEL_FILE_PATH, LABEL_ENCODER_FILE_PATH)
        elapsed_time = time.time() - start_time

        all_received_results.append({
            "input_video": videos_name,
            "received_result": received_result,
            "expected_result": expected_result,
            "elapsed_time": elapsed_time
        })

    log("\n=== Test Summary ===", log_lines, enable_logging)

    total_tests = len(all_received_results)
    for idx, result in enumerate(all_received_results, start=1):
        input_video = result["input_video"]
        received_result = result["received_result"]
        expected_result = result["expected_result"]
        elapsed_time = result["elapsed_time"]

        log(f"\nTest {idx}/{total_tests} — {input_video}", log_lines, enable_logging)
        log(f"Time taken: {elapsed_time:.2f} seconds", log_lines, enable_logging)

        # Unordered match: count how many expected words are in received_result
        expected_set = set(expected_result)
        received_set = set(received_result)
        correct = len(expected_set & received_set)
        total_expected = len(expected_result)
        success_rate = (correct / total_expected) * 100 if total_expected > 0 else 0

        if received_result == expected_result:
            log("✅ Test passed", log_lines, enable_logging)
            log("Result: " + " ".join(received_result), log_lines, enable_logging)
        else:
            log("❌ Test failed", log_lines, enable_logging)
            log(f"Expected: {expected_result}", log_lines, enable_logging)
            log(f"Received: {received_result}", log_lines, enable_logging)

        log(f"✔️ Success: {correct}/{total_expected} words correct ({success_rate:.1f}%)", log_lines, enable_logging)

        if enable_logging:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_lines))
            print(f"\n📝 Log saved to {log_path}")

if __name__ == "__main__":
    test_split_a_sentence()