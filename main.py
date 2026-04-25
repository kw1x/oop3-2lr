"""
Лабораторная работа №3, часть 2.
Тема: «MVC».

GUI-приложение на PyQt6, реализующее три синхронизированных
числа A, B, C с инвариантом A ≤ B ≤ C в стиле Model-View.
"""
import json
import os
import sys
from typing import Optional

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
