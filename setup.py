#!/usr/bin/env/python
# -*- coding: utf-8 -*-

from lionheart import metadata

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-lionheart-helpers',
    version=metadata.__version__,
    url='http://lionheartsw.com',
    license=metadata.__license__,
    description='Django decorators and some other utilities.',
    author=metadata.__author__,
    author_email=metadata.__email__,
    packages=['lionheart'],
    install_requires=[
        'django'
    ],
)

