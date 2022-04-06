import os
from pathlib import Path

CHANGEDIR = Path.home()


def qox(*_):
    print(os.getcwd())
