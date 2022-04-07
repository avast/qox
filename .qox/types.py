"""run mypy over qox.py"""
import logging
import os
import sys
import timeit
from pathlib import Path
from pprint import pformat

LOG = logging.getLogger("qox-types")
HERE = Path(__file__).parent
CHANGEDIR = HERE.parent


def qox(args: list[str]) -> None:
    from mypy import api

    start = timeit.default_timer()
    args = args if args else ["qox_pkg/qox.py"]
    args = ["--config-file", str(HERE / "mypy.ini")] + args
    LOG.info(f"run mypy in {os.getcwd()}:\n{pformat(args)}")
    out, err, ret = api.run(args)
    end = timeit.default_timer()
    print(f"mypy needed {(end - start):.2f} seconds")
    if out:
        print(f"{out}")
    if err:
        print(f"[stderr]{err}")
    if ret:
        sys.exit(f"FATAL: failed with code {ret}")
