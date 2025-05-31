import time
import os
from datetime import datetime
from codes_translation.translate_sentence import translate_video_to_text, call_gpt
from test_single_word_translation import log, create_log_file
from openai import AzureOpenAI
import re


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
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')

def test_split_a_sentence(enable_logging=True):

    test_cases = [
        {
            "input_video": "I_arrive_clinic_later_yanoos_2.mp4",
            "expected_result": ["I", "arrive", "clinic", "later"],
            "hebrew_translation":"אני אגיע לקופת חולים אחר כך"
        },
        {
            "input_video": "I_arrive_clinic_later_yanoos_1.mp4",
            "expected_result": ["I", "arrive", "clinic", "later"],
            "hebrew_translation": "אני אגיע לקופת חולים אחר כך"
        },
        # {
        #     "input_video": "why_I_need_phone_yanoos_2.mp4",
        #     "expected_result": ["why", "I", "need", "phone"],
        #     "hebrew_translation": "למה אני צריך טלפון"
        # },
        # {
        #     "input_video": "why_I_need_phone_yanoos_1.mp4",
        #     "expected_result": ["why", "I", "need", "phone"],
        #     "hebrew_translation": "למה אני צריך טלפון"
        # },
        # {
        #     "input_video": "when_schedule_appointment_yanoos_2.mp4",
        #     "expected_result": ["when", "schedule", "appointment"],
        #     "hebrew_translation": "מתי לקבוע תור"
        # },
        # {
        #     "input_video": "when_schedule_appointment_yanoos_1.mp4",
        #     "expected_result": ["when", "schedule", "appointment"],
        #     "hebrew_translation": "מתי לקבוע תור"
        # },
        # {
        #     "input_video": "thanks_I_no_need_ticket_yanoos_2.mp4",
        #     "expected_result": ["thanks", "I", "no", "need", "ticket"],
        #     "hebrew_translation": "תודה אני לא צריך כרטיס"
        # },
        # {
        #     "input_video": "thanks_I_no_need_ticket_yanoos_1.mp4",
        #     "expected_result": ["thanks", "I", "no", "need", "ticket"],
        #     "hebrew_translation": "תודה אני לא צריך כרטיס"
        # },
        # {
        #     "input_video": "hello_I_need_doctor_yanoos_1.mp4",
        #     "expected_result": ["hello", "I", "need", "doctor"],
        #     "hebrew_translation": "שלום אני צריך רופא"
        # },
        # {
        #     "input_video": "I_go_station_bus_yanoos_2.mp4",
        #     "expected_result": ["I", "go", "station", "bus"],
        #     "hebrew_translation": "אני הולך לתחנת אוטובוס"
        # },
        # {
        #     "input_video": "I_go_station_bus_yanoos_1.mp4",
        #     "expected_result": ["I", "go", "station", "bus"],
        #     "hebrew_translation": "אני הולך לתחנת אוטובוס"
        # },
        # {
        #     "input_video": "when_come_ambulance_yanoos_2.mp4",
        #     "expected_result": ["when", "come", "ambulance"],
        #     "hebrew_translation": "מתי יגיע האמבולנס"
        # },
        # {
        #     "input_video": "when_come_ambulance_yanoos_1.mp4", # the first word is translated to why even that it appears only once!
        #     "expected_result": ["when", "come", "ambulance"],
        #     "hebrew_translation": "מתי יגיע האמבולנס"
        # },
        # {
        #     "input_video": "I_need_go_home_yanoos_2.mp4",
        #     "expected_result": ["I", "need", "go", "home"],
        #     "hebrew_translation": "אני צריך ללכת הביתה"
        # },
        # {
        #     "input_video": "I_need_go_home_yanoos_1.mp4",
        #     "expected_result": ["I", "need", "go", "home"],
        #     "hebrew_translation": "אני צריך ללכת הביתה"
        # },
        # {
        #     "input_video": "when_come_appointment_yanoos_2.mp4",
        #     "expected_result": ["when", "come", "appointment"],
        #     "hebrew_translation": "מתי יבוא התור"
        # },
        # {
        #     "input_video": "when_come_appointment_yanoos_1.mp4",
        #     "expected_result": ["when", "come", "appointment"],
        #     "hebrew_translation": "מתי יבוא התור"
        # },
        # {
        #     "input_video": "you_need_idCard_yanoos_1.mp4",
        #     "expected_result": ["you", "need", "idCard"],
        #     "hebrew_translation": "אתה צריך תעודת זהות"
        # },
        # {
        #     "input_video": "you_need_idCard_yanoos_2.mp4",
        #     "expected_result": ["you", "need", "idCard"],
        #     "hebrew_translation": "אתה צריך תעודת זהות"
        # },
        # {
        #     "input_video": "I_need_doctor_yanoos_1.mp4",
        #     "expected_result": ["I", "need", "doctor"],
        #     "hebrew_translation": "אני צריך רופא"
        # },
        # {
        #     "input_video": "I_need_doctor_yanoos_2.mp4",
        #     "expected_result": ["I", "need", "doctor"],
        #     "hebrew_translation": "אני צריך רופא"
        # },
        # {
        #     "input_video": "I_need_doctor_yael_1.mp4",
        #     "hebrew_translation": "אני צריך רופא"
        # },
        # {
        #     "input_video": "I_need_doctor_yael_2.mp4",
        #     "hebrew_translation": "אני צריך רופא"
        # },
        # {
        #     "input_video": "I_need_schedule_appointment_yael.mp4",
        #     "hebrew_translation": "אני צריך לקבוע תור"
        # },
        # {
        #     "input_video": "I_need_schedule_appointment_lena.mp4",
        #     "hebrew_translation": "אני צריך לקבוע תור"
        # },


        # {
        #     "input_video": "I_need_schedule_appointment_doctor_yanoos.mp4",
        #     "hebrew_translation": "אני צריך לקבוע תור לרופא"
        # },
        # {
        #     "input_video": "I_need_schedule_appointment_doctor_lena.mp4",
        #     "hebrew_translation": "אני צריך לקבוע תור לרופא"
        # },
        # {
        #     "input_video": "when_come_clinic_yanoos.mp4",
        #     "hebrew_translation": "מתי לבוא לקופת חולים"
        # },
        # {
        #     "input_video": "when_come_clinic_lena.mp4",
        #     "hebrew_translation": "מתי לבוא לקופת חולים"
        # },
        # {
        #     "input_video": "when_come_clinic_yael.mp4",
        #     "hebrew_translation": "מתי לבוא לקופת חולים"
        # },
        # {
        #     "input_video": "when_come_clinic_raanan.mp4",
        #     "hebrew_translation": "מתי לבוא לקופת חולים"
        # },
        # {
        #     "input_video": "I_place_station_bus_raanan.mp4",
        #     "hebrew_translation": "אני במקום תחנת אוטובוס"
        # },
        # {
        #     "input_video": "I_need_doctor_yanoos_live.mp4",
        #     "hebrew_translation": "אני צריך רופא"
        # },
        # {
        #     "input_video": "I_need_doctor_yael_live.mp4",
        #     "hebrew_translation": "אני צריך רופא"
        # },
        # {
        #     "input_video": "I_need_schedule_appointment_yael_live.mp4",
        #     "hebrew_translation": "אני צריך לקבוע תור"
        # },
        # {
        #     "input_video": "I_need_schedule_appointment_yanoos_live.mp4",
        #     "hebrew_translation": "אני צריך לקבוע תור"
        # },

    ]

    all_received_results = []
    log_lines = []
    log_path = None

    # Prepare log file name if logging is on
    if enable_logging:
        log_path = create_log_file(LOG_SENTENCE_FOLDER, MODEL_FILE_PATH, len(test_cases), "sentences")

    for test_case in test_cases:
        videos_name = test_case["input_video"]
        videos_full_path = VIDEOS_FOLDER + videos_name

        print(f"\n--- Running test for: {videos_name} ---")
        start_time = time.time()
        received_result = translate_video_to_text(videos_full_path, MODEL_FILE_PATH, LABEL_ENCODER_FILE_PATH)
        elapsed_time = time.time() - start_time

        all_received_results.append({
            "input_video": videos_name,
            "received_result": received_result,
            "elapsed_time": elapsed_time,
            "hebrew_translation": test_case["hebrew_translation"]
        })

    log("\n=== Test Summary ===", log_lines, enable_logging)

    total_tests = len(all_received_results)
    for idx, result in enumerate(all_received_results, start=1):
        input_video = result["input_video"]
        received_result = result["received_result"]
        hebrew_translation = result["hebrew_translation"]
        elapsed_time = result["elapsed_time"]

        log(f"\nTest {idx}/{total_tests} — {input_video}", log_lines, enable_logging)
        log(f"Time taken: {elapsed_time:.2f} seconds", log_lines, enable_logging)

        endpoint = os.getenv("ENDPOINT_URL", "https://isl-translation.openai.azure.com/")
        deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY", AZURE_OPENAI_API_KEY)

        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=subscription_key,
            api_version="2024-05-01-preview",
        )

        # Compute semantic similarity using GPT
        similarity_prompt = (
            f"Compare the following two Hebrew sentences and estimate how semantically similar they are.\n"
            f"Sentence 1: {received_result}\n"
            f"Sentence 2: {hebrew_translation}\n\n"
            f"Use a scale from 0 to 100.\n"
            f"Only return a single number representing the semantic similarity percentage.\n"
            f"Do not add explanations or extra text.\n\n"
            f"Note: Consider words like 'אגיע', 'אלך', and 'אבוא' to mean the same thing (going/arriving).\n"
            f"Also treat minor grammatical differences or word order changes as equivalent.\n"
            f"Examples:\n"
            f"Sentence 1: אני הולך לקופת חולים אחר כך\n"
            f"Sentence 2: אני אגיע לקופת חולים אחר כך\n"
            f"→ Output: 97"
        )

        try:
            similarity_response = call_gpt(similarity_prompt, client, deployment)
            success_rate = float(re.search(r'\d+', similarity_response).group())
        except Exception as e:
            print(f"GPT similarity check failed: {e}")
            success_rate = 0

        result["similarity"] = success_rate

        log(f"Expected: {hebrew_translation}", log_lines, enable_logging)
        log(f"Received: {received_result}", log_lines, enable_logging)
        log(f"Semantic Similarity: {success_rate:.1f}%", log_lines, enable_logging)

    # === Stats Summary ===
    similarity_scores = [result["similarity"] for result in all_received_results if "similarity" in result]

    if similarity_scores:
        total_tests = len(similarity_scores)
        perfect_matches = sum(1 for s in similarity_scores if s == 100)
        high_scores = sum(1 for s in similarity_scores if s >= 90)
        low_scores = sum(1 for s in similarity_scores if s < 70)
        avg_score = sum(similarity_scores) / total_tests
        min_score = min(similarity_scores)
        max_score = max(similarity_scores)

        log_lines.append("\nStatistical summary of test results:")
        log_lines.append(f"Total number of tests: {total_tests}")
        log_lines.append(f"Tests with perfect similarity (100%): {perfect_matches}")
        log_lines.append(f"Average similarity score: {avg_score:.1f}%")
        log_lines.append(f"Tests with similarity score 90% or higher: {high_scores}")
        log_lines.append(f"Tests with similarity score below 70%: {low_scores}")
        log_lines.append(f"Minimum similarity score: {min_score:.1f}%")
        log_lines.append(f"Maximum similarity score: {max_score:.1f}%")

    if enable_logging:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(log_lines))
        print(f"\n Log saved to {log_path}")

if __name__ == "__main__":
    test_split_a_sentence()