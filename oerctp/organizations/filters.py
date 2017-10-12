from django import forms
from django.db.utils import ProgrammingError
from django.contrib.auth.models import User, Group
from .models import Institution, InstitutionProfile, Program, Policy, Event, Resource, Abstract

import ast
import django_filters

# FYI: https://docs.google.com/document/d/1203rWEibAFdM_tJuc05WvWivRTS6YFBePePRPOGO6ME/edit
# FYI: filter types listed here: https://github.com/carltongibson/django-filter/blob/develop/django_filters/filters.py
# FYI: plant_number = django_filters.ChoiceFilter(choices=[[o.id, o.plant_number + " " + o.Manufacturer] for o in Plant.objects.all().order_by('IMS_plant')])

"""
class UserFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    year_joined = django_filters.NumberFilter(name='date_joined', lookup_expr='year')
    groups = django_filters.ModelMultipleChoiceFilter(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'year_joined', 'groups']

# FYI: custom filters act here act like `django_filters.AllValuesMultipleFilter`
# based on: https://github.com/ChrisHartley/blight_fight/blob/4a532c38e18f79caf16fb57aa39cc644e93c0f27/property_inquiry/filters.py
class MyTestFilter(django_filters.ChoiceFilter):

    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = qs.order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = [(o, o) for o in qs]
        self.extra['choices'].insert(0, ('', u'------',))
        self.extra['choices'].append(('', u'------',))
        return super(MyTestFilter, self).field
"""

class CustomEventTypeFilter(django_filters.MultipleChoiceFilter):
    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = qs.order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = [] # list(self.extra['choices']) # # convert to list, so we can append
        # self.extra['choices'] = [(o, o) for o in qs]
        # return super(CustomEventTypeFilter, self).field
        for o in qs:
            lst = ast.literal_eval(o)
            if str(lst[0]) == 'other':
                event_type = str(lst[1]) + ' (Custom Type)'
            else:
                event_type = dict(Event.TYPE_CHOICES).get(str(lst[0]), 'Unknown')
            self.extra['choices'].append((o, event_type))
        return super(CustomEventTypeFilter, self).field


class CustomAbstractLanguageFilter(django_filters.MultipleChoiceFilter):
    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = qs.order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = [] # list(self.extra['choices']) # # convert to list, so we can append
        for o in qs:
            lst = ast.literal_eval(o)
            if str(lst[0]) == 'other':
                lang = str(lst[1])
            else:
                lang = dict(Abstract.LANGUAGE_CHOICES).get(str(lst[0]), 'Unknown')
            self.extra['choices'].append((o, lang))
        return super(CustomAbstractLanguageFilter, self).field


class CustomResourceTypeFilter(django_filters.MultipleChoiceFilter):
    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = qs.order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = [] # convert to list, so we can append
        for o in qs:
            output = []
            try:
                lst = ast.literal_eval(o)
                dct = dict(Resource.TYPE_CHOICES)
                if not (len(lst) == 1 and str(lst[0]) == "other"):
                    for item in lst:
                        output.append(dct.get(item))
            except ValueError:
                pass
            if output:
                output = ', '.join(output)
                self.extra['choices'].append((o, output))
        return super(CustomResourceTypeFilter, self).field


class CustomResourceAudienceFilter(django_filters.MultipleChoiceFilter):
    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = qs.order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = []
        for o in qs: # reimplementation of audience_directorypage (#todo -- cleanup, code duplication is bad)
            output = []
            try:
                lst = ast.literal_eval(o)
                dct = dict(Resource.AUDIENCE_CHOICES)
                if not (len(lst) == 1 and str(lst[0]) == "other"):
                    for item in lst:
                        output.append(dct.get(item))
            except ValueError:
                pass

            if output:
                output = ', '.join(output)
                self.extra['choices'].append((o, output))

        return super(CustomResourceAudienceFilter, self).field


class CustomProgramFundingSourceFilter(django_filters.MultipleChoiceFilter):
    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = qs.order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = [] # convert to list, so we can append

        for o in qs:
            output = []
            try:
                lst = ast.literal_eval(o)
                dct = dict(Program.FUNDING_SOURCE_CHOICES)
                if lst[0] == None:
                    pass
                elif len(lst[0]) == 1 and lst[0][0] == "other":
                    pass
                else:
                    for item in lst[0]:
                        if item != 'other':
                            output.append(dct.get(item))
                        else:
                            output.append('Other: ' + lst[1])
            except ValueError:
                pass
            if output:
                output = ', '.join(output)
                self.extra['choices'].append((o, output))

        return super(CustomProgramFundingSourceFilter, self).field


class CustomProgramIncentivesFilter(django_filters.MultipleChoiceFilter):
    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = qs.order_by(self.name).values_list(self.name, flat=True)
        self.extra['choices'] = [] # convert to list, so we can append

        for o in qs:
            output = []
            try:
                lst = ast.literal_eval(o)
                dct = dict(Program.INCENTIVES_CHOICES)
                if lst[0] == None:
                    pass
                elif len(lst[0]) == 1 and lst[0][0] == "other":
                    pass
                else:
                    for item in lst[0]:
                        if item != 'other':
                            output.append(dct.get(item))
                        else:
                            output.append('Other: ' + lst[1])
            except ValueError:
                pass
            if output:
                output = ', '.join(output)
                self.extra['choices'].append((o, output))

        return super(CustomProgramIncentivesFilter, self).field


class InstitutionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Institution Name contains') # queryset=Institution.objects.all()
    city = django_filters.CharFilter(name='profile__city', lookup_expr='icontains', label='City name contains')
    poc_name = django_filters.CharFilter(name='profile__poc_name', lookup_expr='icontains', label='Point of Contact name contains')

    """
    Why Try-Except? Avoid errors when running "docker-compose -f dev.yml run django python manage.py migrate" (when the database is empty):
    `django.db.utils.ProgrammingError: relation "organizations_institutionprofile" does not exist`
    `psycopg2.ProgrammingError: relation "organizations_institutionprofile" does not exist`

    """
    try:
        state_province_choices = [(i, dict(InstitutionProfile.STATE_PROVINCE_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('state_province', flat=True).distinct()]
        state_province_choices_sorted = sorted(state_province_choices, key=lambda tup: tup[1])
        # https://web.archive.org/web/20171010210134/https://stackoverflow.com/questions/3121979/how-to-sort-list-tuple-of-lists-tuples
        state_province = django_filters.MultipleChoiceFilter(
            name='profile__state_province',
            label='State/Province',
            # choices=InstitutionProfile.STATE_PROVINCE_CHOICES,
            choices = state_province_choices_sorted,
            widget=forms.CheckboxSelectMultiple,
        )

        country = django_filters.ChoiceFilter( # #dropdown
            name='profile__country',
            label='Country',
            choices=InstitutionProfile.COUNTRY_CHOICES,
        )

        highest_degree = django_filters.MultipleChoiceFilter(
            name='profile__highest_degree',
            label='Highest Degree Offered',
            choices=InstitutionProfile.HIGHEST_DEGREE_CHOICES,
            widget=forms.CheckboxSelectMultiple,
        )

        size = django_filters.MultipleChoiceFilter(
            name='profile__size', # see also: enrollment
            label='Enrollment',
            choices=InstitutionProfile.SIZE_CHOICES,
            # choices = [(i, dict(InstitutionProfile.SIZE_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('size', flat=True).distinct()],
            widget=forms.CheckboxSelectMultiple,
        )

        location_type = django_filters.MultipleChoiceFilter(
            name='profile__location_type',
            label='Location Type',
            choices=InstitutionProfile.LOCATION_TYPE_CHOICES,
            # choices = [(i, dict(InstitutionProfile.LOCATION_TYPE_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('location_type', flat=True).distinct()],
            widget=forms.CheckboxSelectMultiple,
        )

        institution_type = django_filters.MultipleChoiceFilter(
            name='profile__type',
            label='Institution Type',
            # choices=InstitutionProfile.TYPE_CHOICES,
            choices = [(i, dict(InstitutionProfile.TYPE_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('type', flat=True).distinct()],
            widget=forms.CheckboxSelectMultiple,
        )

        instcat = django_filters.MultipleChoiceFilter(
            name='profile__instcat',
            label='Institution Category',
            # choices=InstitutionProfile.INSTCAT_CHOICES,
            choices = [(i, dict(InstitutionProfile.INSTCAT_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('instcat', flat=True).distinct()],
            widget=forms.CheckboxSelectMultiple,
        )

        carnegie = django_filters.MultipleChoiceFilter(
            name='profile__carnegie',
            label='Carnegie Classification (U.S. Only)',
            # choices=InstitutionProfile.CARNEGIE_CHOICES,
            choices = [(i, dict(InstitutionProfile.CARNEGIE_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('carnegie', flat=True).distinct()],
            widget=forms.CheckboxSelectMultiple,
        )

        congressional_district = django_filters.ChoiceFilter(
            name='profile__congressional_district',
            label='Congressional District (U.S. Only)',
            # choices=InstitutionProfile.CONGRESSIONAL_DISTRICT_CHOICES,
            choices = [(i, dict(InstitutionProfile.CONGRESSIONAL_DISTRICT_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('congressional_district', flat=True).distinct()],

        )

        system_source_id = django_filters.ChoiceFilter(
            name='profile__system_source_id',
            label='University System',
            # choices=InstitutionProfile.SYSTEM_SOURCE_ID_CHOICES,
            choices = [(i, dict(InstitutionProfile.SYSTEM_SOURCE_ID_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('system_source_id', flat=True).distinct()],
        )

        level = django_filters.MultipleChoiceFilter(
            name='profile__level',
            label='Institution level',
            choices=InstitutionProfile.LEVEL_CHOICES,
            # choices = [(i, dict(InstitutionProfile.LEVEL_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('size', flat=True).distinct()],
            widget=forms.CheckboxSelectMultiple,
        )

        control = django_filters.MultipleChoiceFilter(
            name='profile__control',
            label='Institution control',
            choices=InstitutionProfile.CONTROL_CHOICES,
            # choices = [(i, dict(InstitutionProfile.CONTROL_CHOICES).get(i)) for i in InstitutionProfile.objects.filter(reviewed=True).values_list('size', flat=True).distinct()],
            widget=forms.CheckboxSelectMultiple,
        )
    except ProgrammingError as e:
        print('Silencing exception during initial migration when database tables do not yet exist, e.g. during the first docker-compose up or manage.py migrate.')
    except Exception as e:
        print(e.__class__.__name__)
        raise

    class Meta:
        model = Institution
        fields = ['id',]

    """
        # #todo -- 'sparc_member' ---- YES PLEASE! :D
        # #todo -- profile.main_url vs. profile.institution_website
    """

    # @property
    def qs(self):
        parent = super(InstitutionFilter, self).qs
        return parent.filter(profile__reviewed=True).order_by("name")
        # return parent.filter(is_published=True) \
        # | parent.filter(author=self.request.user)

class ProgramFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='name', lookup_expr='icontains', label='Program Name contains')
    institution_id = django_filters.CharFilter(name='institution__id')
    institution_name = django_filters.CharFilter(name='institution__name')

    program_type = django_filters.MultipleChoiceFilter(
        name='type',
        label='Type of Program',
        choices=Program.TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    home = django_filters.MultipleChoiceFilter(
        label='Home Within Institution',
        choices=Program.HOME_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    funding_source = CustomProgramFundingSourceFilter(
        label='Funding Source',
        choices=Program.FUNDING_SOURCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    # #todo -- Program Focus [primary] -- *** calculated field ***
    # #todo -- Program Annual Budget [funding_annual] -- JG: correct name = funding_total -- *** integer ***

    financial_sustainability = django_filters.MultipleChoiceFilter(
        label='Financial Sustainability',
        choices=Program.FINANCIAL_SUSTAINABILITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    incentives = CustomProgramIncentivesFilter(
        label='Incentives Offered',
        choices=Program.INCENTIVES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    incentives_conditions = django_filters.MultipleChoiceFilter(
        label='Incentive Conditions',
        choices=Program.INCENTIVES_CONDITIONS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    # FYI: `funding_total = django_filters.RangeFilter()` also works but specifying
    # funding_min & funding_max enables more granular control , e.g. manual HTML
    # rendering of individual fields, custom names of URL parameters (i.e.
    # funding_min & funding_max instead of funding_total_0 & funding_total_1)
    funding_min = django_filters.NumberFilter(lookup_expr='gte', name='funding_total')
    funding_max = django_filters.NumberFilter(lookup_expr='lte', name='funding_total')

    class Meta:
        model = Program
        fields = ['id']

    def qs(self):
        parent = super(ProgramFilter, self).qs
        return parent.filter(reviewed=True).order_by("name")


class PolicyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='name', lookup_expr='icontains', label='Policy Name contains')

    policy_type = django_filters.ChoiceFilter(
        name='policy_type',
        label='Type of Policy',
        choices=Policy.POLICY_TYPE_CHOICES,
        # DOES NOT WORK: widget=forms.CheckboxSelectMultiple,
    )

    policy_level = django_filters.ChoiceFilter(
        name='policy_level',
        label='Level',
        choices=Policy.POLICY_LEVEL_CHOICES,
        # DOES NOT WORK: widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Policy
        fields = ['id']

    def qs(self):
        parent = super(PolicyFilter, self).qs
        return parent.filter(reviewed=True).order_by("name")

class EventFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='name', lookup_expr='icontains', label='Event Name contains')

    event_type = CustomEventTypeFilter(
        name='type',
        label='Type of Event',
        choices=Event.TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Event
        fields = ['id']

    def qs(self):
        parent = super(EventFilter, self).qs
        return parent.filter(reviewed=True).order_by("name")

class ResourceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='name', lookup_expr='icontains', label='Resource Name contains')
    resource_type = CustomResourceTypeFilter( # django_filters.ChoiceFilter(
        name='type',
        label='Type of Resource',
        choices=Resource.TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    audience = CustomResourceAudienceFilter(
        label='Intended Audience',
        choices=Resource.AUDIENCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Resource
        fields = ['id']

    def qs(self):
        parent = super(ResourceFilter, self).qs
        return parent.filter(reviewed=True).order_by("name")

class AbstractFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='institution__name', lookup_expr='icontains', label='Institution Name contains')

    language = CustomAbstractLanguageFilter(
        label='Language',
        choices=Abstract.LANGUAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Abstract
        fields = ['id']

    def qs(self):
        parent = super(AbstractFilter, self).qs
        return parent.filter(reviewed=True).order_by("name")
