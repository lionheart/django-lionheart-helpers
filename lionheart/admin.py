import csv

from django.http import HttpResponse

import xlwt

# http://djangosnippets.org/snippets/2020/
def export_as_xls_action(filename, description="Export selected objects as XLS file",
                         fields=None, additional_fields=[], exclude=None, header=True):
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

        row = 0
        if header:
            column = 0
            for field_name in field_names:
                sheet.write(row, column, field_name)
                column += 1

            for field_name in additional_fields:
                sheet.write(row, column, field_name.replace("most_recent_", ""))
                column += 1

            row += 1

        for obj in queryset:
            column = 0
            for field_name in field_names:
                sheet.write(row, column, unicode(getattr(obj, field_name)).encode("utf-8"))
                column += 1

            for field_name in additional_fields:
                sheet.write(row, column, unicode(getattr(obj, field_name)).encode("utf-8"))
                column += 1

            row += 1

        book.save(response)
        return response
    export_as_xls.short_description = description
    return export_as_xls

# http://djangosnippets.org/snippets/2020/
def export_as_csv_action(filename, description="Export selected objects as CSV file",
                         fields=None, additional_fields=[], exclude=None, header=True):
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

        writer = csv.writer(response)
        if header:
            row = []
            for field_name in field_names:
                row.append(field_name)

            for field_name in additional_fields:
                row.append(field_name)

            writer.writerow(row)

        for obj in queryset:
            row = []
            for field_name in field_names:
                row.append(unicode(getattr(obj, field_name)).encode("utf-8"))

            for field_name in additional_fields:
                row.append(unicode(getattr(obj, field_name)).encode("utf-8"))

            writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv
