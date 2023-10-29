import random
import matplotlib.pyplot as plt
import matplotlib
import os
import sys
from collections import namedtuple
from itertools import repeat

from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QHeaderView, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5 import QtCore, Qt, QtWidgets

import main_window as main_window_form

"""
pip install pyinstaller
pyinstaller --onefile --icon=icon.ico --noconsole --name "Sensors" --clean main.py
--onedir или --onefile (в одну папку или в один файл)
pyrcc5 -o resources.py resources.qrc
"""

SETTINGS = QtCore.QSettings("settings.ini", QtCore.QSettings.IniFormat)
BUILDING = False  # Флаг, отвечающий за отладочные функции
DIRNAME, _ = os.path.split(os.path.realpath(__file__))  # Путь к папке с исполняемым файлом
matplotlib.use("agg")


def update_interface():
    ui_names = (item[:-3] for item in os.listdir(rf"{DIRNAME}\ui") if item[-2:] == "ui")

    for name in ui_names:
        ui_path = rf"{DIRNAME}\ui\{name}.ui"  # Формирование пути к файлу .ui
        py_path = rf"{DIRNAME}\{name}.py"  # Формирование пути к файлу .py
        if f"{name}.py" not in os.listdir(DIRNAME):  # Если файла .py нет, то он будет создан
            os.system(f"pyuic5 {ui_path} -o {py_path} -x")
        elif os.path.getmtime(ui_path) > os.path.getmtime(py_path):  # Если он устаревший, то он будет перезаписан
            os.system(f"pyuic5 {ui_path} -o {py_path} -x")
if BUILDING: update_interface()  # Запуск функции, если включён отладочный флаг!!!


def button_style(name_button: str):
    return f"""
    QPushButton#{name_button} {{
        text-align: center;
    }}
    QPushButton#{name_button} {{
        background-color: #e7e7e7;
        border-style: none;
        border-radius: 10px;
    }}
    QPushButton#{name_button}:hover {{
        background-color: #ffc4c5;
    }}
    QPushButton#{name_button}:pressed {{
        background-color: #ffc4c5;
        margin: 2px;
    }}"""


def palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#F1F1F2"))
    palette.setColor(QPalette.Button, QColor("#ECF2F9"))
    palette.setColor(QPalette.Base, QColor("#F1F1F2"))
    palette.setColor(QPalette.Highlight, QColor("#ffd863"))
    palette.setColor(QPalette.HighlightedText, QColor("black"))
    return palette