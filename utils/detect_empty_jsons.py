import os

# Folder path
motion_data_folder = r"C:\Users\yaelm\Documents\4th_year_project\sign_language_translation\resources\motion_data"
log_file_path = os.path.join(motion_data_folder, "defective_json_log.txt")

# Create or overwrite the log file
with open(log_file_path, "w") as log_file:
    log_file.write("")

# Counter for empty files
empty_file_count = 0

# Loop through all files in the folder
for file_name in os.listdir(motion_data_folder):
    if file_name.endswith(".json"):
        file_path = os.path.join(motion_data_folder, file_name)

        # Check file size
        if os.path.getsize(file_path) < 3 * 1024:  # less than 3KB
            try:
                os.remove(file_path)  # delete file
                with open(log_file_path, "a") as log_file:
                    log_file.write(file_name + "\n")
                print(f"Deleted and logged: {file_name}")
                empty_file_count += 1
            except Exception as e:
                print(f"Error deleting {file_name}: {e}")

# Final count print
print(f"\nTotal empty JSON files deleted: {empty_file_count}")
