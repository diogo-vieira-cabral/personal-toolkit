import os
import shutil
import time
import argparse
import yaml

# -----------------------------
# Parse command-line arguments
# -----------------------------
parser = argparse.ArgumentParser(description="Organize your Downloads folder")
parser.add_argument("--dry-run", action="store_true", help="Simulate file moves without changing anything")
args = parser.parse_args()

SIMULATION_MODE = args.dry_run
print("SIMULATION_MODE =", SIMULATION_MODE)

# -----------------------------
# Load YAML config
# -----------------------------
def load_file_rules(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

file_types = load_file_rules("config/file_rules.yaml")
print("Loaded rules:", file_types)

# -----------------------------
# Rest of your organizer code
# -----------------------------


# VARIABLE: The path to your downloads. expanduser handles the Mac/Windows difference.
download_folder = os.path.expanduser("~/Downloads")
SECONDS_IN_WEEK = 604800 
current_time = time.time() # VARIABLE: Stores the exact time you ran the script.



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

    dest_folder = "_Others"

    # Screenshot "detour"
    # Logic: Convert to lowercase to check keywords and verify it's an image.
    if ("screenshot" in filename.lower() or "captura" in filename.lower()) and file_extension in file_types["_Images"]:
        dest_folder = "_Screenshots"
    else:
        for category, extensions in file_types.items():
            if file_extension in extensions:
                dest_folder = category
                break
    print(f"{filename} -> ext: {file_extension} -> category: {dest_folder}")


    
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