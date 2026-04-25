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


class NumberModel(QObject):
    """Хранит три целых числа A, B, C с инвариантом A ≤ B ≤ C."""

    changed = pyqtSignal()

    MIN_VALUE = 0
    MAX_VALUE = 100

    def __init__(self) -> None:
        super().__init__()
        self.__a = self.MIN_VALUE
        self.__b = self.MIN_VALUE
        self.__c = self.MAX_VALUE
        self.__update_count = 0
        self.__notify()

    def get_min(self) -> int:
        return self.MIN_VALUE

    def get_max(self) -> int:
        return self.MAX_VALUE

    def get_update_count(self) -> int:
        return self.__update_count

    def get_a(self) -> int:
        return self.__a

    def get_b(self) -> int:
        return self.__b

    def get_c(self) -> int:
        return self.__c

    def __notify(self) -> None:
        self.__update_count += 1
        self.changed.emit()

    @staticmethod
    def __clamp(v: int, lo: int, hi: int) -> int:
        return max(lo, min(hi, int(v)))

    def set_a(self, value: int) -> None:
        new_a = self.__clamp(value, self.MIN_VALUE, self.MAX_VALUE)
        new_b, new_c = self.__b, self.__c
        if new_a > new_c:
            new_c = new_a
        if new_a > new_b:
            new_b = new_a
        self.__commit(new_a, new_b, new_c)

    def set_c(self, value: int) -> None:
        new_c = self.__clamp(value, self.MIN_VALUE, self.MAX_VALUE)
        new_a, new_b = self.__a, self.__b
        if new_c < new_a:
            new_a = new_c
        if new_c < new_b:
            new_b = new_c
        self.__commit(new_a, new_b, new_c)

    def set_b(self, value: int) -> None:
        new_b = self.__clamp(value, self.__a, self.__c)
        self.__commit(self.__a, new_b, self.__c)

    def __commit(self, a: int, b: int, c: int) -> None:
        if (a, b, c) == (self.__a, self.__b, self.__c):
            return
        self.__a = a
        self.__b = b
        self.__c = c
        self.__notify()
