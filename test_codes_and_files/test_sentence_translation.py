import time
from codes_translation.translate_sentence import translate_video_to_text

VIDEOS_FOLDER = "sentence_videos/"

def test_split_a_sentence():
    test_cases = [
        {
            "input_video": "I_hungry_angry_yanos.mp4",
            "expected_result": ['I', 'hungry', 'angry']
        }
        # {
        #     "input_video": "sentence_videos/bloodTest_lightBlue_moslem_ron.mp4",
        #     "expected_result": ['bloodTest', 'lightBlue', 'moslem']
        # },
        # {
        #     "input_video": "sentence_videos/moslem_ron.mp4",
        #     "expected_result": ['moslem']
        # }
    ]

    all_received_results = []

    for test_case in test_cases:
        videos_name = test_case["input_video"]
        expected_result = test_case["expected_result"]
        videos_full_path = VIDEOS_FOLDER + videos_name

        print(f"\n--- Running test for: {videos_name} ---")
        start_time = time.time()
        received_result = translate_video_to_text(videos_full_path)
        elapsed_time = time.time() - start_time

        all_received_results.append({
            "input_video": videos_name,
            "received_result": received_result,
            "expected_result": expected_result,
            "elapsed_time": elapsed_time
        })

    print("\n=== Test Summary ===")

    total_tests = len(all_received_results)
    for idx, result in enumerate(all_received_results, start=1):
        input_video = result["input_video"]
        received_result = result["received_result"]
        expected_result = result["expected_result"]
        elapsed_time = result["elapsed_time"]

        print(f"\nTest {idx}/{total_tests} — {input_video}")
        print(f"Time taken: {elapsed_time:.2f} seconds")

        # Unordered match: count how many expected words are in received_result
        expected_set = set(expected_result)
        received_set = set(received_result)
        correct = len(expected_set & received_set)
        total_expected = len(expected_result)
        success_rate = (correct / total_expected) * 100 if total_expected > 0 else 0

        if received_result == expected_result:
            print("✅ Test passed")
            print("Result:", " ".join(received_result))
        else:
            print("❌ Test failed")
            print("Expected:", expected_result)
            print("Received:", received_result)

        print(f"✔️ Success: {correct}/{total_expected} words correct ({success_rate:.1f}%)")

if __name__ == "__main__":
    test_split_a_sentence()