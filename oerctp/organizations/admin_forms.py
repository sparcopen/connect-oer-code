import ast

from django import forms
from django.core.validators import ValidationError

from .fields import OptionalChoiceField, OptionalMultiChoiceField
from .forms_mixins import SaveWithUserMixin
from .models import Abstract, Tag, Policy, Program, InstitutionProfile, Event, Resource

# FYI: make sure to exclude 'slug' field to avoid #errormessage "Please correct the error below."
# with no error highlighted (so the form cannot be edited in a way that the error goes away)

class TagAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['type', 'name', 'slug']
        exclude = []
        # exclude.append('slug') # DO NOT ENABLE `exclude.append('slug')` here: this would crash the app when adding a new tag in admin


class TagMembershipAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        exclude = ['reviewed', 'hidden']
        exclude.append('slug')


class TagProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        exclude = ['reviewed', 'hidden', 'system_name', 'system_website', 'system_link']
        exclude.append('slug')


class TagPersonAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        exclude = ['reviewed', 'hidden', 'system_name', 'system_website', 'system_link']
        exclude.append('slug')


class TagSystemAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['type', 'name', 'slug', 'description', 'system_name', 'system_website', 'system_link']
        exclude = []
        exclude.append('slug')


class TagGeneralAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        exclude = ['reviewed', 'hidden']
        exclude.append('slug')

class AnnualImpactReportAdminForm(SaveWithUserMixin, forms.ModelForm):
    pass

class AbstractAdminForm(SaveWithUserMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['language'] = OptionalChoiceField(
            choices=Abstract.LANGUAGE_CHOICES,
            help_text='Please indicate which language the abstract is written in. Note that English is not an option, '
                      'because English abstracts are entered as part of the Institutional Profile form. Once you save '
                      'this form, you will have the option to create additional abstracts in other languages if '
                      'desired.',
        )

    class Meta:
        model = Abstract
        exclude = []


class PolicyAdminForm(SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Policy
        exclude = []

    def clean(self):
        # todo: use this validation in user form as well
        cleaned_data = super().clean()

        # At least 1 url has to be defined
        if not (cleaned_data.get('url_text') or cleaned_data.get('url_description') or
                cleaned_data.get('url_announcement') or cleaned_data.get('url_report')):
            msg = 'You must provide at least one link to more information. Please ensure at least one of the boxes in this section is filled in.'

            raise ValidationError({
                'url_text': msg,
                'url_description': msg,
                'url_announcement': msg,
                'url_report': msg,
            })

        return cleaned_data


class ProgramAdminForm(SaveWithUserMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # do not set hardcoded values (i.e., with a fixed string) via "self.initial" for strategy_adaptation, strategy_adoption, or any other field -- this would override stored values from the database both in the admin *and* on the form and display the hardcoded values everywhere
        self.initial['partners'] = ast.literal_eval(self.initial.get('partners', '[]'))
        self.initial['funding_library'] = ast.literal_eval(self.initial.get('funding_library', '[]'))
        self.fields['incentives'] = OptionalMultiChoiceField(
            label=Program.INCENTIVES_VERBOSE_NAME,
            choices=Program.INCENTIVES_CHOICES,
            help_text=Program.INCENTIVES_HELP_TEXT

            # todo -- Validation: If other is selected, then text box should be minimum 1 character, maximum 50
            # characters. If “Not applicable”, no other options may be selected.
        )

        self.fields['funding_source'] = OptionalMultiChoiceField(
            label='Source(s) of Program Funding',
            choices=Program.FUNDING_SOURCE_CHOICES,
            help_text='Please select all sources of program funding below',
            # todo -- Validation: If Other is checked, the other box must have between 1 and 140 characters.
        )

    class Meta:
        model = Program
        exclude = []

        widgets = {
            'partners': forms.CheckboxSelectMultiple(choices=Program.PARTNERS_CHOICES),
            'funding_library': forms.CheckboxSelectMultiple(choices=Program.FUNDING_LIBRARY_CHOICES),
        }

    def clean(self):
        # todo: use this validation in user form as well
        cleaned_data = super().clean()

        errors = {}

        # At least 1 url has to be defined
        if not (cleaned_data.get('url_program') or cleaned_data.get('url_mou') or
                cleaned_data.get('url_assess') or cleaned_data.get('url_job') or
                cleaned_data.get('url_other')):
            msg = 'You must provide at least one link to more information. Please ensure at least one of the boxes in this section is filled in.'

            errors.update({
                'url_program': msg,
                'url_mou': msg,
                'url_assess': msg,
                'url_job': msg,
                'url_other': msg,
            })

        # Exactly 1 strategy must be primary!
        strategies = [
            'strategy_adaptation', 'strategy_adoption', 'strategy_awareness', 'strategy_curation',
            'strategy_pedagogy', 'strategy_publication', 'strategy_review', 'strategy_research'
        ]
        primary = sum(1 for strategy in strategies if cleaned_data.get(strategy, '') == 'primary')
        if primary != 1:
            msg = 'Must select exactly one option as Primary. May select any number (including 0) as Secondary.'
            errors.update({
                strategy: msg for strategy in strategies
            })

        if errors:
            raise ValidationError(errors)

        return cleaned_data


class InstitutionProfileAdminForm(SaveWithUserMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        custom_initials = [
            'campus_engagement',
            'library_engagement',
            'subject_engagement',
            'staff_location',
            'catalog',
            'oer_included',
        ]

        for key in custom_initials:
            try:
                self.initial[key] = ast.literal_eval(self.initial[key])
            except (ValueError, KeyError):
                self.initial[key] = []

        # avoid nine dashes ("---------") for empty choices
        # #todo -- fix this on other forms, too
        for field in ('campus_engagement', 'subject_engagement', 'oer_included', 'oerdegree_offered'):
            self.fields[field].empty_label = None

    class Meta:
        model = InstitutionProfile
        exclude = []
        widgets = {
            'campus_engagement': forms.CheckboxSelectMultiple(choices=InstitutionProfile.CAMPUS_ENGAGEMENT_CHOICES),
            'library_engagement': forms.CheckboxSelectMultiple(choices=InstitutionProfile.LIBRARY_ENGAGEMENT_CHOICES),
            'subject_engagement': forms.CheckboxSelectMultiple(choices=InstitutionProfile.SUBJECT_ENGAGEMENT_CHOICES),
            'staff_location': forms.CheckboxSelectMultiple(choices=InstitutionProfile.STAFF_LOCATION_CHOICES),
            'catalog': forms.CheckboxSelectMultiple(choices=InstitutionProfile.CATALOG_CHOICES),
            'oer_included': forms.CheckboxSelectMultiple(choices=InstitutionProfile.OER_INCLUDED_CHOICES),
        }


class EventAdminForm(SaveWithUserMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['type'] = OptionalChoiceField(
            label='Event Type',
            help_text='Please indicate the type of event. Please note that we are looking for only events that were '
                      'directly organized by your institution.',
            choices=Event.TYPE_CHOICES
            # todo -- Validation: If other is selected, then text box should be minimum 1 character,
            # maximum 140 characters.
        )

    class Meta:
        model = Event
        exclude = []

    def clean(self):
        # todo: use this validation in user form as well
        cleaned_data = super().clean()

        errors = {}

        # At least 1 url has to be defined
        fields = ['url_summary', 'url_promo', 'url_recording', 'url_slides', 'url_photos', 'url_news']
        url_count = sum(1 for field_name in fields if (cleaned_data.get(field_name)))
        if url_count == 0:
            msg = 'You must provide at least one link to more information. Please ensure at least one of the boxes in this section is filled in.'

            errors.update({
                field: msg for field in fields
            })

        if errors:
            raise ValidationError(errors)

        return cleaned_data


class ResourceAdminForm(SaveWithUserMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.initial['type'] = ast.literal_eval(self.initial.get('type', '[]'))
        self.initial['audience'] = ast.literal_eval(self.initial.get('audience', '[]'))

        self.fields['license'] = OptionalChoiceField(
            choices=Resource.LICENSE_CHOICES,
            help_text='Please specify the copyright permissions of the work.',
            # todo -- Validation: Required. If Other is selected, the text must be between 1 and 300 characters.
        )

    class Meta:
        model = Resource
        exclude = []
        widgets = {
            'type': forms.CheckboxSelectMultiple(choices=Resource.TYPE_CHOICES),
            'audience': forms.CheckboxSelectMultiple(choices=Resource.AUDIENCE_CHOICES),
        }
