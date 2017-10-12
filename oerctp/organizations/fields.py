import ast

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import Select, RendererMixin, ChoiceFieldRenderer, ChoiceInput
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


# Radio button table
class TableRadioChoiceInput(ChoiceInput):
    input_type = 'radio'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # FYI: this is executed only on the form (not in the admin) because the admin uses different widgets
        self.value = force_text(self.value)

    def render(self, name=None, value=None, attrs=None):
        attrs = dict(self.attrs, **attrs) if attrs else self.attrs
        return format_html('{}', self.tag(attrs))


class TableChoiceFieldRenderer(ChoiceFieldRenderer):

    choice_input_class = TableRadioChoiceInput

    def render(self):
        self.choices = self.choices[1:]  # Skip the blank choice
        id_ = self.attrs.get('id')
        output = []
        for i, choice in enumerate(self.choices):  # Skip the first == empty option
            w = self.choice_input_class(self.name, self.value, self.attrs.copy(), choice, i)
            output.append('<td>{}</td>'.format(force_text(w)))

        return format_html(
            '{content}',
            id_attr=format_html(' id="{}"', id_) if id_ else '',
            content=mark_safe('\n'.join(output)),
        )


class TableRadioSelect(RendererMixin, Select):
    renderer = TableChoiceFieldRenderer


# Choice with optional input
class OptionalChoiceWidget(forms.MultiWidget):
    def __init__(self, widgets, attrs=None):
        widgets[1].attrs['class'] = 'form-control'
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = ast.literal_eval(value)
            try: # todo: log this situation and find out when it occurs.
                return [value[0], value[1]]
            except:
                return [None, None]
        return [None, None]


class OptionalChoiceField(forms.MultiValueField):
    def __init__(self, choices, *args, **kwargs):
        fields = [
            forms.ChoiceField(choices=choices, widget=forms.RadioSelect, required=False),
            forms.CharField(required=False, widget=forms.TextInput, help_text='Other')
        ]
        self.widget = OptionalChoiceWidget(widgets=[f.widget for f in fields])
        super().__init__(required=False, fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if not data_list:
            raise ValidationError('This field is required.')

        if 'other' in data_list[0]:
            if not data_list[1]:
                raise ValidationError('You have to fill in the input if you select "Other".')
        else:
            if data_list[1]:
                raise ValidationError('You have to select "Other" if you want to fill in the input.')
        return data_list[0], data_list[1]


class OptionalMultiChoiceField(forms.MultiValueField):
    def __init__(self, choices, required=False, *args, **kwargs):
        self.required = required
        fields = [
            forms.MultipleChoiceField(choices=choices, widget=forms.widgets.CheckboxSelectMultiple, required=False),
            forms.CharField(required=False, widget=forms.TextInput, help_text='Other')
        ]
        self.widget = OptionalChoiceWidget(widgets=[f.widget for f in fields])
        super().__init__(required=False, fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if self.required and not data_list:
            raise ValidationError('You have to select an option or enter text for this field.')
        if data_list:
            if 'other' in data_list[0]:
                if not data_list[1]:
                    raise ValidationError('You have to fill in the input if you select "Other".')
            else:
                if data_list[1]:
                    raise ValidationError('You have to select "Other" if you want to fill in the input.')
            return data_list[0], data_list[1]
        return None, None
