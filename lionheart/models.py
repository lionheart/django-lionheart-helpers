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

from hashlib import md5
import random
import re

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string

import settings
from django.conf import settings as django_settings


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


class SlugField(models.SlugField):
    def __init__(self, *args, **kwargs):
        help_text = "Lowercase with no punctuation and any whitespace replaced by dashes."
        kwargs['help_text'] = help_text
        kwargs['unique'] = True
        super(SlugField, self).__init__(*args, **kwargs)


class SoftDeleteMixin(models.Model):
    """
    Abstract Django model mixin to add 'deleted' column
    This column is set to OK/DELETED which the SoftDeleteManager
    and SoftDeleteQuerySet use.
    """
    OK = 0
    DELETED = 1

    STATE_CHOICES = (
        (OK, "ok"),
        (DELETED, "deleted"),
    )

    deleted = models.IntegerField(choices=STATE_CHOICES, default=OK)

    def delete(self, *args, **kwargs):
        self.deleted = self.DELETED
        self.save()

    def remove_permanently(self, *args, **kwargs):
        super(SoftDeleteMixin, self).delete(*args, **kwargs)

    class Meta:
        abstract = True

class SoftDeleteQuerySet(models.query.QuerySet):
    """
    SubClass of the standard Django QuerySet that ignores soft-deleted rows,
    and overwrites the delete function to update with soft-delete instead
    """
    def delete(self, using='default', *args, **kwargs):
        for model in self:
            model.delete(using, *args, **kwargs)

    def remove_permanently(self):
        return super(SoftDeleteQuerySet, self).delete()

    def deleted(self):
        qs = super(SoftDeleteQuerySet, self).filter(deleted=SoftDeleteMixin.DELETED)
        # Cast qs to SoftDeleteQuery because super() returns a plain ol' QuerySet
        qs.__class__ = SoftDeleteQuerySet
        return qs

    def all_with_deleted(self):
        qs = super(SoftDeleteQuerySet, self).all()
        # Cast qs to SoftDeleteQuery because super() returns a plain ol' QuerySet
        qs.__class__ = SoftDeleteQuerySet
        return qs

class SoftDeleteManager(models.Manager):
    """
    Soft Delete Object Manager that uses the SoftDeleteQuerySet so when you use objects.all(),
    rows with deleted=DELETED will not be returned!
    Also adds propeties to see deleted/active rows
    """
    def all_with_deleted(self):
        qs = super(SoftDeleteManager, self).get_queryset()
        if hasattr(self, 'core_filters'):  # it's a RelatedManager
            qs = qs.filter(**self.core_filters)
        # Cast qs to SoftDeleteQuery because super() returns a plain ol' QuerySet
        qs.__class__ = SoftDeleteQuerySet
        return qs

    def get_queryset(self):
        qs = super(SoftDeleteManager, self).get_queryset().filter(deleted=SoftDeleteMixin.OK)
        # Cast qs to SoftDeleteQuery because super() returns a plain ol' QuerySet
        qs.__class__ = SoftDeleteQuerySet
        return qs

    def remove_permanently(self):
        return super(SoftDeleteManager, self).get_queryset().delete()

    def get(self, *args, **kwargs):
        return self._queryset_from_kwarg_conditions(kwargs).get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        qs = self._queryset_from_kwarg_conditions(kwargs).filter(*args, **kwargs)
        # Cast qs to SoftDeleteQuery because super() returns a plain ol' QuerySet
        qs.__class__ = SoftDeleteQuerySet
        return qs

    def _queryset_from_kwarg_conditions(self, kwargs):
        if 'pk' in kwargs or 'id' in kwargs:
            return self.all_with_deleted()
        else:
            return self.get_queryset()

    def _get_active(self):
        return self.get_queryset()

    def _get_deleted(self):
        qs = super(SoftDeleteManager, self).get_queryset().filter(deleted=SoftDeleteMixin.DELETED)
        # Cast qs to SoftDeleteQuery because super() returns a plain ol' QuerySet
        qs.__class__ = SoftDeleteQuerySet
        return qs

    active = property(_get_active)
    deleted = property(_get_deleted)
