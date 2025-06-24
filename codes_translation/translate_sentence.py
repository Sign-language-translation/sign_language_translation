import os
import time
from openai import AzureOpenAI
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2
import tempfile
# from codes_translation.translate_single_word import load_label_mapping, classify_json_file
from utils.test_mediapipe import extract_motion_data
import numpy as np
from models.local_models.classify_attn import load_label_mapping, classify_json_file

# Load environment variables from the .env file
load_dotenv()

# Constants for average word duration
MIN_WINDOW_SEC = 1
MAX_WINDOW_SEC = 2
START_TIME_STEP_SEC = 0.15
WINDOW_SIZE_STEP_SEC = 1
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AMOUNT_OF_GPT_CALLS = 5


def create_segments_list(video_duration):
    segments_list = []

    for start_sec in np.arange(0, video_duration - MIN_WINDOW_SEC + 0.001, START_TIME_STEP_SEC):
        for segment_duration in np.arange(MIN_WINDOW_SEC, MAX_WINDOW_SEC + 0.001, WINDOW_SIZE_STEP_SEC):
            end_sec = start_sec + segment_duration

            # Trim segment to not go past video duration
            if start_sec >= video_duration:
                continue
            if end_sec > video_duration:
                end_sec = video_duration

            # --- keep only two digits after the decimal point ---
            start_sec = round(start_sec, 2)
            end_sec = round(end_sec, 2)

            segments_list.append((start_sec, end_sec))

    return segments_list


def segment_video_with_opencv(duration, output_folder, cap, fps):
    segments = []

    for start_sec in np.arange(0, duration - MIN_WINDOW_SEC + 0.001, START_TIME_STEP_SEC):
        for segment_duration in np.arange(MIN_WINDOW_SEC, MAX_WINDOW_SEC + 0.001, WINDOW_SIZE_STEP_SEC):
            end_sec = start_sec + segment_duration

            # Trim segment to not go past video duration
            if start_sec >= duration:
                continue
            if end_sec > duration:
                end_sec = duration

            start_frame = int(start_sec * fps)
            end_frame = int(end_sec * fps)
            segment_filename = f"segment_{start_sec}_{end_sec}.mp4"
            segment_path = os.path.join(output_folder, segment_filename)

            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(segment_path, fourcc, fps, (width, height))

            for _ in range(end_frame - start_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)

            out.release()
            segments.append((segment_path, start_sec, end_sec))

    cap.release()
    return segments


def process_segments_with_threads(video_path, model_path, label_encoder_path):
    temp_folder = tempfile.mkdtemp()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    duration = round(duration, 2)

    # start_time = time.time()
    segments = segment_video_with_opencv(duration, temp_folder, cap, fps)
    # elapsed_time = time.time() - start_time
    # print(f"segment_video_with_opencv took {elapsed_time} seconds")

    model_filename = os.path.join(os.path.dirname(__file__), model_path)
    label_encoder_path = os.path.join(os.path.dirname(__file__), label_encoder_path)

    label_encoder = load_label_mapping(label_encoder_path)

    predictions = []  # <- list to store all results
    predictions_lock = threading.Lock()  # Lock to prevent race conditions

    print("Processing segments...\n")

    def classify_segment(segment_path, start, end):
        try:
            video_name = os.path.splitext(os.path.basename(segment_path))[0]
            folder_name = os.path.dirname(segment_path) + os.sep  # Ensure proper path joining
            data_frames = extract_motion_data(video_name, folder_name)

            prediction = classify_json_file(model_filename, data_frames, label_encoder)

        except Exception as e:
            print(f"  → Error: {e}\n")
            prediction = None

        with predictions_lock:
            predictions.append((start, end, prediction))  # Add to list in a thread-safe way

    # start_time = time.time()
    threads = []
    for segment_path, start, end in segments:
        thread = threading.Thread(target=classify_segment, args=(segment_path, start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Wait for all threads to finish

    # Sort by start time, then by end time
    sorted_predictions = sorted(predictions, key=lambda x: (x[0], x[1]))

    # elapsed_time = time.time() - start_time
    # print(f"classify_segments took {elapsed_time} seconds")

    # Print all results at the end
    print("=== Final Predictions ===")
    for start, end, pred in sorted_predictions:
        print(f"{start}-{end}s → {pred}")

    return sorted_predictions, duration


def build_prompt1(classification_text, estimated_word_count, video_duration):
    prompt = f"""
        You are analyzing a sign language video.

        Video duration: {round(video_duration, 1)} seconds.
        Estimated number of signed words: {estimated_word_count}.

        Gesture recognizer output:
        {classification_text}

        Your task:
        - Extract the most frequent and meaningful signed words.
        - Keep the words in the correct **temporal order** based on when they appear.
        - Return a **single English sentence** with space-separated words.
        - The sentence must be **grammatically sensible**.
        - If a **question word** (e.g., when, why) appears not at the beginning, assume it’s a classification error and discard it.
        - If a word appears more then 4 times in the same period of time and makes sense with the sentence, dont miss it. 
        - If a word appears only once or twice in the same period of time, dont put ot in the final sentence!!
        - Do not add any new words. Only use words from the list.
        - Do not include words that appear only once unless needed for grammar.
        - No punctuation. No explanation. Only the final sentence.
        """

    return prompt


def build_prompt2(classification_text, estimated_word_count, video_duration):
    prompt = f"""
       You are analyzing a sign language video.

       Video duration: {round(video_duration, 1)} seconds.
       Estimated number of signed words: {estimated_word_count}.

       Gesture recognizer output:
       {classification_text}

       From this list:
       - Choose the most **frequent** and likely signed words.
       - Keep them in the **correct temporal order** based on appearance.
       - Ensure the sentence is **grammatically correct and makes sense in English**.
       - Ignore words like "why", "what", "how", etc., if they appear in the middle or end of the sentence — this is likely a classification error.
       - Do NOT add any new words not in the list.
       - Output up to {estimated_word_count} words.
       - No punctuation, no explanations. Just return the sentence as a single line, with words separated by spaces.
       - If a word appears more then 4 times in the same period of time and makes sense with the sentence, dont miss it. 
       - If a word appears less then 3 times and doesnt makes sense with the sentence, skip it.
       """

    return prompt


def build_prompt3(classification_text, estimated_word_count):
    prompt = f"""
    You are given a list of time-aligned classifications, each representing a possible word spoken between specific time intervals in seconds.

    Each line follows this format:
    <start_time>-<end_time>s → <word>

    Your task is to infer which distinct words most likely exist in the original sentence. Consider repetition and overlap of time intervals as stronger evidence for a word.

    Only return the {estimated_word_count} most likely distinct words, in the most probable order they appear in the sentence. Return them as a space-separated string, no explanation.

    Here is the classification_text:
    {classification_text}

    Estimated word count: {estimated_word_count}
    """

    return prompt


def build_prompt4_summarize(prompt1_words, prompt2_words, prompt3_words):
    prompt = f"""
    You are given three lists of words from a sign language video analysis.

    List 1: {', '.join(prompt1_words)}
    List 2: {', '.join(prompt2_words)}
    List 3: {', '.join(prompt3_words)}

    Your task:
    - Choose a final list of words combining the most likely ones from all lists, the sentence should make sense.
    - Translate the chosen words into **Hebrew** using this dictionary:
    hello: שלום, thanks: תודה, need: צריך, now: עכשיו, when: מתי, why: למה, appointment: תור,
    schedule: לקבוע, arrive: להגיע, station: תחנה, bus: אוטובוס, phone: טלפון, place: מקום,
    help: לעזור, name: שם, no: לא, go: ללכת, come: לבוא, I: אני, you: אתה, home: בית,
    ticket: כרטיס, later: אחר כך, doctor: רופא, idCard: תעודת זהות, ambulance: אמבולנס,
    clinic: קופת חולים

    - Add appropriate Hebrew **linking words** (e.g., ל, עם, ב, מ, אל) to make a fluent and grammatically correct sentence.
    - Only use words from the dictionary and those provided.
    - No hallucinations, no extra words.
    - Output: one **correct Hebrew sentence**, no punctuation, no explanation.
    """

    return prompt


def call_gpt(message, client, deployment):
    chat_prompt = [{"role": "user", "content": [{"type": "text", "text": message}]}]
    # chat_prompt = [{"role": "user", "content": [{"type": "text", "text": msg}]} for msg in messages]

    completion = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        temperature=0.7,
        max_tokens=256
    )
    #
    # result = completion.choices[0].message.content
    # return [word.strip() for word in result.split("\n") if word.strip()]
    return completion.choices[0].message.content.strip()


def consolidate_answers(answers, client, deployment):
    joined_answers = "\n".join(f"Answer {i + 1}: {', '.join(ans)}" for i, ans in enumerate(answers))
    # final_prompt = f"""
    # You are given 5 different GPT responses that each analyzed a sign language video. Your task is to consolidate them into a single final list of signed words.
    #
    # Here are the answers:
    # {joined_answers}
    #
    # Return only one final list of the most likely signed words, in correct order. Be strict and consistent. No explanations, no punctuation. One word per line.
    # """

    final_prompt = f"""
    You are given {AMOUNT_OF_GPT_CALLS} GPT responses. Each one lists the signed words detected in a sign language video. Your task is to extract the **final list of signed words** based on majority agreement.

    Instructions:
    - Your goal is to reconstruct a meaningful and grammatically correct sentence in Hebrew.
    - DO NOT add words that appear in only one or two answers.
    - Use only words that appear in at least {AMOUNT_OF_GPT_CALLS // 2 + 1} of the answers.
    - Preserve the word order as it appeared in the original answers. DO NOT change the order unless needed for correct Hebrew grammar.
    - If a word appears in enough answers, use it in the same position where it commonly appears.
    - For example, if most responses place "מתי" at the beginning, keep it there.
    - The final sentence must make sense in Hebrew. Question words (like "מתי") should appear at the beginning.
    - Return a **single sentence**, with words separated by **a single space**.
    - Do NOT insert spaces between letters of a word — for example, this is WRONG: מ ת י
    - Do NOT include punctuation, explanations, or anything else — return only the final sentence.

    Here are the {AMOUNT_OF_GPT_CALLS} answers:
    {joined_answers}

    Return only the final sentence. One line. Words separated by spaces.
    """

    return call_gpt(final_prompt, client, deployment)


def get_sentence_translation_from_gpt(client, azure_deployment, predictions, segments_list, video_duration):
    # classification_text = "\n".join(
    #     f"{round(start, 1)}-{round(end, 1)}s → {pred or 'UNKNOWN'}"
    #     for start, end, pred in predictions
    # )
    classification_text = "\n".join(
        f"{round(start, 1)}-{round(end, 1)}s → {pred or 'UNKNOWN'}"
        for (start, end), pred in zip(segments_list, predictions)
    )
    estimated_word_count = round(video_duration / ((MIN_WINDOW_SEC + MAX_WINDOW_SEC) / 2))

    prompt1 = build_prompt1(classification_text, estimated_word_count, video_duration)
    prompt2 = build_prompt2(classification_text, estimated_word_count, video_duration)
    prompt3 = build_prompt3(classification_text, estimated_word_count)

    words1_response = call_gpt(prompt1, client, azure_deployment)
    words1 = words1_response.strip().split()

    words2_response = call_gpt(prompt2, client, azure_deployment)
    words2 = words2_response.strip().split()

    words3_response = call_gpt(prompt3, client, azure_deployment)
    words3 = words3_response.strip().split()

    print(f"\nPrompt1 Words: {words1}")
    print(f"Prompt2 Words: {words2}")
    print(f"Prompt3 Words: {words3}")

    final_prompt = build_prompt4_summarize(words1, words2, words3)
    print("\nCalling GPT for final Hebrew sentence...")
    final_sentence = call_gpt(final_prompt, client, azure_deployment)

    print("\n=== Final Hebrew Sentence ===")
    print(final_sentence)

    return final_sentence


def summarize_predictions_gpt(predictions, segments_list, video_duration):
    endpoint = os.getenv("ENDPOINT_URL", "https://isl-translation.openai.azure.com/")
    deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY", AZURE_OPENAI_API_KEY)

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2024-05-01-preview",
    )
    # without threads:
    # answers = []

    # for i in range(AMOUNT_OF_GPT_CALLS):
    #     answers.append(get_sentence_translation_from_gpt(client, deployment, predictions, video_duration))

    # Generate the base prompt
    # prompt = generate_prompt(predictions, video_duration)
    # part1, part2, part3 = build_prompt_parts(predictions, video_duration)

    print(f"Sending {AMOUNT_OF_GPT_CALLS} GPT requests to get individual predictions...")
    # answers = [call_gpt(prompt, client, deployment) for _ in range(5)]
    # answers = [
    #     call_gpt([part1, part2, part3], client, deployment)
    #     for _ in range(5)
    # ]

    # with threads:
    answers = [None] * AMOUNT_OF_GPT_CALLS

    with ThreadPoolExecutor(max_workers=AMOUNT_OF_GPT_CALLS) as executor:
        futures = {
            executor.submit(get_sentence_translation_from_gpt, client, deployment, predictions, segments_list, video_duration): i
            for i in range(AMOUNT_OF_GPT_CALLS)
        }

        for future in as_completed(futures):
            idx = futures[future]
            try:
                answers[idx] = future.result()
            except Exception as e:
                print(f"Error in GPT call {idx + 1}: {e}")
                answers[idx] = ""

    for i, answer in enumerate(answers, 1):
        print(f"Answer {i}: {answer}")

    print("\nConsolidating the 5 answers into a final result...")
    final_answer = consolidate_answers(answers, client, deployment)

    print("\nFinal consolidated answer:")
    print(final_answer)

    return final_answer



from server_client.client import prepare_video_payload, send_video_payload, get_video_duration
def translate_video_to_text(video_path, model_path, label_encoder_path):
    # predictions, video_duration = process_segments_with_threads(video_path, model_path, label_encoder_path)
    video_duration = get_video_duration(video_path)
    segments_list = create_segments_list(video_duration)
    payload = prepare_video_payload(video_path, segments_list)
    predictions = send_video_payload(payload)
    # start_time = time.time()
    translation_text = summarize_predictions_gpt(predictions, segments_list, video_duration)
    # elapsed_time = time.time() - start_time

    # print(f"summarize_predictions_gpt took {elapsed_time} seconds")
    return translation_text