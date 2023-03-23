import numpy
import torch
from app.io.command_polling_reader import PollingCommandReader
from app.io.simple import SimplePollingReader, SimpleWavWriter
from app.io.vb_cable_writer import VBCableWriter
from app.manager import TTSManager

from app.tts import TTS, Device, Speaker, TTSConfig


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


def test_vb_queued():
    tts = TTS(TTSConfig(
        device=Device.GPU,
        default_speaker=Speaker.baya,
        models_path='./models/',
        download_model_if_not_exists=False,
    ))

    ttsm = TTSManager(tts, SimplePollingReader(), VBCableWriter())
    ttsm.start()
    pass


def test_cmd_polling():
    reader = PollingCommandReader()
    reader.configure()
    
    for result in reader.read():
        print(result)

    reader.close()
    pass

def test_manager_with_cmd_polling():
    tts = TTS(TTSConfig(
        device=Device.GPU,
        default_speaker=Speaker.baya,
        models_path='./models/',
        download_model_if_not_exists=False,
    ))

    ttsm = TTSManager(tts, PollingCommandReader(), VBCableWriter())
    ttsm.start()
    pass