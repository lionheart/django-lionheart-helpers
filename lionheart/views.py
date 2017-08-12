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

from django.http import HttpResponseRedirect
from django.db.models import get_model
from django.contrib.auth import authenticate, login

from decorators import render
from decorators import formify
from decorators import unauthenticated_users_only
from forms import ResetPasswordForm
from forms import ResetPasswordRequestForm
from utils import reverse_lazy
import settings

app_label, model_name = settings.PRIMARY_USER_MODEL.split('.')
GenericUser = get_model(app_label, model_name)

@unauthenticated_users_only
@render
def auth_password_reset(request):
    """
    Generic view to handle user password reset.
    """
    if settings.REDIS_AVAILABLE:
        r = settings.Redis()

        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                reset_code = form.cleaned_data['reset_code']
                password = form.cleaned_data['password']

                if reset_code not in r:
                    return HttpResponseRedirect(settings.HOME_URL)

                user_id = r[reset_code]
                del r[reset_code]

                user = GenericUser.objects.get(id=user_id)
                user.set_password(password)
                user.save()

                user = authenticate(email=user.email, password=password)
                if user:
                    login(request, user)

                return HttpResponseRedirect(settings.HOME_URL)
        else:
            reset_code = request.GET.keys()[0]
            if reset_code not in r:
                return HttpResponseRedirect(settings.HOME_URL)

            form = ResetPasswordForm(initial={
                'reset_code': reset_code})

        return {'form': form}
    else:
        raise Exception("Redis must be installed to use this feature.")

@render
@formify(ResetPasswordRequestForm, url=reverse_lazy('auth-password-reset-sent'))
def auth_password_reset_request(request, fields):
    """
    Generic view that handles password reset requests.
    """
    email = fields['email']

    # Reset the user's password and send them an email.
    if GenericUser.objects.filter(email=email).exists():
        user = GenericUser.objects.get(email=email)
        user.send_password_reset_email()

    return {}


