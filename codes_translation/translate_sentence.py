import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import threading
import cv2
import tempfile
# from codes_translation.translate_single_word import load_label_mapping, classify_json_file
from utils.test_mediapipe import extract_motion_data
import numpy as np
from test_codes_and_files.classify_attn import load_label_mapping, classify_json_file

# Load environment variables from the .env file
load_dotenv()

# Constants for average word duration
MIN_WINDOW_SEC = 1
MAX_WINDOW_SEC = 2
STEP_SIZE_SEC = 0.5
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')

def segment_video_with_opencv(duration, output_folder, cap, fps):
    segments = []

    for start_sec in np.arange(0, duration - MIN_WINDOW_SEC + 0.001, STEP_SIZE_SEC):
        for window_size in np.arange(MIN_WINDOW_SEC, MAX_WINDOW_SEC + 0.001, STEP_SIZE_SEC):
            end_sec = start_sec + window_size

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

    segments = segment_video_with_opencv(duration, temp_folder, cap, fps)

    model_filename = os.path.join(os.path.dirname(__file__), model_path)
    label_encoder_path = os.path.join(os.path.dirname(__file__), label_encoder_path)

    # model_filename = os.path.abspath(
    #     os.path.join(os.path.dirname(__file__), '..', 'models', model_path))
    # label_encoder_path = os.path.abspath(
    #     os.path.join(os.path.dirname(__file__), '..', 'models', label_encoder_path))

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

            print(f"  → Prediction: {prediction}\n")
        except Exception as e:
            print(f"  → Error: {e}\n")
            prediction = None

        with predictions_lock:
            predictions.append((start, end, prediction))  # Add to list in a thread-safe way

    threads = []
    for segment_path, start, end in segments:
        thread = threading.Thread(target=classify_segment, args=(segment_path, start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Wait for all threads to finish

    # Sort by start time, then by end time
    sorted_predictions = sorted(predictions, key=lambda x: (x[0], x[1]))

    # Print all results at the end
    print("=== Final Predictions ===")
    for start, end, pred in sorted_predictions:
        print(f"{start}-{end}s → {pred}")

    return sorted_predictions, duration

def generate_prompt(predictions, video_duration):
    classification_text = "\n".join(
        f"{round(start, 1)}-{round(end, 1)}s → {pred or 'UNKNOWN'}"
        for start, end, pred in predictions
    )

    estimated_word_count = round(video_duration / ((MIN_WINDOW_SEC + MAX_WINDOW_SEC) / 2))

    # prompt = f"""
    # You are analyzing segments of a Hebrew Sign Language video to determine the most likely words that were signed.
    #
    # - The total video duration is {round(video_duration, 1)} seconds.
    # - On average, each word lasts between {MIN_WINDOW_SEC} and {MAX_WINDOW_SEC} seconds.
    # - Based on this, the total number of distinct words in the video should be approximately {estimated_word_count}.
    #
    # You are given classification results for gesture recognition. Each line represents a time window and the word the model detected for that segment:
    #
    # {classification_text}
    #
    # Your task is to extract only the **most likely words** signed in the video. Follow these rules strictly:
    #
    # 1. Only include a word if it appears in **at least 3 overlapping consecutive segments AND those segments together span at least 1.5 seconds of the timeline**.
    # 2. Ignore any word that appears in only 1 or 2 segments, or appears in non-continuous/isolated time windows.
    # 3. Do NOT include a word that appears briefly at the start or in the middle unless it persists clearly.
    # 4. Favor words that span **long stretches of time** or appear in **dense overlapping windows** — these are more reliable.
    # 5. Consider the average word duration. Do not include more than 5 words in total. Most likely, the number of signed words is around {estimated_word_count}.
    # 6. Return only the selected words, in order of appearance in the video. No extra explanations, no punctuation.
    #
    # Be strict: Do not include uncertain or short-lived classifications like "no" or "far" unless they clearly follow the rules above.
    # """

    prompt = f"""
    You are analyzing segments of a Hebrew Sign Language video to determine the most likely words that were signed.

    - The total video duration is {round(video_duration, 1)} seconds.
    - On average, each word lasts between {MIN_WINDOW_SEC} and {MAX_WINDOW_SEC} seconds.
    - Based on this, the total number of distinct words in the video should be approximately {estimated_word_count}.

    You are given classification results for gesture recognition. Each line represents a time window and the word the model detected for that segment:

    {classification_text}

    Your task is to extract only the most likely words signed in the video, and then return a fluent and grammatically correct sentence in Hebrew using only the translated Hebrew words and appropriate linking/preposition words.

    Follow these strict rules:

    1. Only include a word if it appears in at least 3 overlapping consecutive segments AND those segments together span at least 1 second of the timeline.
    2. Ignore any word that appears in only 1 or 2 segments, or appears in non-continuous/isolated time windows.
    3. Most likely, the number of signed words is around {estimated_word_count}.
    4. After selecting the valid words, translate them into Hebrew using the following dictionary. When constructing the sentence, you may use any grammatically appropriate form of the word, such as gender, number, or tense variations. For example, "go" may be translated as "ללכת", "הלך", "הולך", "הולכת", or "הולכים" based on the sentence context, if the person that is talking in the sentence is I(me), assume that it is a man.

    hello: שלום  
    thanks: תודה  
    need: צריך  
    now: עכשיו  
    when: מתי  
    why: למה  
    appointment: תור  
    schedule: לקבוע  
    arrive: להגיע  
    station: תחנה  
    bus: אוטובוס  
    phone: טלפון  
    place: מקום  
    help: לעזור  
    name: שם  
    no: לא  
    go: ללכת  
    come: לבוא  
    I: אני  
    you: אתה  
    home: בית  
    ticket: כרטיס  
    later: אחר כך  
    doctor: רופא  
    idCard: תעודת זהות  
    ambulance: אמבולנס  
    clinic: קופת חולים
 
    7. Use appropriate linking words (such as ל, אל, עם, ואז, לכן, ב, מ) to form a full natural Hebrew sentence that makes sense.
    8. Return the final result as a single fluent Hebrew sentence only — no English, no explanations, and no punctuation at the end.

    Be strict: only include reliable words that follow the above rules and are supported by the evidence. The final output must sound like a natural Hebrew sentence based on the detected signs.
    """

    return prompt

def call_gpt(prompt, client, deployment):
    chat_prompt = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    completion = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )

    result = completion.choices[0].message.content
    return [word.strip() for word in result.split("\n") if word.strip()]

def consolidate_answers(answers, client, deployment):
    joined_answers = "\n".join(f"Answer {i+1}: {', '.join(ans)}" for i, ans in enumerate(answers))

    final_prompt = f"""
    You are given 5 different GPT responses that each analyzed a sign language video. Your task is to consolidate them into a single final list of signed words.
    
    Here are the answers:
    {joined_answers}
    
    Return only one final list of the most likely signed words, in correct order. Be strict and consistent. No explanations, no punctuation. One word per line.
    """

    return call_gpt(final_prompt, client, deployment)

def summarize_predictions_gpt(predictions, video_duration):

    endpoint = os.getenv("ENDPOINT_URL", "https://isl-translation.openai.azure.com/")
    deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY", AZURE_OPENAI_API_KEY)

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2024-05-01-preview",
    )

    # Generate the base prompt
    prompt = generate_prompt(predictions, video_duration)

    print("Sending 5 GPT requests to get individual predictions...")
    answers = [call_gpt(prompt, client, deployment) for _ in range(5)]

    for i, answer in enumerate(answers, 1):
        print(f"Answer {i}: {answer}")

    print("\nConsolidating the 5 answers into a final result...")
    final_answer = consolidate_answers(answers, client, deployment)

    print("\nFinal consolidated answer:")
    print(final_answer)

    return final_answer

def translate_video_to_text(video_path, model_path, label_encoder_path):
    predictions, video_duration = process_segments_with_threads(video_path, model_path, label_encoder_path)

    translation_text = summarize_predictions_gpt(predictions, video_duration)

    return translation_text