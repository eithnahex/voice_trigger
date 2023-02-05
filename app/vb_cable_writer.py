from multiprocessing import Process
from typing import Any
from numpy import array
import pyaudio
from torch import Tensor
from app.tts import SampleRate, Writer


class VBCableWriter(Writer):

    def __init__(self) -> None:
        super().__init__()
        self.device_name = 'CABLE Input'
        self.device_info = self._get_device_info()

    def write(self, audio: Tensor, sample_rate: SampleRate) -> Any:
        
        audio_wav = (audio * 32767).numpy().astype('int16')

        p1 = Process(target=self._play, args=(audio_wav, sample_rate))
        p2 = Process(target=self._play, args=(
            audio_wav, sample_rate, self.device_info.get('index'))
        )

        p1.start()
        p2.start()

        p1.join()
        p2.join()
        pass

    def _get_device_info(self) -> dict:
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        device_info = {}

        for i in range(info.get('deviceCount')):
            inf = p.get_device_info_by_host_api_device_index(0, i)
            if self.device_name in inf.get('name'):
                device_info = inf
        if not device_info:
            raise Exception(f"No device found: {device_info}")

        return device_info

    @staticmethod
    def _play(audio_wav: array, rate: SampleRate, device_index: int | None = None) -> None:
        CHUNK = 1024

        channels = 1

        p = pyaudio.PyAudio()

        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            frames_per_buffer=CHUNK,
            output=True,
            output_device_index=device_index
        )

        stream.write(audio_wav.tostring())
        stream.close()
        p.terminate()