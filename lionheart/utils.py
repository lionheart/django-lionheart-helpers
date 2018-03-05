# Copyright 2015-2017 Lionheart Software LLC
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

import datetime
import json
import random
import re
import string
import time
import unicodedata

from django.http import HttpResponse
from django.utils.functional import lazy

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

try:
    # Django 1.6+
    from django.conf.urls import url
except ImportError:
    # Django 1.5
    from django.conf.urls.defaults import url

from django.views.generic.base import TemplateView

non_url_name_safe_characters = re.compile(r'[^a-z-]')

class IgnoreFormatString(object):
    """
    A simple class which takes a string and will ignore any formatting
    applied to it
    """
    def __init__(self, s):
        self.s = s

    def __str__(self):
        return self.s

    def __mod__(self, k):
        return self


class JSONResponse(HttpResponse):
    def __init__(self, content, content_type='application/json', *args, **kwargs):
        encoded_content = json.dumps(content)
        super(JSONResponse, self).__init__(
                content=encoded_content,
                content_type=content_type,
                status=200, *args, **kwargs)


def timestamped_file_url(prefix):
    def inner(instance, filename):
        r = re.compile(r'[^\S]')
        filename = r.sub('', filename)
        now = datetime.datetime.now()
        timestamp = int(time.time())
        return '{0}/{1.year:04}/{1.month:02}/{1.day:02}/{2}/{3}'.format( \
                prefix, now, timestamp, filename)
    return inner


def slugify(phrase, simple=True):
    """
    Removes all non-important words to generate a meaningful slug.
    """
    if simple:
        alphanumeric = re.compile(r'[^a-zA-Z0-9]+')
        slug = alphanumeric.sub('-', phrase.lower()).strip('-')
        if len(slug) == 0:
            return random.choice(string.lowercase)
        return slug
    else:
        from nltk import pos_tag, word_tokenize
        tokens = pos_tag(word_tokenize(phrase))
        words = []
        for token, pos in tokens:
            if pos in [
                    'CD',
                    'IN',
                    'JJ',
                    'JJR',
                    'NN',
                    'NNP',
                    'VB',
                    'VBG',
                    'VBN',
                    'WRB']:
                words.append(token)
        phrase = " ".join(words)
        symbols = re.compile(r'[^\w]')
        dashes = re.compile(r'-+')
        phrase = phrase.decode("unicode_escape")
        phrase = unicodedata.normalize("NFKD", phrase)
        phrase = phrase.encode("ascii", "ignore")
        phrase = phrase.lower()
        phrase = symbols.sub('-', phrase)
        phrase = dashes.sub('-', phrase)
        phrase = phrase.strip('-')
        return phrase


def simple_url(path, view, *args, **kwargs):
    """
    Shortcut method that generates a url for paths which map directly to view
    names.

        simple_url('auth/login', 'login_view')

    :param path: the URL path that you would like to map to
    :type path: str

    :param view: a view name or function
    :type view: str or function
    """
    if 'name' not in kwargs:
        kwargs['name'] = non_url_name_safe_characters.sub('-', path).strip('-')

    return url(r'^{}$'.format(path), view, *args, **kwargs)


def template_url(path):
    """
    Shortcut method that generates a url for paths which map directly to
    templates.

    For example, the following will map "/home" to the `home.html` template.

        simple_url('home')

    :param path: the URL path that you would like to the template to
    :type path: str
    """
    return url(
        r'^{}$'.format(path),
        TemplateView.as_view(template_name='{}.html'.format(path)),
        name=path.replace('/', '-')
    )

def home_url(logged_out_view, logged_in_view=None):
    """
    Shortcut method that serves two different views at '/', depending
    on whether the user is logged in or logged out.

    For example, the following will map "/" to the `home` view when the user is
    logged in, and the `landing` view when the user is not logged in.

        home_url('landing', 'home')

    :param logged_out_name: the name of the view that's served when the user is
    logged out
    :type logged_out_name: str

    :param logged_in_name: the name of the view that's served when the user is
    logged in
    :type logged_in_name: str

    :param app_name: the Django application used to serve the views
    :type app_name: str
    """
    if logged_in_view is None:
        return url(r'^$', logged_out_view, name='home')
    else:
        def authentication_redirect(request):
            if request.user.is_authenticated():
                return logged_in_view(request)
            else:
                return logged_out_view(request)

        return url(r'^$', authentication_redirect, name='home')

def status_204(request):
    """ Simple view which returns an empty 204 No Content response """
    return HttpResponse(status=204)

def random_digits(length):
    return ''.join(random.choice(string.digits) for _ in range(length))

def random_string(length):
    try:
        letters = string.letters
    except AttributeError:
        letters = string.ascii_letters

    alphanumeric = letters + string.digits
    return ''.join(random.choice(alphanumeric) for _ in range(length))


reverse_lazy = lazy(reverse, str)

