from setuptools import setup

setup(
    name="qox",
    version="0.1",
    packages=["qox_pkg"],
    extras_require={"lint": ["black", "mypy"], "test": ["pytest"]},
    entry_points={"console_scripts": ["qox = qox_pkg.qox:main"]},
)
