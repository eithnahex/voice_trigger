from __future__ import annotations
from multiprocessing import Queue
import time

from typing import Any, Generator, Optional
from PySide6 import QtCore, QtWidgets, QtGui, QtMultimedia
import sys

import PySide6
from PySide6.QtWidgets import *
from torch import Tensor
from app.io.vb_cable_writer import VBCableWriter

from app.tts import SampleRate, Speaker
from app.io.io import Reader, Writer


class PysideReader(Reader):
    def __init__(self, q_input: Queue[str]) -> None:
        self.q_input = q_input
        self.default_speaker = Speaker.baya
        self.stop = False

    def configure(self) -> None:
        pass

    def close(self) -> None:
        self.stop = True

    def read(self) -> Generator[tuple[str, Speaker | None], None, None]:
        while True:
            if self.stop:
                break
            data = self.q_input.get()
            sample = f"<speak>{data}</speak>"
            yield (sample, self.default_speaker)


class PysideWriter(VBCableWriter):
    pass
    # def configure(self, sample_rate: SampleRate) -> None:
    #     pass

    # def close(self) -> None:
    #     pass

    # def write(self, audio: Tensor) -> Any:
    #     pass


class PlayMenuButtons(QtWidgets.QWidget):
    # play in vb cable and headphones button
    # play button
    # pause button
    # stop button

    # test in headphones button
    # play button
    # pause button
    # stop button

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.layout = QtWidgets.QHBoxLayout(self)

        self.dual_play_btn = QtWidgets.QPushButton(
            text="Dual Play",
            parent=self
        )
        self.test_play_btn = QtWidgets.QPushButton(
            text="Test Play",
            parent=self
        )

        # self.dual_play_btn.clicked.connect(self.dual_play_clicked)
        # self.test_play_btn.clicked.connect(self.test_play_clicked)

        self.layout.addWidget(self.dual_play_btn)
        self.layout.addWidget(self.test_play_btn)

    # def dual_play_clicked(self):
    #     print('dual_play_clicked', self)

    # def test_play_clicked(self):
    #     print('test_play_clicked', self)


class MacrosListView(QtWidgets.QWidget):
    # list with tts text labels
    # play menu buttons

    def __init__(self, data: MacrosDataManager, parent) -> None:
        super().__init__(parent)

        self.data = data

        self.layout = QtWidgets.QVBoxLayout(self)

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setLayoutDirection(
            PySide6.QtCore.Qt.LayoutDirection.RightToLeft)

        self.scroll_widget = QtWidgets.QWidget(self)
        self.scroll_widget_layout = QtWidgets.QVBoxLayout(self)
        self.scroll_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_widget.setLayout(self.scroll_widget_layout)

        self.data.set_scroll_layout(self.scroll_widget_layout)

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setVerticalScrollBarPolicy(
            PySide6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(
            PySide6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.layout.addWidget(self.scroll_area)


class TTSTextPane(QtWidgets.QWidget):
    # text edit
    # add macros button
    # play menu buttons

    def __init__(self, data: MacrosDataManager, q_output: Queue[str], parent) -> None:
        super().__init__(parent)
        self.data = data
        self.q_output = q_output

        self.layout = QtWidgets.QVBoxLayout(self)
        self.buttons_layout = QtWidgets.QHBoxLayout(self)

        self.text_edit = QtWidgets.QPlainTextEdit(self)
        self.play_menu = PlayMenuButtons(self)
        self.add_macros_btn = QtWidgets.QPushButton(
            text="Add Macros",
            parent=self
        )

        self.buttons_layout.addWidget(self.add_macros_btn)
        self.buttons_layout.addWidget(self.play_menu)

        self.layout.addWidget(self.text_edit)
        self.layout.addLayout(self.buttons_layout)

        self.add_macros_btn.clicked.connect(self.add_macros_click)
        self.play_menu.dual_play_btn.clicked.connect(self.play_dual_clicked)

        pass

    def add_macros_click(self):
        print('add_macros_btn clicked')
        sample = self.text_edit.toPlainText().strip()
        if sample:
            self.data.add_item(sample)
        pass

    def play_dual_clicked(self):
        print('play_dual_clicked')
        smaple = self.text_edit.toPlainText().strip()
        self.q_output.put(smaple)
        pass


class MacrosWidget(QtWidgets.QWidget):

    def __init__(self, manager: MacrosDataManager, text: str = '', parent=None) -> None:
        super().__init__(parent)
        self.manager = manager

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setText(text)

        self.remove_btn = QtWidgets.QPushButton(text='Remove', parent=self)
        self.remove_btn.clicked.connect(self.remove_clicked)

        self.play_menu = PlayMenuButtons(self)

        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.remove_btn)
        self.layout.addWidget(self.play_menu)

    def set_text(self, text: str):
        self.line_edit.setText(text)

    def remove_clicked(self):
        print('remove btn clicked')
        self.manager.remove_item(self)


class MacrosDataManager:

    def __init__(self, q_reader: Queue[str], elements: list[QtWidgets.QWidget] = None) -> None:
        self.q_reader = q_reader
        self.scroll_layout = None
        self.elements = elements or []
        pass

    def set_scroll_layout(self, l: QtWidgets.QBoxLayout):
        self.scroll_layout = l
        for w in self.elements:
            self.scroll_layout.addWidget(w)

    def get_all(self) -> list[QtWidgets.QWidget]:
        return self.elements

    def add_item(self, text: str = ''):
        w = self._create_item(text)
        self._add_widget(w)

    def _add_widget(self, w: QtWidgets.QWidget):
        self.elements.append(w)
        if self.scroll_layout:
            self.scroll_layout.addWidget(w)
        else:
            pass
            # raise Exception(
            #     'The scroll_layout is null. Set one by set_scroll_layout'
            # )

    def remove_item(self, w: QtWidgets.QWidget):
        if self.scroll_layout:
            self.scroll_layout.removeWidget(w)
            self.elements.remove(w)
            w.setParent(None)
            w.deleteLater()
            del w
        else:
            raise Exception(
                'The scroll_layout is null. Set one by set_scroll_layout'
            )

    def remove_item_by_index(self, index: int):
        if self.scroll_layout:
            w = self.elements[index]
            self.scroll_layout.removeWidget(w)
            self.elements.remove(w)
            w.setParent(None)
            w.deleteLater()
            del w
        else:
            raise Exception(
                'The scroll_layout is null. Set one by set_scroll_layout'
            )

    def _create_item(self, text: str = '') -> QtWidgets.QWidget:
        w = MacrosWidget(self, text)
        w.play_menu.dual_play_btn.clicked.connect(
            lambda: self.play_dual_clicked(w.line_edit.text()))
        return w

    def play_dual_clicked(self, text: str):
        print('play_dual_clicked')
        smaple = text.strip()
        self.q_reader.put(smaple)
        pass


class TTSUI(QtWidgets.QWidget):

    def __init__(self, q_reader: Queue[str]) -> None:
        super().__init__()

        macros_manager = MacrosDataManager(q_reader)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.output_layout = QtWidgets.QHBoxLayout(self)

        self.macros_list_view = MacrosListView(macros_manager, parent=self)
        self.left_pane = TTSTextPane(macros_manager, q_reader, self)
        self.right_pane = TTSTextPane(macros_manager, q_reader, self)

        self.output_layout.addWidget(
            self.left_pane
        )
        self.output_layout.addWidget(
            self.right_pane
        )

        self.layout.addWidget(
            self.macros_list_view
        )
        self.layout.addLayout(self.output_layout)

    pass


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    q_reader: Queue[str] = Queue()

    widget = TTSUI(q_reader)
    widget.resize(800, 600)
    widget.setWindowTitle('TTS UI')
    widget.show()

    sys.exit(app.exec())
