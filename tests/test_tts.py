from app.tts import TTS, Device, SimplePollingReader, SimpleWavWriter, Speaker, TTSConfig, TTSManager
from app.vb_cable_writer import VBCableWriter


def test_new_tts():
    tts = TTS(TTSConfig(
        device=Device.GPU,
        default_speaker=Speaker.baya,
        models_path='./models/',
        download_model_if_not_exists=False,
    ))

    ttsm = TTSManager(tts, SimplePollingReader(), SimpleWavWriter())
    ttsm.start()
    pass


def test_tts_vb():
    tts = TTS(TTSConfig(
        device=Device.GPU,
        default_speaker=Speaker.baya,
        models_path='./models/',
        download_model_if_not_exists=False,
    ))

    ttsm = TTSManager(tts, SimplePollingReader(), VBCableWriter())
    ttsm.start()
