from keyboard import add_hotkey
import keyboard
from app.io.hotkeys import gather_hotkey_from_user_input


def test_hotkeys() -> None:
    hotkey = gather_hotkey_from_user_input()
    handler = add_hotkey(hotkey, print, args=(
        'triggered', 'hotkey'), suppress=True)
    print(f'hotkey added: {hotkey}')
    keyboard.wait('esc')
