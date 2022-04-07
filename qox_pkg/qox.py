"""qox - quality out of the box."""
# Copyright (c) 2022 Oliver Bestwalter
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import annotations

import logging
import os
import re
import stat
import sys
import textwrap
from functools import cached_property
from pathlib import Path
from pprint import pformat
from types import ModuleType
from typing import Any, cast

LOG = logging.getLogger(__name__)
QOX_FOLDER = ".qox"


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="<%(name)s:%(funcName)s(%(lineno)d) %(levelname)s> %(message)s",
    )

    args = sys.argv[1:]
    cmd = args.pop(0) if args else None
    qtf = QoxTaskFinder()

    if not cmd or cmd in ["-h", "--help"]:
        print("💯 ✨ qox - quality out of the box  - available tasks ✨ 💯")
        tasks_info = [t.FULL_INFO for t in qtf.TASK_MAP.values()]
        assert tasks_info, f"no tasks found in {qtf.paths} - add some tasks"
        print("\n".join(sorted(t.FULL_INFO for t in qtf.TASK_MAP.values())))
    else:
        task = qtf.fetch_task(cmd)
        try:
            task.run(args)
        except QoxTaskFailedError as e:
            sys.exit(f"qox task failed: {e}")


class QoxTaskFinder:
    _IGNORED_EXTENSIONS = [".ini"]

    def __init__(self) -> None:
        self.paths = self._find_qox_paths()
        self.handler_classes = self._collect_handler_classes()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}() => {[self.ROOT]}"

    @property
    def ROOT(self) -> Path:
        """The path containing the topmost .qox path is considered root.

        This is where the search for tasks will end.
        """
        return self.paths[0].parent

    def fetch_task(self, name: str) -> QoxTask:
        """Get a qox command object from its name."""
        assert name in self.TASK_MAP, f"'{name}' not in\n{pformat(self.TASK_MAP)}"
        task = self.TASK_MAP[name]
        self._ensure_is_executable(task.PATH)
        return task

    @cached_property
    def TASK_MAP(self) -> dict[str, QoxTask]:
        """Make a map of all qox tasks in all discoverable qox folders upwards.

        Each task can only exist once.
        More specific tasks with same name override less specific tasks further up.
        """
        task_map: dict[str, QoxTask] = {}
        for qox_path in self.paths:
            task_map.update(self._get_task_map(qox_path))
        return task_map

    @staticmethod
    def _collect_handler_classes() -> dict[str, type[QoxTask]]:
        """Find all classes implementing qox tasks and register them by file type."""
        extension2handler = {}
        for candidate in globals().values():
            if hasattr(candidate, "EXTENSION"):
                extension2handler[candidate.EXTENSION] = candidate
        return extension2handler

    def _get_task_map(self, qox_path: Path) -> dict[str, QoxTask]:
        task_map: dict[str, QoxTask] = {}
        for q in qox_path.iterdir():
            if q.name.startswith("_"):
                continue

            handler_class = self.handler_classes.get(q.suffix)
            if not handler_class:
                if q.suffix not in self._IGNORED_EXTENSIONS:
                    LOG.warning(f"[IGNORE] no task handler for {q}")
                continue

            task = handler_class(q, self.ROOT)
            task_map[task.NAME] = task
        return task_map

    @staticmethod
    def _find_qox_paths() -> list[Path]:
        paths = []
        candidate = Path.cwd() / QOX_FOLDER
        while True:
            if candidate.exists():
                paths.append(candidate)
            if len(candidate.parts) <= 2:
                break
            candidate = candidate.parents[1] / QOX_FOLDER

        assert paths, f"nothing to do from {Path.cwd()} upwards - add some .qox"
        return list(reversed(paths))

    @staticmethod
    def _ensure_is_executable(path: Path) -> None:
        if not os.access(path, os.X_OK):
            path.chmod(path.stat().st_mode | stat.S_IEXEC)


class QoxTask:
    EXTENSION: str

    def __init__(self, path: Path, root: Path) -> None:
        self.PATH = path
        self.ROOT = root
        self.NAME = self.PATH.with_suffix("").name
        rel_path = self.PATH.relative_to(self.ROOT).parents[1]
        self._REL_PATH = f"[{rel_path}] " if rel_path.name else ""
        self._LONG_NAME = f"{self._REL_PATH}{self.NAME}"
        self._broken = False

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}]{self._REL_PATH}{self.NAME}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"('{self.PATH.relative_to(self.ROOT)}', "
            f"'{self.ROOT.relative_to(self.ROOT)}')"
        )

    @property
    def CHANGEDIR(self) -> Path | None:
        """Directory to change into before running this task."""
        raise NotImplementedError

    @property
    def HELP(self) -> str:
        """Text that will be printed along the task, when calling calling for help."""
        raise NotImplementedError

    @property
    def RUNNABLE(self) -> bool:
        """Is the task runnable in the current context?"""
        raise NotImplementedError

    def run(self, args: list[str] = None) -> None:
        """Shared wrapper for all _run methods."""
        if not self.RUNNABLE:
            raise QoxTaskFailedError(f"\n{self.as_text}\n => task not RUNNABLE")

        msg = f"{self._LONG_NAME}"
        if self.CHANGEDIR:
            assert isinstance(self.CHANGEDIR, Path), f"bad type {self.CHANGEDIR}"
            try:
                changedir = self.CHANGEDIR.relative_to(self.ROOT)
            except ValueError:
                LOG.debug(f"task will run outside of {self.ROOT}")
                changedir = self.CHANGEDIR
            msg += f"\n[CHANGEDIR] {changedir if changedir.parts else '<qox root>'}"
        if args:
            msg = f"\n[args] {args}"
        msg += "\n[definition]\n" + textwrap.indent(self.as_text, "  ")
        LOG.info(msg)
        self._run(args or [])

    @property
    def FULL_INFO(self) -> str:
        """Full info about the task that will be printed, when calling for help."""
        if self._broken:
            msg = "  🐛"
        else:
            msg = "  🏃" if self.RUNNABLE else "  💤"
        msg += f" {self._LONG_NAME}"
        split_help = self.HELP.split("\n", maxsplit=1)
        if split_help[0]:
            msg += f" ({split_help[0]})"
        if len(split_help) == 2:
            msg += f"\n{textwrap.indent(split_help[1], '      ')}"
        return msg

    def _run(self, args: list[str]) -> None:
        raise NotImplementedError

    @cached_property
    def as_text(self) -> str:
        """Source code of the task."""
        return self.PATH.read_text()


class ShellTask(QoxTask):
    """Some script. Needs text munging to get at the meta data."""

    EXTENSION = ".sh"
    _EVAL_CONTEXT_FILE = "_qox_eval_context.py"

    @property
    def CHANGEDIR(self) -> Path | None:
        changedir = self._evaluate_criterion("CHANGEDIR")
        if not changedir or changedir == Path.cwd():
            return None

        assert isinstance(changedir, Path), changedir
        assert changedir.is_dir(), f"{changedir} is not an existing directory."
        return changedir

    @property
    def HELP(self) -> str:
        mark = "# HELP: "
        lines = self.as_text.splitlines()
        return "\n".join([h.replace(mark, "") for h in lines if mark in h])

    @property
    def RUNNABLE(self) -> bool:
        result = self._evaluate_criterion("RUNNABLE")
        return True if result is None else cast(bool, result)

    def _run(self, args: list[str]) -> None:
        cmd = f"{self.PATH}"
        if args:
            cmd = f"{cmd} {' '.join(args)}"
        if self.CHANGEDIR:
            cmd = f"cd {self.CHANGEDIR} && {cmd}"
        LOG.debug(f"full command: '{cmd}'")
        ret = os.system(cmd)
        if ret:
            raise QoxTaskFailedError(f"Task failed (error: {ret})")

    def _evaluate_criterion(self, criterion: str) -> Any | None:
        """Evaluate a criterion as a piece of Python code and return the result.

        NOTE: the expression must have all that is needed in the namespace.
          It can be placed in `_EVAL_CONTEXT_FILE` in the
          top `.qox` folder. All global objects will be provided during eval.
        """
        if match := re.search(rf"# {criterion}: (.*)", self.as_text):
            globals_dict = {
                # directory where the top .qox folder presides
                "ROOT": self.ROOT,
                # directory containing the task
                "HERE": self.PATH.parents[1],
            }
            context_path = self.ROOT / QOX_FOLDER / self._EVAL_CONTEXT_FILE
            if context_path.exists():
                qontext_module = import_python_module(context_path)
                globals_dict.update(vars(qontext_module))
            return eval(match[1], globals_dict)


class PythonTask(QoxTask):
    """A python module. Can use all project knowledge."""

    EXTENSION = ".py"
    _RUNNER_FUNCTION_NAME = "qox"
    _BROKEN_MODULE_MARKER = "qox-fake-module-py-broken"

    def __init__(self, path: Path, root: Path):
        super().__init__(path, root)
        self._py_module = self._load_py_module()
        self._broken = self._py_module.__name__ == self._BROKEN_MODULE_MARKER

    @property
    def CHANGEDIR(self) -> Path | None:
        try:
            changedir: Path | None = self._py_module.CHANGEDIR  # type: ignore
        except AttributeError:
            return None

        if not changedir or changedir == Path.cwd():
            return None

        assert changedir.is_dir(), f"{changedir} is not an existing directory."
        return changedir

    @property
    def HELP(self) -> str:
        return (self._py_module.__doc__ or "").strip()

    @property
    def RUNNABLE(self) -> bool:
        try:
            return cast(bool, self._py_module.RUNNABLE)  # type: ignore # noqa
        except AttributeError:
            return True

    def _run(self, args: list[str]) -> None:
        old_cwd = os.getcwd()
        try:
            if self.CHANGEDIR:
                os.chdir(self.CHANGEDIR)
            run_function = getattr(self._py_module, self._RUNNER_FUNCTION_NAME, None)
            assert run_function, f"FATAL: {self.PATH} needs a qox function."
            run_function(args or [])
        finally:
            os.chdir(old_cwd)

    def _load_py_module(self) -> ModuleType:
        """Load a python module or a non-crashing fake if broken."""
        try:
            py_module = import_python_module(self.PATH)
        except Exception as e:
            LOG.warning(f"{self.PATH} is broken: {e}")
            py_module = ModuleType(self._BROKEN_MODULE_MARKER)
            py_module.__doc__ = "Module broken - import failed."
            py_module.RUNNABLE = False  # type: ignore # noqa
        return py_module


def import_python_module(path: Path) -> ModuleType:
    """Given a path: load a Python module and evaluate it."""
    from importlib import util

    spec = util.spec_from_file_location(path.stem, path)
    module = util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module


class QoxTaskFailedError(Exception):
    """Raised in case a task failed."""
