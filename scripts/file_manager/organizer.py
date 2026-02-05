import os      # Function library for system paths
import shutil  # Function library for moving files
import time    # Function library for handling time

# --- CONFIGURATION ---
SIMULATION_MODE = True  # Change to False to execute real moves
# VARIABLE: The path to your downloads. expanduser handles the Mac/Windows difference.
download_folder = os.path.expanduser("~/Downloads")
# VARIABLE: Constant for 7 days in seconds.
SECONDS_IN_WEEK = 604800 
# VARIABLE: Stores the exact time you ran the script.
current_time = time.time()

# VARIABLE: Dictionary mapping folder names to lists of extensions.
file_types = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
    "Videos": [".mp4", ".mkv", ".flv", ".avi", ".mov", ".wmv"],
    "Music": [".mp3", ".wav", ".acc", ".flac", ".ogg", ".m4a"],
    "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".csv", ".pptx"]
}

print(f"--- ORGANIZER STARTING (Simulation: {SIMULATION_MODE}) ---")

# LOOP: 'filename' is a variable that changes for every file found in the folder.
for filename in os.listdir(download_folder):
    # VARIABLE: The full system path created by the join FUNCTION.
    file_path = os.path.join(download_folder, filename)

    # FUNCTION: Checks if the path is a folder. If true, 'continue' skips to the next file.
    if os.path.isdir(file_path):
        continue

    # VARIABLE: Stores the file's 'last modified' time.
    file_age = os.path.getmtime(file_path)
    if (current_time - file_age) < SECONDS_IN_WEEK:
        continue 

    # VARIABLE: Splits name from extension. [1] grabs the second part (the extension).
    file_extension = os.path.splitext(filename)[1].lower()
    dest_folder = "Others"

    # Screenshot "detour"
    # Logic: Convert to lowercase to check keywords and verify it's an image.
    if ("screenshot" in filename.lower() or "captura" in filename.lower()) and file_extension in file_types["Images"]:
        dest_folder = "Screenshots"
    else:
        # LOOP: Checking the dictionary. 'category' (Key) and 'extensions' (Value).
        for category, extensions in file_types.items():
            # LOGIC: If the file extension exists inside the list of extensions.
            if file_extension in extensions:
                dest_folder = category
                break
    
    # VARIABLE: Creating the final path for the destination folder.
    final_dest_path = os.path.join(download_folder, dest_folder)

    # ACTION PHASE
    if SIMULATION_MODE:
        print(f"READY TO MOVE: {filename} -> {dest_folder}")
    else:
        # LOGIC: If the folder doesn't exist, create it using the makedirs FUNCTION.
        if not os.path.exists(final_dest_path):
            os.makedirs(final_dest_path) 
        
        # FUNCTION: Moves the file from old path to new path.
        shutil.move(file_path, os.path.join(final_dest_path, filename))
        print(f"MOVED: {filename} -> {dest_folder}")

print("--- TASK FINISHED ---")