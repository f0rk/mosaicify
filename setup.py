# Copyright 2017, Ryan P. Kelly. All Rights Reserved.

from __future__ import absolute_import

from setuptools import setup


setup(
    name="mosaicify",
    version="1.0",
    description="Create image mosaics",
    author="Ryan P. Kelly",
    author_email="ryan@ryankelly.us",
    url="http://blog.ryankelly.us/",
    scripts=[
        "scripts/mosaicify",
    ],
    install_requires=[
        "pillow",
        "numpy",
    ],
    test_suite="nose.collector",
    package_dir={"": "lib"},
    packages=["mosaicify"],
)
