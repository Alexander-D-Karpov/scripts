from tkinter.filedialog import askdirectory
from tkinter import Tk
import os
import hashlib
from pathlib import Path

Tk().withdraw()

# Dialog box for selecting a folder.
file_path = askdirectory(title="Select a folder")

# Listing out all the files
# inside our root folder.
list_of_files = os.walk(file_path)

# In order to detect the duplicate
# files we are going to define an empty dictionary.
unique_files = dict()

for root, folders, files in list_of_files:
    for file in files:
        file_path = Path(os.path.join(root, file))
        hash_file = hashlib.md5(open(file_path, 'rb').read()).hexdigest()

        if hash_file not in unique_files:
            unique_files[hash_file] = file_path
        else:
            os.remove(file_path)
            print(f"{file_path} has been deleted")
