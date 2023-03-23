from queue import Queue
from typing import Callable
import keyboard
from keyboard._keyboard_event import KeyboardEvent

handlers: dict = {}


def add_hotkey(hotkey: str, cb: Callable, args: tuple = (), suppress: bool = True) -> None:
    handler = keyboard.add_hotkey(
        hotkey=hotkey,
        callback=cb,
        args=args,
        suppress=suppress,
    )
    handlers[hotkey] = handler


def clear_hotkey(hotkey: str) -> None:
    if hotkey in handlers:
        keyboard.remove_hotkey(hotkey)
    else:
        print(f'Hotkey "{hotkey}" not found.')


def clear_all_hotkeys() -> None:
    for h in handlers:
        keyboard.remove_hotkey(h)


def setup_hotkeys() -> None:
    ...


def read_hotkey() -> list[KeyboardEvent]:
    # alternate: keyboard.read_hotkey()
    print('Input the hotkey:')

    hotkey: list[KeyboardEvent] = []

    q: Queue[KeyboardEvent] = Queue()
    keyboard.start_recording(recorded_events_queue=q)

    last = None
    while True:
        key: KeyboardEvent = q.get()
        if 'enter' in key.name:
            keyboard.stop_recording()
            break

        if key.name == 'backspace':
            if key.event_type == keyboard.KEY_UP and hotkey:
                hotkey.pop()
                print(" + ".join([k.name for k in hotkey]))
            continue

        if (key.event_type == keyboard.KEY_DOWN) and (key != last) and (key not in hotkey):
            hotkey.append(key)
            print(" + ".join([k.name for k in hotkey]))

        last = key
    return hotkey


def gather_hotkey_from_user_input() -> str:
    while True:
        hotkey = ' + '.join([key.name for key in read_hotkey()])
        print(f'"{hotkey}" is okay? y/n')

        while True:
            answer = keyboard.read_key()
            if answer.lower() == 'y':
                return hotkey
            if answer.lower() == 'n':
                break
