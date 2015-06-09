import logging
from functools import wraps

import django
from django.shortcuts import render as django_render
from django.http import HttpResponseRedirect
from django.template import loader as template_loader

from utils import JSONResponse

import forms
import settings

logger = logging.getLogger(__name__)

def unauthenticated_users_only(fun):
    """
    Decorator which redirects users to `settings.HOME_URL` when the user is not
    logged in.
    """
    def resource(request, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.HOME_URL)
        return fun(request, **kwargs)
    return resource

def redirect(url):
    """
    Decorator factory for views which generates a function that performs a 302
    redirect to the given URL unless another action is explicitly given by the
    view.

    :param url: the url to redirect to
    :type url: str
    """
    def k(fun):
        @wraps(fun)
        def wrapper(request, *args, **kwargs):
            response = fun(request, *args, **kwargs)
            if type(response) == dict:
                return HttpResponseRedirect(url)
            return response
        return wrapper
    return k

def render_json(fun):
    """
    Decorator for views which return a dictionary that encodes the dictionary
    into a JSON string and sets the mimetype of the response to
    application/json.
    """
    @wraps(fun)
    def wrapper(request, *args, **kwargs):
        response = fun(request, *args, **kwargs)
        try:
            return JSONResponse(response)
        except TypeError:
            # The response isn't JSON serializable.
            return response
    return wrapper

def render_to(template):
    def k(fun):
        @wraps(fun)
        def wrapper(request, *args, **kwargs):
            context = fun(request, *args, **kwargs)
            if type(context) == dict:
                return django_render(request, template, context)
            else:
                return context
        return wrapper
    return k

def render(fun):
    """
    Decorator for views which return a dictionary that sets the dictionary as
    the template context and uses the view name as a heuristic for the template
    name.

    If the original view doesn't return a dictionary, the response is
    untouched.

    The following code sets the template context to `{'name': "Steve Jobs"}` and
    feeds it into "home.html".

        @render
        def home(request):
            return {'name': "Steve Jobs"}
    """
    name = fun.__name__.replace("_", "/")

    @wraps(fun)
    def wrapper(request, *args, **kwargs):
        context = fun(request, *args, **kwargs)
        if isinstance(context, dict):
            template_name = name + ".html"
            template_name_with_underscores = template_name.replace('_', '-')
            template = template_loader.select_template(
                [template_name, template_name_with_underscores]
            )

            template_name = None
            if django.VERSION > (1, 8):
                template_name = template.template.name
            else:
                template_name = template.name

            return django_render(request, template.name, context)
        else:
            return context

    return wrapper

def render_to(template):
    """
    Decorator generator for views which return a dictionary that renders the
    view to `template` and sets the returned dictionary as the template
    context.

    If the original view doesn't return a dictionary, the response is
    untouched.

    The following code sets the template context to `{'name': "Steve Jobs"}` and
    feeds it into "home.html".

        @render_to("home.html")
        def home_view(request):
            return {'name': "Steve Jobs"}
    """
    def decorator(fun):
        @wraps(fun)
        def wrapper(request, *args, **kwargs):
            context = fun(request, *args, **kwargs)
            if isinstance(context, dict):
                return django_render(request, template, context)
            else:
                return context
        return wrapper
    return decorator

def formify(form_obj, url='/', save=False, tipsy_errors=False):
    """
    TODO
    """
    def renderer(fun):
        @wraps(fun)
        def wrapper(request, *args, **kwargs):
            if request.method == 'GET':
                form = form_obj()
            else:
                form = form_obj(request.POST)
                if form.is_valid():
                    try:
                        if save:
                            obj = form.save()
                            fun(request, obj, **dict(form.cleaned_data))
                        else:
                            fun(request, **dict(form.cleaned_data))

                        return HttpResponseRedirect(url)
                    except forms.InvalidFormException:
                        return {'form': form}
                else:
                    if tipsy_errors:
                        for field_name, errors in form.errors.iteritems():
                            widget = form.fields[field_name].widget
                            widget.attrs['rel'] = "tipsy"
                            widget.attrs['title'] = ", ".join(errors)

                    logger.debug(form.errors)

            return {'form': form}
        return wrapper
    return renderer

