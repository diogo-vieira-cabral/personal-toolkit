
import os
import shutil
import time     # add time 

download_folder = os.path.expanduser("~/Downloads")
folders = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
    "Videos": [".mp4", ".mkv", ".flv", ".avi", ".mov", ".wmv"],
    "Music": [".mp3", ".wav", ".acc", ".flac", ".ogg", ".m4a"],
    "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".csv", ".pptx"]
}

# 1 week in seconds: 7 days * 24 hours * 60 mins * 60 secs
SECONDS_IN_WEEK = 7 * 24 * 60 * 60
current_time = time.time()

# Create folders if they don't exist
for folder_name in list(folders.keys()) + ["Others"]:
    path = os.path.join(download_folder, folder_name)
    if not os.path.exists(path):
        os.makedirs(path)

for filename in os.listdir(download_folder):
    file_path = os.path.join(download_folder, filename)

    # Skip directories and the script itself
    if os.path.isdir(file_path):
        continue

    # TIME CONDITION: Only proceed if file is older than 1 week
    file_age = os.path.getmtime(file_path)
    if (current_time - file_age) < SECONDS_IN_WEEK:
        continue 

    # Determine category
    file_extension = os.path.splitext(filename)[1].lower()
    dest_folder = "Others"
    
    for category, extensions in folders.items():
        if file_extension in extensions:
            dest_folder = category
            break
    
    # Move the file
    shutil.move(file_path, os.path.join(download_folder, dest_folder, filename))

print("Old files organized successfully.")


