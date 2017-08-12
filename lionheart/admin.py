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

import csv
import operator
import json
import datetime

from django.http import HttpResponse
from django.utils import timezone

import xlwt

def handle_field(field):
    if type(field) is datetime.datetime:
        return timezone.make_naive(field)
    elif type(field) is dict:
        return json.dumps(field)
    else:
        return str(field)

# http://djangosnippets.org/snippets/2020/
def export_as_xls_action(filename, description="Export as XLS",
                         fields=None, additional_fields=[], m2m_fields={},
                         exclude=None, header=True):
    """
    This function returns an export XLS action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """

    def export_as_xls(modeladmin, request, queryset):
        """
        Generic xls export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        if fields:
            fieldset = set(fields)
            field_names = fields
        else:
            field_names = set([field.name for field in opts.fields])

            if exclude:
                excludeset = set(exclude)
                field_names = field_names - excludeset

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        book = xlwt.Workbook(encoding="utf-8")
        sheet = book.add_sheet("Results")

        m2m_field_names = map(operator.itemgetter("name"), m2m_fields)
        m2m_field_groups = map(operator.itemgetter("group_by_name"), m2m_fields)
        m2m_field_group_models = map(operator.itemgetter("group_by_model"), m2m_fields)

        m2m_instances_to_field_names = {}
        for field_name, group_name, Model in zip(m2m_field_names, m2m_field_groups, m2m_field_group_models):
            for instance in Model.objects.all():
                m2m_instances_to_field_names[instance] = (field_name, group_name)

        m2m_instances = m2m_instances_to_field_names.keys()

        row = 0
        if header:
            column = 0
            for field_name in field_names:
                sheet.write(row, column, field_name)
                column += 1

            for field_name in additional_fields:
                sheet.write(row, column, field_name)
                column += 1

            for instance in m2m_instances:
                sheet.write(row, column, unicode(instance))
                column += 1

            row += 1

        for obj in queryset:
            column = 0
            for field_name in field_names:
                sheet.write(row, column, handle_field(operator.attrgetter(field_name)(obj)))
                column += 1

            for field_name in additional_fields:
                sheet.write(row, column, handle_field(operator.attrgetter(field_name)(obj)))
                column += 1

            for instance, (field_name, group_name) in m2m_instances_to_field_names.items():
                field = operator.attrgetter(field_name)(obj)
                queryset = field.filter(**{group_name: instance})
                value = ", ".join(map(str, queryset))
                sheet.write(row, column, value)
                column += 1

            row += 1

        book.save(response)
        return response
    export_as_xls.short_description = description
    return export_as_xls

# http://djangosnippets.org/snippets/2020/
def export_as_csv_action(filename, description="Export as CSV",
                         fields=None, additional_fields=[], m2m_fields={},
                         exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """

    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        if fields:
            fieldset = set(fields)
            field_names = fields
        else:
            field_names = set([field.name for field in opts.fields])

            if exclude:
                excludeset = set(exclude)
                field_names = field_names - excludeset

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        m2m_field_names = map(operator.itemgetter("name"), m2m_fields)
        m2m_field_groups = map(operator.itemgetter("group_by_name"), m2m_fields)
        m2m_field_group_models = map(operator.itemgetter("group_by_model"), m2m_fields)

        m2m_instances_to_field_names = {}
        for field_name, group_name, Model in zip(m2m_field_names, m2m_field_groups, m2m_field_group_models):
            for instance in Model.objects.all():
                m2m_instances_to_field_names[instance] = (field_name, group_name)

        m2m_instances = m2m_instances_to_field_names.keys()

        writer = csv.writer(response)
        if header:
            row = []
            for field_name in field_names:
                row.append(field_name)

            for field_name in additional_fields:
                row.append(field_name)

            for instance in m2m_instances:
                row.append(unicode(instance))

            writer.writerow(row)

        for obj in queryset:
            row = []
            for field_name in field_names:
                row.append(handle_field(operator.attrgetter(field_name)(obj)))

            for field_name in additional_fields:
                row.append(handle_field(operator.attrgetter(field_name)(obj)))

            for instance, (field_name, group_name) in m2m_instances_to_field_names.items():
                field = operator.attrgetter(field_name)(obj)
                queryset = field.filter(**{group_name: instance})
                value = ", ".join(map(str, queryset))
                row.append(value)

            writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv
