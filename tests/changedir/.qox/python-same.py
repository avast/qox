import os
from pathlib import Path

CHANGEDIR = Path(__file__).parents[1]


def qox(*_):
    print(os.getcwd())
