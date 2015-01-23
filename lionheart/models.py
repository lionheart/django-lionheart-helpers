from hashlib import md5
import bcrypt
import random
import re

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string

import settings
from django.conf import settings as django_settings

class PasswordHelper(object):
    def __init__(self, password):
        self.password = password

    def __eq__(self, raw_password):
        return self.password == bcrypt.hashpw(raw_password, self.password)

    def __repr__(self):
        return "<Password: {}>".format(self.password)


class OptionalCharField(models.CharField):
    """
    Shortcut class that adds both `null` and `blank` attributes to
    `models.CharField`.
    """
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        super(OptionalCharField, self).__init__(*args, **kwargs)

class OptionalEmailField(models.EmailField):
    """
    Shortcut class that adds both `null` and `blank` attributes to
    `models.EmailField`.
    """
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        super(OptionalEmailField, self).__init__(*args, **kwargs)

class CreatedMixin(models.Model):
    """
    Abstract model mixin that adds `created_on` and `updated_on` fields to
    models.
    """
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta():
        abstract = True


def BcryptMixin(rounds=10):
    """
    Class factory that returns an abstract Django model mixin that adds tools
    to set and check bcrypt-secured passwords on user models.

    :param rounds: the number of log rounds to use for the salt generator
    :type rounds: int
    """

    class inner(models.Model):
        _password = models.CharField(max_length=60)
        """ Salted bcrypt passwords are never longer than 60 characters """

        class Meta():
            abstract = True

        @property
        def password(self):
            return PasswordHelper(self._password)

        @password.setter
        def password(self, raw_password):
            """
            Set the password of the user to `raw_password`.

            :param raw_password: text password
            :type raw_password: str
            """
            password = bcrypt.hashpw(raw_password, bcrypt.gensalt(rounds))
            self._password = password
            return True

        @password.deleter
        def password(self, new_password):
            self._password = None

        def check_password(self, raw_password):
            """
            Check that the user's password matches the given string.

            :param raw_password: text string
            :type raw_password: str
            """
            provided_password = bcrypt.hashpw(raw_password, self.password)
            return provided_password == self.password

        def is_authenticated(self):
            """ Instantiated users with the BcryptMixin are always authenticated """
            return True

        @property
        def is_staff(self):
            return False

        @property
        def is_active(self):
            return True

        @property
        def is_superuser(self):
            return False

    return inner


def PasswordResetMixin(template="emails/password_reset.txt",
        subject="Reset your password",
        sender="notifications@elmcitylabs.com",
        recipient_attribute='email'):
    """
    Class factory for a Django model mixin that adds a method to a user model
    to easily send password reset emails.

    :param template: the template to use for the email.
    :type template: str

    :param subject: the email subject line
    :type subject: str

    :param sender: who the email is sent from
    :type sender: str

    :param recipient_attribute: the field on the model which contains the
    user's email address
    :type recipient_attribute: str
    """
    class inner(models.Model):
        class Meta():
            abstract = True

        def send_password_reset_email(self):
            if settings.REDIS_AVAILABLE:
                """
                Send a password reset email to the user.
                """
                r = settings.Redis()
                code = md5(str(random.random())).digest().encode('base-64')

                non_alphanumeric = re.compile(r'[^a-zA-Z0-9]')
                code = non_alphanumeric.sub('', code)
                r.set(code, self.id)

                message = render_to_string(template, {
                    'user': self,
                    'code': code,
                    'BASE_URL': settings.BASE_URL })

                # Now send out the password reset email
                msg = EmailMultiAlternatives(subject, message, sender, [
                    getattr(self, recipient_attribute, None)])

                try:
                    msg.send()
                except:
                    pass
                return True
            else:
                raise Exception("Redis must be installed to use this feature.")
    return inner


def formatted_total(instance, Model, key, prefix="formatted_"):
    if key.startswith(prefix):
        value = object.__getattribute__(instance, key.replace(prefix, ""))
        if key == "formatted_tax":
            if value == 0:
                return "$0.00"
            elif value is None:
                return "-"

        return "${:,.2f}".format(value)
    else:
        return super(Model, instance).__getattribute__(key)


if django_settings.DEFAULT_FILE_STORAGE.endswith('Base64DatabaseStorage'):
    class UploadedFile(models.Model):
        filename = models.CharField(max_length=100)
        blob = models.TextField()
        size = models.BigIntegerField()

        def __unicode__(self):
            return self.filename
else:
    class UploadedFile():
        pass


class Orderable(models.Model):
    position = models.IntegerField(default=0)

    class Meta():
        abstract = True
        ordering = ('position',)

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.position is None:
            first = model.objects.order_by('-position').first()
            if first is None:
                self.position = 0
            else:
                self.position = first.position + 1

        return super(Orderable, self).save(*args, **kwargs)

