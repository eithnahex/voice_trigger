from argparse import Namespace
from typing import Type
from app.io.command_polling_reader import PollingCommandReader
from app.io.io import Reader, Writer
from app.io.simple import SimplePollingReader, SimpleWavWriter
from app.io.vb_cable_writer import VBCableWriter
from app.manager import TTSManager
from app.tts import TTS, TTSConfig


def _match_io(io_str: str) -> Type[Reader] | Type[Writer]:
    match io_str:
        case 'SimplePollingReader':
            return SimplePollingReader
        case 'PollingCommandReader':
            return PollingCommandReader
        case 'SimpleWavWriter':
            return SimpleWavWriter
        case 'VBCableWriter':
            return VBCableWriter
        case _:
            raise Exception(f"Unknown IO {io_str}")


def boot(tts_config: TTSConfig, args: Namespace) -> None:
    tts = TTS(tts_config)

    ttsm = TTSManager(
        tts,
        _match_io(args.reader)(),  # type: ignore
        _match_io(args.writer)(),  # type: ignore
    )
    ttsm.start()
