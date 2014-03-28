#!/usr/bin/env python

"""pygios
=========

A crazy simple framework for creating compliant nagios plugins

While the nagios monotoring framework really doesn't require mich more
than the monitoring script return a 0/non-0 status code, to fully
benefit from all of nagio's feautrues requires careful attention to
output formatting and error codes.  If you have a bevy of custom
parameters you'd like to monitor, creating a fully featured nagios
plugin for each can be a little tedious.  This module solves that
problem.


Getting started
===============

You'll need to install pygios.  Usually this means running pip or easy_install like ths

````bash
pip install pygios 
````

Now 

"""

from setuptools import setup

setup(
    name="pygios",
    version="0.0.2",
    author="Adam DePrince",
    author_email="deprince@googlealumni.com",
    description="Python based Nagios plugs made simple",
    long_description=__doc__,
    py_modules = [
        "pygios/__init__",
        ],
    packages = ["pygios"],
    zip_safe = True,
    include_package_data = True,
    classifiers = [],
    scripts = [
        ],
    install_requires = [
        "python-gflags",
        "python-gflags-multibool",
        ],
)
