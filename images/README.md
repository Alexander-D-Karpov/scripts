# Image scripts
several scripts for sorting and managing images

Note: highly depended on python's tkinter and pillow
### Install
```shell
# Debian
$ sudo apt-get install python3-tk 
# Fedora
$ sudo dnf install python3-tkinter
# Arch
$ yay -S tk

$ pip install Pillow tk
```

## Clear
Find files with the same hash and deletes them

### Run
```shell
$ python3 clear.py
```

## Manage
Show images and moves them to folders on key press

### Run
```shell
$ python3 manage.py
```

## Classifier
Sort images into real/not real photos

### Run
```shell
$ python3 classifier.py
```
