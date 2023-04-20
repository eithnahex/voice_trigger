import sys
from app.manager import TTSManager
from app.tts import TTS, TTSConfig
from app.ui.pyside_ui import TTSUI, PysideReader, PysideWriter
from PySide6 import QtWidgets
from multiprocessing import Process, Queue


def _run_tts(q_reader, tts_config: TTSConfig) -> None:  # type: ignore
    tts = TTS(tts_config)

    r = PysideReader(q_reader)
    w = PysideWriter()

    ttsm = TTSManager(
        tts,
        r,  # type: ignore
        w,  # type: ignore
    )
    ttsm.start()


def _run_pyside(q_reader) -> None:   # type: ignore
    app = QtWidgets.QApplication([])

    widget = TTSUI(
        q_reader=q_reader,
    )
    widget.resize(800, 600)
    widget.setWindowTitle('Voice Trigger')
    widget.show()

    sys.exit(app.exec())


def boot(tts_config: TTSConfig) -> None:
    q_reader: Queue[str] = Queue()

    p1 = Process(target=_run_pyside, args=(q_reader,), daemon=True)
    p1.start()

    p2 = Process(target=_run_tts, args=(q_reader, tts_config), daemon=False)
    p2.start()

    p1.join()
    p2.terminate()
