from abc import ABC, abstractmethod
from typing import Any, Generator

from torch import Tensor

from app.tts import SampleRate, Speaker


class Reader(ABC):
    @abstractmethod
    def configure(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def read(self) -> Generator[tuple[str, Speaker | None], None, None]:
        pass
    pass


class Writer(ABC):
    @abstractmethod
    def configure(self, sample_rate: SampleRate) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def write(self, audio: Tensor) -> Any:
        pass
    pass
