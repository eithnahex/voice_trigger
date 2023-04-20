import sys
from app.bootstrap.bootstrap import run_boot

"""
Pytorch install: pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
"""


def main() -> None:
    args = sys.argv[1:]
    run_boot(args)


if __name__ == "__main__":
    main()
