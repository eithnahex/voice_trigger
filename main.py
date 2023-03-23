from typing import Type
from app.io.command_polling_reader import PollingCommandReader
from app.io.io import Reader, Writer
from app.io.simple import SimplePollingReader, SimpleWavWriter
from app.io.vb_cable_writer import VBCableWriter
from app.manager import TTSManager
from app.tts import TTS, Device, Speaker, TTSConfig
import argparse

"""
Pytorch install: pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
"""


parser = argparse.ArgumentParser()
parser.add_argument(
    '--reader',
    type=str,
    default='PollingCommandReader',
    choices=['PollingCommandReader', 'SimpleWavWriter']
)
parser.add_argument(
    '--writer',
    type=str,
    default='VBCableWriter',
    choices=['VBCableWriter', 'SimpleWavWriter']
)
parser.add_argument(
    '--models_dir',
    type=str,
    default='./models/',
)
parser.add_argument(
    '--model_name',
    type=str,
    default='v3_1_ru.pt',
)
parser.add_argument(
    '--device',
    type=str,
    default='cuda',
    choices=['cpu', 'cuda']
)


def match_io(io_str: str) -> Type[Reader] | Type[Writer]:
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


def main() -> None:
    args = parser.parse_args()
    [args.reader, args.writer]

    tts = TTS(TTSConfig(
        device=Device.from_string(args.device),
        default_speaker=Speaker.baya,
        models_path='./models/',
        download_model_if_not_exists=True,
    ))

    ttsm = TTSManager(
        tts,
        match_io(args.reader)(),  # type: ignore
        match_io(args.writer)(),  # type: ignore
    )
    ttsm.start()


if __name__ == "__main__":
    main()
