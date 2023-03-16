#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Elevator simulator
"""
import os
import random

from time import sleep


class Passenger(object):
    __slots__ = ["frm", "to", "time", "on_elevator"]

    def __init__(self, frm, to):
        self.frm = frm
        self.to = to
        self.time = 0
        self.on_elevator = False


def clear():
    os.system("clear")


def add_random():
    to = random.randint(1, 100)
    if to < 90:
        return
    flr = random.randint(1, MAX_FLOORS)
    flr2 = random.randint(1, MAX_FLOORS)
    while flr2 == flr:
        flr2 = random.randint(1, MAX_FLOORS)
    next_command.append(flr)
    next_command.append(flr2)


def print_elevator():
    msx = len(str(MAX_FLOORS))
    r = ""
    mx_n = 0
    for i in range(MAX_FLOORS, 0, -1):
        s = f"{i}{' ' * (msx - len(str(i)))}|"
        if i == current_floor:
            s += "e"
        else:
            s += " "
        s += "|"
        if i in next_command:
            n = next_command.count(i)
            if n + 1 > mx_n:
                mx_n = n + 1
            s += " " + "i" * n
        s += "\n"
        r += s
    r += "_" * len(next_command)
    clear()
    print(r)


# config
MOVE_SPEED = 2
TURN_TIME = 2
MAX_FLOORS = 30

next_command = [10, 6, 8, 30, 1]
passengers = []
current_floor = 1
stop = True

while True:
    next_command = sorted(next_command, key=lambda x: abs(current_floor - x))
    status = f"idling on floor {current_floor}"
    if next_command:
        if not stop:
            if MOVE_SPEED >= abs(current_floor - next_command[0]):
                stop = True
                current_floor = next_command[0]
                del next_command[0]
                status = f"arrived to floor {current_floor}"
            else:
                if current_floor > next_command[0]:
                    current_floor -= MOVE_SPEED
                else:
                    current_floor += MOVE_SPEED
                status = f"moving to floor {next_command[0]}, current floor - {current_floor}"
        else:
            stop = False
            status = f"stated moving to floor {next_command[0]}, current floor - {current_floor}"
    print(status)
    print_elevator()
    add_random()
    sleep(TURN_TIME)
