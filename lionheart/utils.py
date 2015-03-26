import datetime
import json
import random
import re
import string
import time
import unicodedata

from django.http import HttpResponse
from django.utils.functional import lazy
from django.core.urlresolvers import reverse
try:
    # Django 1.5
    from django.conf.urls.defaults import url
except ImportError:
    # Django 1.6+
    from django.conf.urls import url

from django.views.generic.base import TemplateView

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

def simple_url(path, view=None):
    """
    Shortcut method that generates a url for paths which map directly to view
    names.

    For example, the following will map "/home" to the `home` view.

        simple_url('home')

    If the you would like your URL to be mapped to a different path than the
    name of your view, just provide the view name or function as the second
    parameter. E.g.,

        simple_url('auth/login', 'login_view')

    :param path: the URL path that you would like to map to
    :type path: str

    :param view: a view name or function (optional)
    :type view: str or function
    """
    if not view:
        view = path.replace('/', '_')

    return url(r'^%s$' % path,
            view,
            name=path.replace('/', '-'))

def template_url(path):
    """
    Shortcut method that generates a url for paths which map directly to
    templates.

    For example, the following will map "/home" to the `home.html` template.

        simple_url('home')

    :param path: the URL path that you would like to the template to
    :type path: str
    """
    return url(r'^%s$' % path,
            TemplateView.as_view(template_name=path + '.html'),
            name=path.replace('/', '-'))

def home_url(logged_out_name, logged_in_name=None, app_name='app'):
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
    app = __import__(app_name, fromlist=['views'])
    logged_out_view = getattr(app.views, logged_out_name)

    if logged_in_name:
        logged_in_view = getattr(app.views, logged_in_name)

        def authentication_redirect(request):
            if request.user.is_authenticated():
                return logged_in_view(request)
            else:
                return logged_out_view(request)

        return url(r'^$',
                authentication_redirect,
                name='home')
    else:
        return url(r'^$',
                logged_out_view,
                name='home')

def status_204(request):
    """ Simple view which returns an empty 204 No Content response """
    return HttpResponse(status=204)

def random_digits(length):
    return ''.join(random.choice(string.digits) for _ in range(length))

def random_string(length):
    alphanumeric = string.letters + string.digits
    return ''.join(random.choice(alphanumeric) for _ in range(length))


reverse_lazy = lazy(reverse, str)

