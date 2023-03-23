import contextlib
from pathlib import Path
import time
from typing import Any, Generator
import wave
from torch import Tensor
from app.io.io import Reader, Writer

from app.tts import SampleRate, Speaker


class SimplePollingReader(Reader):

    def configure(self) -> None:
        return super().configure()

    def close(self) -> None:
        return super().close()

    def read(self) -> Generator[tuple[str, Speaker | None], Any, None]:
        speaker = Speaker.baya

        print('\nPrint exit or stop for exit')
        while True:
            print('Print text for tts:')
            i = input().strip()

            if i.startswith('exit') or i.startswith('stop'):
                break

            if i.startswith('speaker'):
                input_speaker = i.removeprefix('speaker').strip()
                if not Speaker.contains(input_speaker):
                    print('Wrong speaker')
                    continue
                speaker = input_speaker # type: ignore
                continue

            sample = f"<speak>{i}</speak>"
            yield sample, speaker
            pass
        print('exit')
    pass


class SimpleWavWriter(Writer):

    def __init__(self, save_dir: str = './polling_results/') -> None:
        super().__init__()
        self.save_dir = save_dir
        self.__create_dir_if_not_exists(self.save_dir)

    def configure(self, sample_rate: SampleRate) -> None:
        self.sample_rate = sample_rate

    def close(self) -> None:
        return super().close()

    def write(self, audio: Tensor) -> Any:
        audio_name = int(time.time() * 1000)
        path = f'{self.save_dir}/{audio_name}.wav'

        audio_wav = (audio * 32767).numpy().astype('int16')

        with contextlib.closing(wave.open(path, 'wb')) as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_wav)
        pass

    def __create_dir_if_not_exists(self, path: str) -> None:
        if not (p := Path(path)).exists():
            p.mkdir()
    pass
