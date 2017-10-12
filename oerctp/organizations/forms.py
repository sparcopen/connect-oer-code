from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import CheckboxSelectMultiple, RadioSelect

from .admin_forms import (
    AbstractAdminForm, AnnualImpactReportAdminForm, EventAdminForm, InstitutionProfileAdminForm, PolicyAdminForm, ProgramAdminForm, ResourceAdminForm
)
from .fields import TableRadioSelect
from .forms_mixins import SaveWithUserMixin
from .models import (
    InstitutionProfile, Event, Program, Policy, Resource, AnnualImpactReport, Abstract,
    AccessLink
)


class InstitutionProfileForm(InstitutionProfileAdminForm, SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = InstitutionProfile
        # #todo -- convert this to a templated form with hand-controlled HTML
        # #fyi -- "twitter_image_displayed" is not shown (SPARC can change the value through the back-end)
        # why are we listing fields explicitly? because there are many #opendata fields which we don't want to display
        fields=list('''
            institution_website
            institution_twitter
            poc_name
            poc_job
            poc_email
            poc_twitter
            poc_url
            poc_visibility
            overview_raw
            campus_engagement
            library_engagement
            subject_engagement
            url_oer
            url_libguide
            taskforce
            staff
            staff_location
            catalog
            oer_included
            oerdegree_offered

            private_comments
            filled_in_by
            acknowledgments
        '''.split())

        widgets = {
            'poc_visibility': RadioSelect(choices=InstitutionProfile.POC_VISIBILITY_CHOICES),
            'campus_engagement': CheckboxSelectMultiple(choices=InstitutionProfile.CAMPUS_ENGAGEMENT_CHOICES),
            'library_engagement': CheckboxSelectMultiple(choices=InstitutionProfile.LIBRARY_ENGAGEMENT_CHOICES),
            'subject_engagement': CheckboxSelectMultiple(choices=InstitutionProfile.SUBJECT_ENGAGEMENT_CHOICES),
            'taskforce': RadioSelect(choices=InstitutionProfile.TASKFORCE_CHOICES),
            'staff': RadioSelect(choices=InstitutionProfile.STAFF_CHOICES),
            'staff_location': CheckboxSelectMultiple(choices=InstitutionProfile.STAFF_LOCATION_CHOICES),
            'catalog': CheckboxSelectMultiple(choices=InstitutionProfile.CATALOG_CHOICES),
            'oer_included': CheckboxSelectMultiple(choices=InstitutionProfile.OER_INCLUDED_CHOICES),
            'oerdegree_offered': RadioSelect(choices=InstitutionProfile.OERDEGREE_OFFERED_CHOICES),
        }

class EventForm(EventAdminForm, SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['reviewed', 'hidden', 'institution']
        widgets = {
            # #todo -- 'type': Question Type: Radio button with fill-in other
            'type': RadioSelect(choices=Event.TYPE_CHOICES),
            'scope': RadioSelect(choices=Event.SCOPE_CHOICES),
        }


class ProgramForm(ProgramAdminForm, SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Program
        exclude = ['reviewed', 'hidden', 'institution']

        widgets = {
            'type': RadioSelect(choices=Program.TYPE_CHOICES),
            'home': RadioSelect(choices=Program.HOME_CHOICES),
            'partners': CheckboxSelectMultiple(choices=Program.PARTNERS_CHOICES),
            'scope': RadioSelect(choices=Program.SCOPE_CHOICES),
            'funding_library': forms.CheckboxSelectMultiple(choices=Program.FUNDING_LIBRARY_CHOICES),
            'strategy_adaptation': TableRadioSelect(),
            'strategy_adoption': TableRadioSelect(),
            'strategy_awareness': TableRadioSelect(),
            'strategy_curation': TableRadioSelect(),
            'strategy_pedagogy': TableRadioSelect(),
            'strategy_publication': TableRadioSelect(),
            'strategy_review': TableRadioSelect(),
            'strategy_research': TableRadioSelect(),
            'financial_sustainability': RadioSelect(choices=Program.FINANCIAL_SUSTAINABILITY_CHOICES),
            'incentives_conditions': RadioSelect(choices=Program.INCENTIVES_CONDITIONS_CHOICES),
        }


class PolicyForm(PolicyAdminForm, SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Policy
        exclude = ['reviewed', 'hidden', 'institution']

        widgets = {
            'policy_type': RadioSelect(choices=Policy.POLICY_TYPE_CHOICES),
            'scope': RadioSelect(choices=Policy.SCOPE_CHOICES),
            'policy_level': RadioSelect(choices=Policy.POLICY_LEVEL_CHOICES),
            'policy_definition': RadioSelect(choices=Policy.POLICY_DEFINITION_CHOICES),
        }


class ResourceForm(ResourceAdminForm, SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Resource
        exclude = ['reviewed', 'hidden', 'institution']
        widgets = {
            'type': CheckboxSelectMultiple(choices=Resource.TYPE_CHOICES),
            'scope': RadioSelect(choices=Resource.SCOPE_CHOICES),
            # #todo -- license -- Question Type: Drop down menu with fill-in other
            'license': RadioSelect(choices=Resource.LICENSE_CHOICES),
            'audience': CheckboxSelectMultiple(choices=Resource.AUDIENCE_CHOICES),
        }


class AnnualImpactReportForm(AnnualImpactReportAdminForm, SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = AnnualImpactReport
        fields = [
            'year', 'impact_students', 'impact_faculty', 'impact_courses', 'public_notes', 'private_notes',
            'awareness_rating_admin', 'awareness_rating_faculty', 'awareness_rating_library',
            'awareness_rating_students', 'private_comments', 'filled_in_by', 'acknowledgments',
        ]

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "An Annual Impact Report for the Academic Year you selected already exists. "
                                   "Please go back to the previous page and edit the existing report, or select a "
                                   "different Academic Year.",
            }
        }


class AbstractForm(AbstractAdminForm, SaveWithUserMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Abstract
        fields = ['language', 'abstract_raw', 'private_comments', 'filled_in_by', 'acknowledgments']


class EditAccessLinkForm(forms.ModelForm):
    class Meta:
        model = AccessLink
        fields = ['text_raw']


class ReviewProgramForm(SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Program
        fields = ['reviewed']


class ReviewEventForm(SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['reviewed']


class ReviewPolicyForm(SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Policy
        fields = ['reviewed']


class ReviewResourceForm(SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['reviewed']


class ReviewAnnualImpactReportForm(SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = AnnualImpactReport
        fields = ['reviewed']


class ReviewAbstractForm(SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = Abstract
        fields = ['reviewed']


class ReviewInstitutionProfileForm(SaveWithUserMixin, forms.ModelForm):
    class Meta:
        model = InstitutionProfile
        fields = ['reviewed']
