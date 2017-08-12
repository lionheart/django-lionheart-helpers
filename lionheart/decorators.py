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

import logging
from functools import wraps

import django
from django.shortcuts import render as django_render
from django.http import HttpResponseRedirect
from django.template import loader as template_loader

from lionheart.utils import JSONResponse
from lionheart import forms
from lionheart import settings

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

            return django_render(request, template_name, context)
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


def create_redirect_if_required(fun):
    @functools.wraps(fun)
    def inner(self, *args, **kwargs):
        Model = self.__class__

        # Compare previous slug with new slug.
        try:
            unchanged_self = Model.objects.get(id=self.id)
        except Model.DoesNotExist:
            # There is no previous instance of the object, so we don't need to
            # do anything.
            pass
        else:
            old_path = unchanged_self.get_absolute_url()
            new_path = self.get_absolute_url()

            if old_path != new_path:
                # If the URL has changed, set up a redirect.
                with transaction.atomic():
                    # Update all relevant redirects to point towards the
                    # updated new_path.
                    previous_redirects = redirect_models.Redirect.objects \
                            .filter(new_path=old_path)
                    previous_redirects.update(new_path=new_path)

                    # If new_path is an existing old_path in another Redirect
                    # object, we delete that previous object to avoid a
                    # redirect loop.
                    redirect_models.Redirect.objects \
                            .filter(old_path=new_path) \
                            .delete()

                    params = {
                        'site_id': 1,
                        'old_path': old_path,
                        'new_path': new_path
                    }

                    try:
                        redirect_models.Redirect.objects.create(**params)
                    except IntegrityError:
                        pass

                    fun(self, *args, **kwargs)

                    # We return here so that the super call to save below does
                    # not get called.
                    return

        fun(self, *args, **kwargs)

    return inner
