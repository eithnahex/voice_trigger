from app.tts import TTS, Device, SimplePollingReader, Speaker, TTSConfig, TTSManager
from app.vb_cable_writer import VBCableWriter

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
