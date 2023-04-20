import argparse
from app.tts import Device, Speaker, TTSConfig


def __boolean_string(s: str) -> bool:
    if s.lower() not in {'false', 'true'}:
        raise ValueError('Not a valid boolean string')
    return s.lower() == 'true'


def _parse(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(exit_on_error=True)

    parser.add_argument(
        '--gui',
        type=__boolean_string,
        default=True,
    )

    parser.add_argument(
        '--reader',
        type=str,
        default='PollingCommandReader',
        choices=['PollingCommandReader', 'SimpleWavWriter']
    )
    parser.add_argument(
        '--writer',
        type=str,
        default='VBCableWriter',
        choices=['VBCableWriter', 'SimpleWavWriter']
    )
    parser.add_argument(
        '--models_dir',
        type=str,
        default='./models/',
    )
    parser.add_argument(
        '--model_name',
        type=str,
        default='v3_1_ru.pt',
    )
    parser.add_argument(
        '--device',
        type=str,
        default='cuda',
        choices=['cpu', 'cuda']
    )

    return parser.parse_args(args=args)


def run_boot(sys_args: list[str]) -> None:
    args: argparse.Namespace = _parse(sys_args)

    print(args)

    tts_config = TTSConfig(
        device=Device.from_string(args.device),
        default_speaker=Speaker.baya,
        models_path=args.models_dir,
        model_name=args.model_name,
        download_model_if_not_exists=False,
    )

    if args.gui:
        from app.bootstrap.pyside_boot import boot as pyside_boot
        pyside_boot(tts_config)
    else:
        from app.bootstrap.tui_boot import boot as tui_boot
        tui_boot(tts_config, args)
