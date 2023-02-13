from setuptools import setup

setup(
    name="qox",
    author="Oliver Bestwalter",
    copyright="Gen Digital Inc",
    version="23.2.10",
    packages=["qox_pkg"],
    extras_require={"lint": ["black", "mypy"], "test": ["pytest"]},
    entry_points={"console_scripts": ["qox = qox_pkg.qox:main"]},
)
