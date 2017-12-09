#!/usr/bin/env python

from distutils.core import setup

setup(
    name="n5reader",
    version="0.1.0",
    author="Carsten Haubold",
    author_email="carsten.haubold@iwr.uni-heidelberg.com",
    description=("Pure python reader for n5 files"),
    license="BSD",
    keywords="...",
    url="http://github.com/chaubold/n5reader",
    packages=['n5reader'], # list all package folders here that should be installed, e.g. also 'mypackage.util'
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6"
    ],
)
