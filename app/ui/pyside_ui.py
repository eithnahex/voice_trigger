from __future__ import annotations
from dataclasses import dataclass
from multiprocessing import Queue
import time

from typing import Any, Callable, Generator, Optional
from PySide6 import QtCore, QtWidgets, QtGui, QtMultimedia
import sys

import PySide6
from PySide6.QtWidgets import *
from torch import Tensor
from app.io.vb_cable_writer import VBCableWriter

from app.tts import SampleRate, Speaker
from app.io.io import Reader, Writer


@dataclass
class FormatText:
    value: str

    def format(self, *args: Any, **kwargs: Any) -> str:
        return self.value.format(*args, **kwargs)


class PysideReader(Reader):
    def __init__(self, q_input: Queue[str]) -> None:
        self.q_input = q_input
        self.default_speaker = Speaker.baya
        self.stop = False

    def configure(self) -> None:
        print('PysideReader ready')
        pass

    def close(self) -> None:
        self.stop = True
        print('PysideReader closed')

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

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.dual_play_btn = QtWidgets.QPushButton(
            text="Dual Play",
            parent=self
        )

        self.test_play_btn = QtWidgets.QPushButton(
            text="Test Play",
            parent=self
        )

        layout.addWidget(self.dual_play_btn)
        layout.addWidget(self.test_play_btn)

        self.setLayout(layout)

        pass


class TTSTextPane(QtWidgets.QWidget):
    # text edit
    # add macros button
    # play menu buttons

    def __init__(self, data: MacrosDataManager, q_output: OutputProxy, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.data = data
        self.q_output = q_output

        layout = QtWidgets.QVBoxLayout()
        self.buttons_layout = QtWidgets.QHBoxLayout()

        self.text_edit = QtWidgets.QPlainTextEdit(self)
        self.text_edit.installEventFilter(self)

        self.play_menu = PlayMenuButtons()
        self.add_macros_btn = QtWidgets.QPushButton(
            text="Add Macros",
            parent=self
        )

        self.buttons_layout.addWidget(self.add_macros_btn)
        self.buttons_layout.addWidget(self.play_menu)

        layout.addWidget(self.text_edit)
        layout.addLayout(self.buttons_layout)

        self.add_macros_btn.clicked.connect(self.add_macros_click)
        self.play_menu.dual_play_btn.clicked.connect(self.play_dual_clicked)

        self.setLayout(layout)
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

    def eventFilter(self, widget: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if widget == self.text_edit and event.type() == QtCore.QEvent.Type.KeyPress:
            keyEvent = QtGui.QKeyEvent(event)  # type: ignore
            if keyEvent.keyCombination() == QtCore.QKeyCombination(QtCore.Qt.KeyboardModifier.ControlModifier, QtCore.Qt.Key.Key_Return):
                self.play_dual_clicked()

        return False


class MacrosListView(QtWidgets.QWidget):
    # list with tts text labels
    # play menu buttons

    def __init__(self, data: MacrosDataManager, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.data = data

        layout = QtWidgets.QVBoxLayout()

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.setLayoutDirection(
        #     PySide6.QtCore.Qt.LayoutDirection.RightToLeft)

        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_widget_layout = QtWidgets.QVBoxLayout()
        self.scroll_widget_layout.setAlignment(PySide6.QtCore.Qt.AlignTop)

        self.scroll_widget.setLayout(self.scroll_widget_layout)

        self.data.set_scroll_layout(self.scroll_widget_layout)

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setVerticalScrollBarPolicy(
            PySide6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(
            PySide6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(self.scroll_area)

        self.setLayout(layout)


class MacrosWidget(QtWidgets.QWidget):

    def __init__(self, manager: MacrosDataManager, text: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.manager = manager

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setContentsMargins(6, 0, 6, 0)
        self.line_edit.setText(text)

        self.remove_btn = QtWidgets.QPushButton(text='Remove')
        self.remove_btn.setMaximumWidth(60)
        self.remove_btn.clicked.connect(self.remove_clicked)

        self.play_menu = PlayMenuButtons()

        layout.addWidget(self.remove_btn)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.play_menu)

        self.setLayout(layout)

    def set_text(self, text: str):
        self.line_edit.setText(text)

    def remove_clicked(self):
        print('remove btn clicked')
        self.manager.remove_item(self)


class MacrosDataManager:

    def __init__(self, q_reader: OutputProxy, elements: list[QtWidgets.QWidget] | None = None) -> None:
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

    def remove_item_by_index(self, index: int) -> None:
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

    def play_dual_clicked(self, text: str) -> None:
        print('play_dual_clicked')
        smaple = text.strip()
        self.q_reader.put(smaple)
        pass


class GlobalProsodyWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        default_globals = FormatText('<prosody rate="fast">{}</prosody>')

        self.__line_edit = QtWidgets.QLineEdit(self)
        self.__line_edit.setText(default_globals.value)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.__line_edit)
        self.setLayout(layout)

    def get_text(self) -> FormatText:
        return FormatText(self.__line_edit.text())

    def add_change_cb(self, slot: QtCore.Slot | Callable) -> None:
        self.__line_edit.textChanged.connect(slot)


class OutputProxy:
    def __init__(self, q_reader: Queue[str]) -> None:
        self.q_reader = q_reader
        self.__global_prosody_text: FormatText = FormatText('')

    def put(self, data: str, block: bool = True, timeout: float | None = None) -> None:
        print('proxy put')
        sample = self.__global_prosody_text.format(data)
        self.q_reader.put(sample, block, timeout)

    def slot_prosody_changed(self, text: str) -> None:
        self.__global_prosody_text = FormatText(text)

    def set_default_global_prosody(self, global_prosody: FormatText) -> None:
        self.__global_prosody_text = global_prosody


class TTSUI(QtWidgets.QWidget):

    def __init__(self, q_reader: Queue[str]) -> None:
        super().__init__()

        self.output_proxy = OutputProxy(q_reader)

        macros_manager = MacrosDataManager(self.output_proxy)

        self.global_prosody = GlobalProsodyWidget()
        self.global_prosody.add_change_cb(
            self.output_proxy.slot_prosody_changed
        )
        self.output_proxy.set_default_global_prosody(
            self.global_prosody.get_text())

        layout = QtWidgets.QVBoxLayout()

        self.output_layout = QtWidgets.QHBoxLayout()

        self.macros_list_view = MacrosListView(macros_manager)
        self.left_pane = TTSTextPane(
            macros_manager, self.output_proxy, parent=self)
        self.right_pane = TTSTextPane(
            macros_manager, self.output_proxy, parent=self)

        self.output_layout.addWidget(
            self.left_pane
        )
        self.output_layout.addWidget(
            self.right_pane
        )

        layout.addWidget(
            self.global_prosody
        )

        layout.addWidget(
            self.macros_list_view
        )
        layout.addLayout(self.output_layout)

        self.setLayout(layout)

    pass


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    q_reader: Queue[str] = Queue()

    widget = TTSUI(q_reader)
    widget.resize(800, 600)
    widget.setWindowTitle('TTS UI')
    widget.show()

    sys.exit(app.exec())
