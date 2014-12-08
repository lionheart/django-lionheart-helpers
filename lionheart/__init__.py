# -*- coding: utf-8 -*-

"""
Django Statictastic
~~~~~~~~~~~~~~~~~~~

:copyright: © 2014 Lionheart Software
"""

from .metadata import (
    __author__,
    __copyright__,
    __email__,
    __license__,
    __maintainer__,
    __version__,
)

from django.conf import settings
if not settings.configured:
    settings.configure()

import decorators
import forms
import models
import settings
import storages
import urls
import utils
import validators
import views

__all__ = [
    '__author__', '__copyright__', '__email__', '__license__',
    '__maintainer__', '__version__'
    'decorators',
    'forms',
    'models',
    'settings',
    'storages',
    'urls',
    'utils',
    'validators',
    'views'
]

