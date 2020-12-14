#!/usr/bin/env python
from setuptools import setup

setup(
    name="raoc",
    version="0.1.0",
    url="https://github.com/clbarnes/raoc",
    author="Chris L. Barnes",
    author_email="chrislloydbarnes@gmail.com",
    description=(
        "Script to automate random acts of coffee: "
        "random scheduled meetups within a group"
    ),
    py_modules=["raoc"],
    install_requires=["yagmail", "strictyaml"],
    entry_points={"console_scripts": ["raoc=raoc:main"]}
)
