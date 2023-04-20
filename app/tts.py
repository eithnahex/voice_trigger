from enum import Enum
import os
from pathlib import Path
from typing import TypeAlias
from torch import Tensor
import torch
from torch.package.package_importer import PackageImporter

from app.typing.multi_acc_v3_package import TTSModelMultiAcc_v3


class Device(str, Enum):
    CPU = 'cpu'
    GPU = 'cuda'

    @staticmethod
    def from_string(device: str) -> 'Device':
        device = device.lower()
        if device == 'cpu':
            return Device.CPU
        if device == 'cuda':
            return Device.GPU
        raise Exception(f"Unknown Device {device}")


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


class TTSConfig():

    def __init__(
        self,
        device: Device,
        default_speaker: Speaker,
        sample_rate: SampleRate = 48000,
        model_name: str = 'v3_1_ru.pt',
        models_path: str = '.',
        download_model_if_not_exists: bool = True,
        threads: int = 4,
        url_base_models_download: str = 'https://models.silero.ai/models/tts/ru/{}',
        warmup: bool = True,
        _jit_stuck_fix: bool = True,
    ) -> None:
        self.sample_rate = sample_rate
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

    def download_model(self) -> None:
        if not os.path.isfile(self._full_model_path):
            torch.hub.download_url_to_file(
                f"{self.url_base_models_download}/{self.model_name}", self.model_name
            )
        pass

    def get_model_path(self) -> str:
        return str(self._full_model_path)

    pass


class TTS():

    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        pass

    def do_tts(self, sample: str, speaker: Speaker | None = None) -> Tensor:
        speaker = speaker if speaker else self.config.default_speaker
        audio: Tensor = self.model.apply_tts(
            ssml_text=sample,
            speaker=speaker,
            sample_rate=self.config.sample_rate,
        )
        return audio

    def configure(self) -> None:
        print('tts configure...')
        if self.config._jit_stuck_fix:
            # fix torch stuck bug
            torch._C._jit_set_profiling_mode(False)

        torch.set_num_threads(self.config.threads)

        if self.config.download_model_if_not_exists:
            self.config.download_model()
        self.model = self._load_model()

        if self.config.warmup:
            self._warmup()
        
        print('TTS ready')

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

    def _warmup(self) -> None:
        print('model warmup...')
        self.model.apply_tts('с', speaker=self.config.default_speaker)
        pass

    pass
