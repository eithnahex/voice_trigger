
from abc import ABC, abstractmethod
import contextlib
from enum import Enum
from os import PathLike
import os
from pathlib import Path
import time
from typing import Any, Generator, TypeAlias
import wave
from numpy import array

from torch import Tensor
import torch
from torch.package.package_importer import PackageImporter

from stubs.multi_acc_v3_package import TTSModelMultiAcc_v3


class Device(str, Enum):
    CPU = 'cpu'
    GPU = 'cuda'


class Speaker(str, Enum):
    baya = 'baya'
    xenia = 'xenia'
    kseniya = 'kseniya'
    aidar = 'aidar'
    eugene = 'eugene'
    random = 'random'

    @staticmethod
    def contains(obj: str) -> bool:
        return obj in [item.value for item in Speaker]


Sample: TypeAlias = str
SampleRate: TypeAlias = int


class Reader(ABC):
    @abstractmethod
    def read(self) -> Generator[None, None, tuple[Sample, SampleRate, Speaker | None]]:
        """
        return: generator with tuple of sample str, sample_rate int, Speaker | None
        """
        pass
    pass


class Writer(ABC):
    @abstractmethod
    def write(self, audio: Tensor, sample_rate: SampleRate) -> Any:
        pass
    pass


class TTSConfig():

    def __init__(
        self,
        device: Device,
        default_speaker: Speaker,
        model_name: str = 'v3_1_ru.pt',
        models_path: PathLike = '.',
        download_model_if_not_exists: bool = True,
        threads: int = 4,
        url_base_models_download: str = 'https://models.silero.ai/models/tts/ru/{}',
        warmup: bool = True,
        _jit_stuck_fix: bool = True,
    ) -> None:
        self.device = torch.device(device)
        self.default_speaker = default_speaker
        self.model_name = model_name
        self.models_path = models_path
        self.threads = threads
        self.url_base_models_download = url_base_models_download
        self.warmup = warmup
        self.download_model_if_not_exists = download_model_if_not_exists
        self._jit_stuck_fix = _jit_stuck_fix

        self._full_model_path = Path(
            f"{self.models_path}/{self.model_name}").resolve()

    def download_model(self):
        if not os.path.isfile(self._full_model_path):
            torch.hub.download_url_to_file(
                f"{self.url_base_models_download}/{self.model_name}", self.model_name
            )
        pass

    def get_model_path(self) -> PathLike:
        return self._full_model_path

    pass


class TTS():

    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        pass

    def do_tts(self, sample: str, sample_rate: int, speaker: Speaker | None = None) -> Tensor:
        speaker = speaker if speaker else self.config.default_speaker
        audio: Tensor = self.model.apply_tts(
            ssml_text=sample,
            speaker=speaker,
            sample_rate=sample_rate,
        )
        return audio

    @staticmethod
    def tensor_to_wav_array(audio: Tensor) -> array:
        # pytorch Tensor -> numpy array
        return (audio * 32767).numpy().astype('int16')

    def configure(self):
        print('configure...')
        if self.config._jit_stuck_fix:
            # fix torch stuck bug
            torch._C._jit_set_profiling_mode(False)

        torch.set_num_threads(self.config.threads)

        if self.config.download_model_if_not_exists:
            self.config.download_model()
        self.model = self._load_model()

        if self.config.warmup:
            self._warmup()

    def _load_model(self) -> TTSModelMultiAcc_v3:
        importer: PackageImporter = torch.package.PackageImporter(
            self.config.get_model_path()
        )

        model: TTSModelMultiAcc_v3 = importer.load_pickle(
            "tts_models",
            "model"
        )

        model.to(self.config.device)
        return model

    def _warmup(self):
        print('warmup...')
        self.model.apply_tts('с', speaker=self.config.default_speaker)
        pass

    pass


class TTSManager():
    def __init__(self, tts: TTS, inputer: Reader, outputer: Writer) -> None:
        self.tts = tts
        self.inputer = inputer
        self.outputer = outputer
        pass

    def start(self):
        self.tts.configure()

        for (sample, rate, speaker) in self.inputer.read():
            audio = self.tts.do_tts(
                sample, rate, speaker
            )
            self.outputer.write(audio, rate)
    pass


class SimplePollingReader(Reader):
    def read(self) -> Generator[None, None, tuple[str, SampleRate, Speaker | None]]:
        speaker = Speaker.baya
        sample_rate = 48000

        print('Print exit or stop for exit')
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
                speaker = input_speaker
                continue

            sample = f"<speak>{i}</speak>"
            yield sample, sample_rate, speaker
            pass
        print('exit')
    pass


class SimpleWavWriter(Writer):

    def __init__(self, save_dir: PathLike = './polling_results/') -> None:
        super().__init__()
        self.save_dir = save_dir
        self.__create_dir_if_not_exists(self.save_dir)

    def write(self, audio: Tensor, sample_rate: SampleRate) -> Any:
        audio_name = int(time.time() * 1000)
        path = f'{self.save_dir}/{audio_name}.wav'

        audio_wav = (audio * 32767).numpy().astype('int16')

        with contextlib.closing(wave.open(path, 'wb')) as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_wav)
        pass

    def __create_dir_if_not_exists(self, path: PathLike):
        if not (p := Path(path)).exists():
            p.mkdir()
    pass
