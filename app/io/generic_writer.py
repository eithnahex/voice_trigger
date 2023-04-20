from dataclasses import dataclass
from enum import Enum, auto
from io import BytesIO
import time
from typing import Any
import wave
import pyaudio
from app.io.io import Writer
from app.tts import SampleRate


@dataclass
class WriterConfig:
    sample_rate: SampleRate
    audio_device_names: list[str]


class GenericWriter(Writer):

    def configure(self, config: WriterConfig) -> None:
        self.player = AudioPlayer(config)

        ...

    def close(self) -> None:
        self.player.close()
        del self.player

    def run_process() -> None:
        ...


class AudioDevices(str, Enum):
    DEFAULT = 'default'
    VB_CABLE_INPUT = 'CABLE Input'


class PlayerState(Enum):
    PLAY = auto()
    STOP = auto()


class AudioPlayer:

    def __init__(self, config: WriterConfig) -> None:
        self.config = config
        self.state: PlayerState = PlayerState.PLAY
        self.streams: list[pyaudio.Stream] = []
        self.pa = pyaudio.PyAudio()

        self.__init_streams()
        pass

    def close(self) -> None:
        self.stop()
        for s in self.streams:
            s.close()

        self.pa.terminate()

    class CallbackHolder:
        def __init__(self, device_name: str, data: wave.Wave_read) -> None:
            self.device_name = device_name
            self.data = data
            pass

        def __call__(self, in_data: Any, frame_count: int, time_info: float, status: int) -> tuple[bytes, int]:
            data = self.data.readframes(frame_count)

            return (data, pyaudio.paContinue)

    def __init_streams(self) -> None:
        for device in self.config.audio_device_names:
            if device is None:
                device = AudioDevices.DEFAULT

            callback = self.CallbackHolder(device)

            if device == AudioDevices.DEFAULT:
                self.__add_stream(callback=callback)
                continue

            info = self.get_device_info(device)
            if not info:
                raise Exception(f'Audio Device {device} not found.')

            self.__add_stream(callback=callback,
                              device_index=info.get('index'))

    def __add_stream(self, callback: CallbackHolder, device_index: int | None = None) -> None:
        stream = self.pa.open(
            stream_callback=callback,
            output=True,
            format=pyaudio.paInt16,
            channels=1,
            rate=self.config.sample_rate,
            start=False,
            # frames_per_buffer=CHUNK,
            output_device_index=device_index,
        )
        self.streams.append(stream)

    def get_device_info(self, device_name: str) -> dict | None:
        info = self.pa.get_host_api_info_by_index(0)

        for i in range(info.get('deviceCount')):
            inf = self.pa.get_device_info_by_host_api_device_index(0, i)
            if device_name in inf.get('name'):
                return inf

        return None

    def play(self, data: bytes) -> None:
        self.data = wave.open(BytesIO(data), 'rb')

        for s in self.streams:
            s.start_stream()

    def stop(self) -> None:
        if self.state is not PlayerState.STOP:
            self.state = PlayerState.STOP
            for s in self.streams:
                s.stop_stream()

    def resume(self) -> None:
        if self.state is PlayerState.STOP:
            self.state = PlayerState.PLAY
            for s in self.streams:
                s.start_stream()

    def is_any_active(self) -> bool:
        return any([s.is_active() for s in self.streams])

    @staticmethod
    def get_device_names(pa: pyaudio.PyAudio | None = None) -> list[str]:
        no_pa = pa is None
        if no_pa:
            pa = pyaudio.PyAudio()
        info = pa.get_host_api_info_by_index(0)  # type: ignore

        names: list[str] = []
        for i in range(info.get('deviceCount')):
            inf = pa.get_device_info_by_host_api_device_index(  # type: ignore
                0, i
            )
            names.append(inf.get('name'))

        if no_pa:
            pa.terminate()  # type: ignore
        return names
