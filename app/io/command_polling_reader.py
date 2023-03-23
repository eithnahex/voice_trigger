from collections import deque
from enum import Enum
from typing import Callable, Generator, TypeAlias
from app.io.io import Reader
from app.tts import Speaker


Cmd: TypeAlias = Callable[[str, 'PollingCommandReader'], str | None]


_commands: list[Cmd] = []


class ProsodyValues(str, Enum):
    pitch = 'pitch'
    rate = 'rate'

    x_slow = 'x-slow'
    slow = 'slow'
    medium = 'medium'
    fast = 'fast'
    x_fast = 'x-fast'

    x_low = 'x-low'
    low = 'low'
    high = 'high'
    x_high = 'x-high'

    robot = 'robot'

    @staticmethod
    def contains(obj: str) -> bool:
        return obj in [item.value for item in ProsodyValues]


def cmd(func: Cmd) -> Cmd:
    """
    cmd decorator
    """
    _commands.append(func)
    return func


class PollingCommandReader(Reader):
    def __init__(self) -> None:
        self.global_prosody_attrs: dict[str, str] = {}
        self.speaker: Speaker = Speaker.baya

    def configure(self) -> None:
        return super().configure()

    def close(self) -> None:
        return super().close()

    def read(self) -> Generator[tuple[str, Speaker | None], None, None]:

        print('\nPrint exit or stop for exit')
        while True:
            print()
            print('Print text for tts:')
            
            i = input().strip()
            
            sample = None
            do_continue = False
            for c in _commands:
                sample = c(i, self)
                if sample is None:
                    do_continue = True
                    break
            if do_continue:
                continue

            if i.startswith('exit') or i.startswith('stop'):
                break

            if i.startswith('speaker'):
                input_speaker = i.removeprefix('speaker').strip()
                if not Speaker.contains(input_speaker):
                    print('Wrong speaker')
                    continue
                self.speaker = input_speaker # type: ignore
                continue

            sample = f'<speak>{sample}</speak>'
            yield sample, self.speaker

            pass

        print('exit')
    pass


@cmd
def change_global_prosody(data: str, reader: PollingCommandReader) -> str | None:
    orig_data = data
    if data.startswith('g ') or data.startswith('global '):
        data = data.removeprefix('global ').removeprefix('g ')
        attrs = deque([s for s in data.replace(':', ' ').split(' ') if s != ''])
        if len(attrs) % 2 != 0:
            print("Wrong syntax")
            return None
        while attrs:
            attr, value = attrs.popleft(), attrs.popleft()
            if not ProsodyValues.contains(attr) or not ProsodyValues.contains(value):
                print("Wrong syntax")
                return None
            reader.global_prosody_attrs[attr] = value
        print(f'Set prosody attrs to: {reader.global_prosody_attrs}')
        return None

    if not reader.global_prosody_attrs:
        return orig_data

    prosody = '<prosody'
    for attr, value in reader.global_prosody_attrs.items():
        prosody += f' {attr}="{value}"'
    prosody += '>'

    data = f'{prosody}{data}</prosody>'
    return data
