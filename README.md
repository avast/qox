# `qox` - quality out of the box

*(pronounced like: kyox ('k' as in cool, 'y' as in yes, 'o' as in otter, and 'x' as in Xena: Warrior Princess))*

A minimalistic, single file, zero dependency automation task runner to bundle project automation and unify command line and CI use for Python projects.

## Is this for you?

If you are a developer working on internal Python projects with a set of requirements where the established open source automation solutions are not a good fit or maybe just too much, `qox` might be a simple way to add automation (or consolidate existing automation) without much overhead.

Before you even consider going down this route, please ensure that you are aware of the following projects and have already ruled them out:

* [tox](https://tox.wiki)
* [nox](https://nox.thea.codes/)
* [invoke](https://www.pyinvoke.org/)
* [pants](https://www.pantsbuild.org/) (for monorepos)

If all these don't quite fit the bill and the following features and non-features sound not completely off, then the qox minimalist approach might be for you.

### Non-Features

* no (automatic) venv / virtualenv handling - this is the responsibility of the project that qox is integrated into (but can also be handled by qox tasks)
* no configuration file (e.g. `nox.py` or `tox.ini`), configuration happens only in the task files
* only run one task at a time - no bundling, no build matrices, no parallelization and none of its complexities
* not even a proper command line interface (just the bare functionality)

### Features

* drop `qox.py` in to your project and integrate it any way you like
* run all automation tasks locally and on CI via
  `python -m <path.to.qox> <taskname> <args for the task>` or simply `qox <taskname> <args for the task>` (depending on how you integrated it)
* very small and simple enough to wrap your head around it to make it your own
* tasks are Python or shell scripts with full integration into the project knowledge
* tasks are discovered by searching for scripts with supported extensions in `.qox` folders in the project hierarchy - this automatically means that tasks can have scope
* this is meant to be an internal, developer facing tool - logging on debug level is the default and the source code of the task is dumped to the screen as part of the run.
* make qox your own: extend capabilities by changing the code rather than configuring it e.g.:
    * adding more task handler classes to e.g. support other task runners (e.g. Powershell)
    * changing the interface of all task runners to fit your needs
    * changing the logging / chattyness level as preferred
    * add argparse, fire, plumbum, click or whatever you are already using in the rest of your project to add a proper command line parser and add more command line options
    * for non python scripts - add `<root>/.qox/_qox_eval_context.py` to inject needed objects for evaluations, e.g. if and where a task should be run (`RUNNABLE`, `CHANGEDIR`).

## Example: using qox to lint and test itself

To get started, a virtual environment with qox and test dependencies is needed:

```text
ob@xyz:~/[...]/qox$ ./bootstrap.sh 
+ .qox/dev.sh
+ rm -rf .venv
+ python3.10 -m venv .venv
+ .venv/bin/pip install --editable '.[lint,test]'
[...]
Successfully installed [...]
HINT: activate venv with ...
source .venv/bin/activate
```

```text
source .venv/bin/activate
```

This demo version of qox has a little `setup.py` that defines the test dependencies and sets `qox` as an entry point. This means it can be used as a command line tool now. Simply running `qox` without arguments, will give you all tasks you can run.  As this is an extremely simple project with no hierarchy of libs and sub projects or something similar you might have in a codebase that would integrate `qox`, there is only a top level `.qox` folder that contains what is needed to create a venv and run some linters and tests.

All functionality worth talking about, is in the tasks, which are specific to the codebase qox is integrated into. These simple uses here, can give an idea, what it could be used for (and much more).

```text
(qox@~/.../qox/.venv) ob@xyz:~/.../qox$ qox
💯 ✨ qox - quality out of the box  - available tasks ✨ 💯
  🏃 dev (ensure dev environment is in good shape)
      always create a fresh venv
  🏃 lint (run linters)
  🏃 test (run tests)
```

```text
(qox@~/.../qox/.venv) ob@xyz:~/[...]/qox$ qox lint
<qox_pkg.qox:run(195) INFO> lint
[definition]
  #!/usr/bin/env bash
  # CHANGEDIR: ROOT
  # HELP: run linters
  set -xe

  black qox_pkg/qox.py tests
  mypy qox_pkg/qox.py

<qox_pkg.qox:_run(257) DEBUG> full command: '~/[...]/qox/.qox/lint.sh'
+ black qox_pkg/qox.py tests
All done! ✨ 🍰 ✨
16 files left unchanged.
+ mypy qox_pkg/qox.py
Success: no issues found in 1 source file
```

```text
(qox@~/.../qox/.venv) ob@xyz:~/[...]/qox$ qox test
<qox_pkg.qox:run(195) INFO> test
[definition]
  #!/usr/bin/env bash
  # CHANGEDIR: ROOT
  # HELP: run tests
  set -e

  source .venv/bin/activate

  set -x
  pytest -l tests

<qox_pkg.qox:_run(257) DEBUG> full command: '~/[...]/qox/.qox/test.sh'
+ pytest -l tests
=============================== test session starts ================================
platform linux -- Python 3.10.0, pytest-7.1.1, pluggy-1.0.0
rootdir: ~/[...]/qox
collected 24 items                                                                                                                                                   
tests/test_qox.py ........................                                    [100%]

================================ 24 passed in 0.09s ================================
```

## FAQ

### How do I use this?

This code is very likely only useful for internal projects - for open source projects, tools like tox or nox are recommended. So the current recommendation is to steal the code and make it yours.

Copy `qox.py` and integrate it into your project (e.g. by adding it as an [entry point](https://packaging.python.org/en/latest/specifications/entry-points/#entry-points-specification)). 

I would also recommend adding the tests to your suite, you will likely make some adjustments, so the tests will come in handy as a base. The tests are using pytest. If you don't use pytest, wou will need to make some adjustments (or start using pytest ... what's holding you back?).

### Why can't I install it from `pypi.org`?

Whereas it wouldn't be hard to add this project to https://pypi.org, currently it simply isn't, because for the kind of projects this tool makes sense it is far better to steal the code and make it your own. This also ensures that you know what you are buying into, when you integrate this.

The way the `qox` grows and changes is then up to you and the needs of your project.

### Where is the documentation?

As you are supposed to steal the code and make it your own, you need to understand what it does anyway, so best is: read the source. No really, it's a [tiny file](./qox_pkg/qox.py). Also run and read the tests to see how it works.

### Why is this Python 3.10+?

Because the code is using features like [union types](https://peps.python.org/pep-0604/). 

If you want to use this for your own project and rely on older versions of python, you will need to make a few adjustments.

### Why is this only tested on Linux? 

Because that is where we use it, but this can definitely run on other operating systems and it won't be too hard to add specialized task runners for these systems if needed (e.g. Powershell on Windows).

### How can I contribute back, if I am supposed to steal the code?

Open an issue, in case ...

* there are bugs that need fixing directly in `qox`.
* you want to contribute some documentation or provide an example project demonstrating the use of `qox`.
* you found it useful. I would love to hear how you used it and how you adapted it to your project. That will make me happy.
