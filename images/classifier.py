import os
import shutil
import numpy as np

from PIL import Image
from pathlib import Path
from tkinter.filedialog import askdirectory
from tkinter import Tk


def test_color_distribution(file):
    img = Image.open(file)
    img.thumbnail((200, 200), Image.ANTIALIAS)
    w, h = img.size
    return sum(
        x[0]
        for x in sorted(
            img.convert("RGB").getcolors(w * h), key=lambda x: x[0], reverse=True
        )[:10]
    ) / float((w * h))


def test_sharp_edge_detection(file):
    img = Image.open(file).convert("L")
    values = abs(np.fft.fft2(np.asarray(img.convert("L")))).flatten().tolist()
    high_values = [x for x in values if x > 10000]
    high_values_ratio = 100 * (float(len(high_values)) / len(values))
    return high_values_ratio


def test_file(file):
    image = 0
    real = 0
    color = test_color_distribution(file)
    edges = test_sharp_edge_detection(file)

    if color > 0.28:
        image += (color - 0.28) * 10
    else:
        real += (0.28 - color) * 10

    if edges > 13:
        image += edges - 13
    else:
        real += 13 - edges
    return image > real


Tk().withdraw()

# Dialog box for selecting a folder.
file_path = askdirectory(title="Select a folder")

list_of_files = os.walk(file_path)


if not os.path.exists(os.path.join(file_path, "sorted")):
   os.makedirs(os.path.join(file_path, "sorted"))

if not os.path.exists(os.path.join(file_path, "sorted/image_real")):
   os.makedirs(os.path.join(file_path, 'sorted/image_real'))

real = os.path.join(file_path, 'sorted/image_real')

if not os.path.exists(os.path.join(file_path, "sorted/drawn")):
   os.makedirs(os.path.join(file_path, 'sorted/drawn'))

drawn = os.path.join(file_path, 'sorted/drawn')


for root, folders, files in list_of_files:
    for file in files:
        file_path = Path(os.path.join(root, file))
        is_drawn = test_file(file_path)
        if is_drawn:
            shutil.move(file_path, os.path.join(drawn, str(file_path).split("/")[-1]))
        else:
            shutil.move(file_path, os.path.join(real, str(file_path).split("/")[-1]))

