import os
import shutil
import tkinter
from time import sleep

from PIL import ImageTk, Image

# Dialog box for selecting a folder.
file_path = input("Path: ")
files = []
print("started loading files")
for dirpath, _, filenames in os.walk(file_path):
    for f in filenames:
        files.append(os.path.abspath(os.path.join(dirpath, f)))
files = sorted(files, key=os.path.getsize, reverse=True)
print("files loaded")


if not os.path.exists(os.path.join(file_path, "sorted")):
    os.makedirs(os.path.join(file_path, "sorted"))

if not os.path.exists(os.path.join(file_path, "sorted/drawn")):
    os.makedirs(os.path.join(file_path, "sorted/drawn"))

drawn = os.path.join(file_path, "sorted/drawn")

if not os.path.exists(os.path.join(file_path, "sorted/real")):
    os.makedirs(os.path.join(file_path, "sorted/real"))

real = os.path.join(file_path, "sorted/real")

if not os.path.exists(os.path.join(file_path, "sorted/comic")):
    os.makedirs(os.path.join(file_path, "sorted/comic"))

comic = os.path.join(file_path, "sorted/comic")

if not os.path.exists(os.path.join(file_path, "sorted/other")):
    os.makedirs(os.path.join(file_path, "sorted/other"))

other = os.path.join(file_path, "sorted/other")

if not os.path.exists(os.path.join(file_path, "sorted/delete")):
    os.makedirs(os.path.join(file_path, "sorted/delete"))

delete = os.path.join(file_path, "sorted/delete")


class Window:
    def __init__(self, master, files):
        self.img = None
        self.label = None

        self.files = files
        self.cur = 0
        self.master = master

        init_file = self.files[0]
        self.show_file(init_file)

    def show_file(self, f):
        self.img = Image.open(f)
        x = self.img.height / 1080
        self.img = self.img.resize((int(self.img.width / x), 1080), Image.LANCZOS)

        self.img = ImageTk.PhotoImage(self.img)

        self.label = tkinter.Label(self.master, image=self.img)
        self.label.pack_propagate(0)
        self.label.pack(side=tkinter.TOP, expand=True, fill=tkinter.X)

    def next(self, event):
        self.cur += 1
        self.show_file(self.files[self.cur])
        sleep(0.1)

    def real(self, event):
        self.label.destroy()
        shutil.move(
            self.files[self.cur],
            os.path.join(real, str(self.files[self.cur]).split("/")[-1]),
        )
        self.next(event)

    def drawn(self, event):
        self.label.destroy()
        shutil.move(
            self.files[self.cur],
            os.path.join(drawn, str(self.files[self.cur]).split("/")[-1]),
        )
        self.next(event)

    def comic(self, event):
        self.label.destroy()
        shutil.move(
            self.files[self.cur],
            os.path.join(comic, str(self.files[self.cur]).split("/")[-1]),
        )
        self.next(event)

    def other(self, event):
        self.label.destroy()
        shutil.move(
            self.files[self.cur],
            os.path.join(other, str(self.files[self.cur]).split("/")[-1]),
        )
        self.next(event)

    def delete(self, event):
        self.label.destroy()
        shutil.move(
            self.files[self.cur],
            os.path.join(delete, str(self.files[self.cur]).split("/")[-1]),
        )
        self.next(event)


root = tkinter.Tk()
root.title("1 - real; 2 - drawn; 3 - comic; 4 - other; 5 - delete")
window = Window(root, files)
root.bind("<Return>", window.next)
root.bind("1", window.real)
root.bind("2", window.drawn)
root.bind("3", window.comic)
root.bind("4", window.other)
root.bind("5", window.delete)
root.mainloop()

root.mainloop()
