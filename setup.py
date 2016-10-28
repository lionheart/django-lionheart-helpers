#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2015 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

metadata = {}
metadata_file = "lionheart/metadata.py"
exec(compile(open(metadata_file).read(), metadata_file, 'exec'), metadata)

setup(
    name='django-lionheart-helpers',
    version=metadata['__version__'],
    url='http://lionheartsw.com',
    license=metadata['__license__'],
    description='Django decorators and some other utilities.',
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    packages=['lionheart']
)

