from multiprocessing import Process, Queue
from typing import Any
from numpy import ndarray
import numpy
import pyaudio
from torch import Tensor

from app.io.io import Writer
from app.tts import SampleRate


class VBCableWriter(Writer):
    msg_ready = 'ready'
    msg_close = 'close'

    def configure(self, sample_rate: SampleRate) -> None:
        self.configured = True
        self.device_name = 'CABLE Input'
        self.sample_rate = sample_rate
        self.device_info = self._get_device_info()
        self.q_data: Queue = Queue()
        self.q_signals: Queue = Queue()
        self.processes: list[Process] = self._run_processes()

    def close(self) -> None:
        if not self.configured:
            raise Exception("call Writer#configure() first!")

        print('writer closing...')

        self.q_data.put(VBCableWriter.msg_close)

        for p in self.processes:
            if p.is_alive():
                p.terminate()

        for p in self.processes:
            p.join()

        print('writer closed')
        pass

    def write(self, audio: Tensor) -> Any:
        if not self.configured:
            raise Exception("call Writer#configure() first!")

        audio_wav = self._tensor_to_wav_array(audio).tobytes()
        self.q_data.put_nowait(audio_wav)
        self.q_data.put_nowait(audio_wav)

        pass

    def _run_processes(self) -> list[Process]:
        processes = [
            Process(target=self._work, args=(
                self.q_data,
                self.q_signals,
                self.sample_rate, None,
                "default stream")
            ),
            Process(target=self._work, args=(
                self.q_data,
                self.q_signals,
                self.sample_rate,
                self.device_info.get('index'),
                "vb_cable stream")
            ),
        ]

        for p in processes:
            p.start()

        # wait for ready
        for _ in processes:
            msg = self.q_signals.get()
            if msg == VBCableWriter.msg_ready:
                continue
            else:
                raise Exception(
                    f'Message error. Expected value: {VBCableWriter.msg_ready}. Iтcoming value: {msg}')

        return processes

    @staticmethod
    def _work(
        q_data: Queue,
        q_signals: Queue,
        sample_rate: SampleRate,
        device_index: int | None = None,
        process_name: str = 'process'
    ) -> None:
        print(f'{process_name}: configure...')
        p = pyaudio.PyAudio()

        CHUNK = 1024
        channels = 1

        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            frames_per_buffer=CHUNK,
            output=True,
            output_device_index=device_index
        )

        # send ready
        q_signals.put(VBCableWriter.msg_ready)

        print(f'{process_name}: ready')
        while True:
            if not q_signals.empty() and q_signals.get_nowait() == VBCableWriter.msg_close:
                break

            data = q_data.get()
            stream.write(data)

        stream.close()
        p.terminate()
        print(f'{process_name}: stopped')
        pass

    @staticmethod
    def _tensor_to_wav_array(tensor: Tensor) -> ndarray:
        return (tensor * 32767).numpy().astype(numpy.int16)

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

        p.terminate()

        return device_info
