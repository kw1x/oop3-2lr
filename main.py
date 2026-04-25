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
    DEFAULT_FILE = "model_data.json"

    def __init__(self, file_path: Optional[str] = None) -> None:
        super().__init__()
        self.__file_path = file_path or self.DEFAULT_FILE
        self.__a = self.MIN_VALUE
        self.__b = self.MIN_VALUE
        self.__c = self.MAX_VALUE
        self.__update_count = 0
        self.__load_silent()
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

    def set_all(self, a: int, b: int, c: int) -> None:
        a = self.__clamp(a, self.MIN_VALUE, self.MAX_VALUE)
        c = self.__clamp(c, self.MIN_VALUE, self.MAX_VALUE)
        if a > c:
            a, c = c, a
        b = self.__clamp(b, a, c)
        self.__commit(a, b, c)

    def __commit(self, a: int, b: int, c: int) -> None:
        if (a, b, c) == (self.__a, self.__b, self.__c):
            return
        self.__a = a
        self.__b = b
        self.__c = c
        self.__notify()

    def save(self) -> None:
        try:
            data = {"a": self.__a, "c": self.__c}
            with open(self.__file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            print(f"NumberModel: ошибка сохранения: {exc}")

    def __load_silent(self) -> None:
        if not os.path.exists(self.__file_path):
            return
        try:
            with open(self.__file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"NumberModel: ошибка загрузки: {exc}")
            return

        a = self.__clamp(data.get("a", self.MIN_VALUE),
                         self.MIN_VALUE, self.MAX_VALUE)
        c = self.__clamp(data.get("c", self.MAX_VALUE),
                         self.MIN_VALUE, self.MAX_VALUE)
        if a > c:
            a, c = c, a
        b = a
        self.__a, self.__b, self.__c = a, b, c


class NumberWidget(QWidget):
    """Три синхронизированных контрола для одного числа."""

    request_value = pyqtSignal(int)

    def __init__(self, title: str, min_val: int, max_val: int,
                 initial: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.__min = min_val
        self.__max = max_val
        self.__current = initial
        self.__updating = False

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        title_label = QLabel(title, self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = title_label.font()
        f.setBold(True)
        title_label.setFont(f)
        layout.addWidget(title_label)

        self.__edit = QLineEdit(str(initial), self)
        self.__edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__edit.setValidator(QIntValidator(min_val, max_val, self))
        self.__edit.editingFinished.connect(self.__on_edit_finished)
        layout.addWidget(self.__edit)

        self.__spin = QSpinBox(self)
        self.__spin.setRange(min_val, max_val)
        self.__spin.setValue(initial)
        self.__spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__spin.valueChanged.connect(self.__on_spin_changed)
        layout.addWidget(self.__spin)

        self.__slider = QSlider(Qt.Orientation.Horizontal, self)
        self.__slider.setRange(min_val, max_val)
        self.__slider.setValue(initial)
        self.__slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.__slider.setTickInterval(10)
        self.__slider.valueChanged.connect(self.__on_slider_changed)
        layout.addWidget(self.__slider)

    def set_display_value(self, value: int) -> None:
        self.__current = value
        self.__updating = True
        try:
            if self.__edit.text() != str(value):
                self.__edit.setText(str(value))
            if self.__spin.value() != value:
                self.__spin.setValue(value)
            if self.__slider.value() != value:
                self.__slider.setValue(value)
        finally:
            self.__updating = False

    def __on_edit_finished(self) -> None:
        if self.__updating:
            return
        text = self.__edit.text().strip()
        if not text or text in ("-", "+"):
            self.set_display_value(self.__current)
            return
        try:
            value = int(text)
        except ValueError:
            self.set_display_value(self.__current)
            return
        value = max(self.__min, min(self.__max, value))
        self.request_value.emit(value)

    def __on_spin_changed(self, value: int) -> None:
        if self.__updating:
            return
        self.request_value.emit(int(value))

    def __on_slider_changed(self, value: int) -> None:
        if self.__updating:
            return
        self.request_value.emit(int(value))

    def focusOutEvent(self, event) -> None:
        super().focusOutEvent(event)
        if self.__edit.text().strip() in ("", "-", "+"):
            self.set_display_value(self.__current)
