# `qox` - quality out of the box

*(pronounced like: kyox ('k' as in cool, 'y' as in yes, 'o' as in otter, and 'x' as in Xena: Warrior Princess))*

A minimalistic, single file, zero dependency automation task runner to bundle project automation and unify command line and CI use for Python projects.

## Is this for you?

If you are a developer working on internal Python projects with a set of requirements where the established open source automation solutions are not a good fit or maybe just too much, qox might be a simple way to add automation (or consolidate existing automation) without much overhead.

Before you even consider going down this route, please ensure that you are aware of the following projects and have already ruled them out:

* [tox](https://tox.wiki)
* [nox](https://nox.thea.codes/)
* [invoke](https://www.pyinvoke.org/)
* [pants](https://www.pantsbuild.org/) (for monorepos)

If all these don't quite fit the bill and the following features and non-features sound not completely off, then the qox minimalist approach might be for you.

### Non-Features

* no venv / virtualenv handling - this is the responsibility of the project that
  qox is integrated into
* no configuration file (e.g. `nox.py` or `tox.ini`), configuration happens only in the task files
* just run one task at a time - no bundling, no build matrices, no parallelization and none of its complexities
* not even a command line interface worth the name

### Features

* drop `qox.py` in to your project and integrate it any way you like
* run all automation tasks locally and on CI via
  `python -m <path.to.qox> <taskname> <args for the task>` or simply `qox <taskname> <args for the task>` 
  (depending on how you integrated it)
* very small and simple enough to wrap your head around it to make it your own
* tasks are Python or shell scripts with full integration into the project knowledge
* tasks are discovered by searching for scripts with supported extensions in `.qox`
  folders in the project hierarchy - this automatically means that tasks can have scope
* this is meant to be an internal, developer facing tool - logging on debug level is the default and the source code of
  the task is dumped to the screen as part of the run.
* make qox your own: extend capabilities by changing the code rather than configuring it e.g.:
    * adding more task handler classes to e.g. support other task runners (e.g. Powershell)
    * changing the interface of all task runners to fit your needs
    * changing the logging / chattyness level as preferred
    * add argparse, fire, plumbum, click or whatever you are already using in the rest of your project to add a proper command line parser and add more command line options
    * for non python scripts - add `<root>/.qox/_qox_eval_context.py` to inject needed objects for evaluations, e.g. if and where a task should be run (`RUNNABLE`, `CHANGEDIR`).

## NOTES

## Steal This Code

This code is very likely only useful for internal projects. Although qox is pip-installable (but not published on pypi.org) and could be used "as-is" it is much more likely that you will just grab qox.py copy it into your project and "make it yours" in the ways described above.

# Where is the documentation?

As you are supposed to steal the code and make it your own, you need to understand what it does anyway, so best is: read the source. No really, it's a tiny file. Also run and read the tests to see how it works.

### This is Python 3.10+

The code is using 3.10+ features like [union types](https://peps.python.org/pep-0604/). If you want to use this for your own project and rely on older versions of python, you will need to make a few adjustments. 

### Only tested on Linux

This can definitely run on other Osses, but it is currently only tested / used on Linux. 
