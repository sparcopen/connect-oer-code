import csv
from django.contrib import admin
from django.http import HttpResponse

# code based on https://web.archive.org/web/20170415183122/https://raw.githubusercontent.com/hackupc/backend/02cba72b4ea2f86cbb1382cdba2e975e26c03a93/register/utils.py which was inspired by: https://gist.github.com/mgerring/3645889

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields

        response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename=export.csv'
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    export_as_csv.short_description = description
    return export_as_csv

### #djangoadmin #howto -- define multiple views per model (several ModelAdmins) -- solution: use proxy models

def create_modeladmin(modeladmin, model, name = None, custom_verbose_plural = None):
    """
    Allows to register a model in multiple views
    https://stackoverflow.com/a/2228821 -> https://web.archive.org/web/20170415145137/https://stackoverflow.com/questions/2223375/multiple-modeladmins-views-for-same-model-in-django-admin
    """
    class Meta:
        proxy = True
        app_label = model._meta.app_label
        verbose_name_plural = custom_verbose_plural

    attrs = {'__module__': '', 'Meta': Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, modeladmin)
    return modeladmin
