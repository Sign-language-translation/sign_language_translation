import os
import shutil

hebrew_to_english = {
    "אתה": "you",
    "אני": "I",
    "בית": "house",
    "ברוך הבא": "welcome",
    "יום שבת": "Saturday",
    "למה": "why",
    "לבוא": "to_come",
    "ללכת": "to_walk",
    "לא": "no",
    "מתי": "when",
    "מנוחה": "rest",
    "רעב": "hungry",
    "רחוק": "far",
    "עצבני": "angry",
}

def rename_and_copy_videos(source_folder, target_folder, name_mapping):
    os.makedirs(target_folder, exist_ok=True)

    for word_folder in os.listdir(source_folder):
        word_path = os.path.join(source_folder, word_folder)

        if os.path.isdir(word_path):
            english_name = name_mapping.get(word_folder, word_folder.replace(" ", ""))
            count = 1

            for file_name in os.listdir(word_path):
                if file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    extension = os.path.splitext(file_name)[1]
                    new_file_name = f"{english_name}_{count}{extension}"

                    src = os.path.join(word_path, file_name)
                    dst = os.path.join(target_folder, new_file_name)

                    shutil.copy2(src, dst)

                    print(f"Copied: {src} → {dst}")
                    count += 1

# Example usage
if __name__ == "__main__":
    source = r"C:\Users\yaelm\Downloads\סרטוני מילים"
    target = r"C:\Users\yaelm\Documents\4th_year_project\sign_language_translation\test_vid\new_words_20_04"
    rename_and_copy_videos(source, target, hebrew_to_english)
