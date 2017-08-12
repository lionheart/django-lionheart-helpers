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

from django.utils.translation import ugettext_lazy as _
from django import forms

class InvalidFormException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

class PlaceholderTextInput(forms.TextInput):
    """
    Django form text input that turns off autocomplete and provides a shortcut
    for setting a placeholder.
    """
    def __init__(self, name, **kwargs):
        kwargs['placeholder'] = name
        kwargs['autocomplete'] = 'off'
        super(PlaceholderTextInput, self).__init__(attrs=kwargs)


class PlaceholderPasswordInput(forms.PasswordInput):
    """
    Django form password input that turns off autocomplete and provides a shortcut
    for setting a placeholder.
    """
    def __init__(self, name, **kwargs):
        kwargs['placeholder'] = name
        kwargs['autocomplete'] = 'off'
        super(PlaceholderPasswordInput, self).__init__(attrs=kwargs)


class PasswordField(forms.CharField):
    """
    Django field for password input that turns off autocomplete and contains a
    shortcut for setting a placeholder.
    """
    def __init__(self, placeholder='', *args, **kwargs):
        widget = PlaceholderPasswordInput(placeholder)
        super(PasswordField, self).__init__(widget=widget, *args, **kwargs)


class ResetPasswordRequestForm(forms.Form):
    """
    Generic password reset request form that only requires email address.
    """
    email = forms.EmailField()


class ResetPasswordForm(forms.Form):
    """
    Generic password reset form that requires a new password and a randomly
    generated `reset_code` to verify user authenticity.
    """
    password = forms.CharField(widget=PlaceholderPasswordInput("Password"))
    reset_code = forms.CharField(widget=forms.HiddenInput)

    def clean_password(self):
        """
        Validates that the password is at least 6 characters.
        """
        password = self.cleaned_data['password']
        if len(password) < 6:
            raise forms.ValidationError(_("Password must be at least 6 characters"))
        return password

class ErrorForm(forms.ModelForm):

    """
    Adds class='error' to form elements when an error is found.
    """

    def clean(self):
        if self.errors:
            for name, field in self.fields.iteritems():
                if name in self.errors:
                    field.widget.attrs={'class': 'error'}
        return self.cleaned_data
