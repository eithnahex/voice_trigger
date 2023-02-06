from app.io.simple import SimplePollingReader
from app.io.vb_cable_writer import VBCableWriter
from app.manager import TTSManager
from app.tts import TTS, Device, Speaker, TTSConfig

"""
Pytorch install: pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
"""


def main():
    tts = TTS(TTSConfig(
        device=Device.GPU,
        default_speaker=Speaker.baya,
        models_path='./models/',
        download_model_if_not_exists=True,
    ))

    ttsm = TTSManager(tts, SimplePollingReader(), VBCableWriter())
    ttsm.start()


if __name__ == "__main__":
    main()
