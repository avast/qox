import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import pytest

from qox import (
    QoxTaskFinder,
    QoxTask,
    QoxTaskFailedError,
    QOX_FOLDER,
)

HERE = Path(__file__).parent


@contextmanager
def top_less_qtf() -> Generator[QoxTaskFinder, None, None]:
    """Tests are in a project using qox itself => remove top path from search."""
    q = QoxTaskFinder()
    q.paths.pop(0)
    yield q


@contextmanager
def top_only_qtf(root_name: str) -> Generator[QoxTaskFinder, None, None]:
    """Provide a restricted qtf that only contains tasks from root."""
    old_path = Path.cwd()
    try:
        os.chdir(HERE / root_name)
        with top_less_qtf() as q:
            q.paths = [q.ROOT / QOX_FOLDER]
            yield q
    finally:
        os.chdir(old_path)


class TestBasics:
    def test_task_finding(self, monkeypatch):
        root_name = "task-finding"
        top = HERE / root_name / QOX_FOLDER
        middle = top.parent / "middle" / QOX_FOLDER
        lowest = middle.parent / "lowest" / QOX_FOLDER
        assert all(p.is_dir() for p in (top, middle, lowest))
        monkeypatch.chdir(lowest)
        with top_less_qtf() as qtf:
            assert qtf.ROOT == HERE / "task-finding"
            # check search path is good
            assert qtf.paths == [
                lowest.parents[2] / QOX_FOLDER,
                lowest.parents[1] / QOX_FOLDER,
                lowest,
            ]

            # check correct tasks are found
            for name, path in {
                "top-wins": top,
                "middle-wins": middle,
                "lowest-wins": lowest,
            }.items():
                task = qtf.fetch_task(name)
                assert issubclass(task.__class__, QoxTask)
                assert task.NAME == name
                assert task.PATH.parent == path

    @pytest.mark.parametrize(
        "name, exp",
        (
            ("generic-true", True),
            ("generic-false", False),
            ("python-true", True),
            ("python-false", False),
        ),
    )
    def test_runnable(self, name, exp):
        with top_only_qtf("runnable") as q:
            assert q.fetch_task(name).RUNNABLE == exp

    @pytest.mark.parametrize("task_type", ("generic", "python"))
    @pytest.mark.parametrize(
        "test_type, exp",
        (
            ("empty", ""),
            ("one-line", "one line"),
            ("multi-line", "multi\nline\nhelp"),
        ),
    )
    def test_help(self, task_type, test_type, exp):
        task_name = f"{task_type}-{test_type}"
        with top_only_qtf("help") as q:
            assert q.fetch_task(task_name).HELP == exp

    @pytest.mark.parametrize("task_type", ("generic", "python"))
    @pytest.mark.parametrize(
        "test_type, exp",
        (
            ("no-change", None),
            ("home", Path.home()),
            ("same", None),
        ),
    )
    def test_changedir(self, capfd, task_type, test_type, exp):
        name = f"{task_type}-{test_type}"
        with top_only_qtf("changedir") as q:
            task = q.fetch_task(name)
            assert task.CHANGEDIR == exp
            task.run()
            out = capfd.readouterr()[0]
            assert str(exp if exp else HERE / "changedir") in out

    def test_changedir_root_generic(self, capfd):
        os.chdir(HERE / "changedir")
        q = QoxTaskFinder()
        root = HERE.parent
        task = q.fetch_task("generic-root")
        assert task.CHANGEDIR == root
        task.run()
        out = capfd.readouterr()[0]
        assert str(root) in out.splitlines()


class TestGenericTasks:
    def test_execute_red(self, capfd):
        with top_only_qtf("task-type-generic") as q:
            task = q.fetch_task("generic-red")
            with pytest.raises(QoxTaskFailedError):
                task.run()
            out = capfd.readouterr()[0]
            assert "I am a miserable failure" in out

    def test_execute_green(self, capfd):
        with top_only_qtf("task-type-generic") as q:
            task = q.fetch_task("generic-green")
            task.run()
            out = capfd.readouterr()[0]
            assert "I am a raving success" in out


class TestPythonTasks:
    def test_execute_red(self, capsys):
        with top_only_qtf("task-type-python") as q:
            task = q.fetch_task("python-red")
            assert task.HELP == "A failing python task."
            with pytest.raises(SystemExit) as exc_info:
                task.run()
            assert exc_info.value.code == "I am a miserable failure!"

    def test_execute_green(self, capfd):
        with top_only_qtf("task-type-python") as q:
            task = q.fetch_task("python-green")
            task.run()
            out = capfd.readouterr()[0]
            assert "Everything is fine" in out

    def test_missing_module_resilience(self):
        with top_only_qtf("task-type-python") as q:
            task = q.fetch_task("python-missing-module")
            assert task._broken
            assert not task.RUNNABLE
            err = "🐛 python-missing-module (Module broken - import failed.)"
            assert err in task.FULL_INFO

    def test_missing_run_report(self):
        with top_only_qtf("task-type-python") as q:
            task = q.fetch_task("python-missing-run")
            with pytest.raises(AssertionError) as exc_info:
                task.run()
            exc_info.match(".*needs a qox function.*")
