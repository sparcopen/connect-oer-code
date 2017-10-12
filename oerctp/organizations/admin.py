from django.contrib import admin
from django.contrib.sites.models import Site
from django.shortcuts import reverse

from .models import (AnnualImpactReport, Event, Abstract,
                     Institution, InstitutionProfile, Policy, Program, Resource,
                     Tag, AccessLink)

from .admin_forms import (AbstractAdminForm, TagMembershipAdminForm, PolicyAdminForm, ProgramAdminForm,
                          InstitutionProfileAdminForm, EventAdminForm, ResourceAdminForm, TagAdminForm,
                          TagSystemAdminForm, TagGeneralAdminForm, TagPersonAdminForm, TagProjectAdminForm)

from .utils import export_as_csv_action, create_modeladmin


class CustomAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'access_uuid', 'updated_at', 'created_at']

    def displayed_admin(self, obj):
        return obj.displayed
    displayed_admin.boolean = True
    displayed_admin.short_description = "Will this be shown?"

    def save_model(self, request, obj, form, change):
        return obj.save(user=request.user)


# see https://docs.djangoproject.com/en/1.10/ref/contrib/admin/
class ProfileFilledOutListFilter(admin.SimpleListFilter):
    title = ('profile filled out')
    parameter_name = 'filled_out'

    def lookups(self, request, model_admin):
        return (
            ('1', ('Yes')),
            ('0', ('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(acknowledgments=False)
        if self.value() == '1':
            return queryset.filter(acknowledgments=True)


class ProfileDisplayedListFilter(admin.SimpleListFilter):
    title = ('showability status')
    parameter_name = 'displayable'

    def lookups(self, request, model_admin):
        return (
            ('1', ('Yes')),
            ('0', ('No')),
        )

    def queryset(self, request, queryset):
        # must use "hidden" (not "displayed") because properties aren't supported
        if self.value() == '0':
            return queryset.filter(hidden=True)
        if self.value() == '1':
            return queryset.filter(hidden=False)


@admin.register(AnnualImpactReport)
class AnnualImpactReportAdmin(CustomAdmin):
    list_display = ['institution', 'year', 'reviewed', 'displayed_admin']
    list_filter = ['year', 'reviewed', ProfileDisplayedListFilter]
    search_fields = ['institution__name']


@admin.register(Event)
class EventAdmin(CustomAdmin):
    list_display = ['name', 'institution', 'reviewed', 'displayed_admin']
    search_fields = ['name', 'institution__name']
    list_filter = ['type', 'reviewed', ProfileDisplayedListFilter]
    form = EventAdminForm


@admin.register(Abstract)
class AbstractAdmin(CustomAdmin):
    list_display = ['institution', 'name', 'reviewed', 'displayed_admin']
    search_fields = ['abstract_raw', 'institution__name']
    list_filter = ['language', 'reviewed', ProfileDisplayedListFilter]
    form = AbstractAdminForm


@admin.register(Institution)
class InstitutionAdmin(CustomAdmin):
    exclude = ['reviewed', 'hidden']  # #todo -- consider removing these fields completely from the model, not just from the admin (we're using "reviewed" and "hidden" at the institutional profile level, having them duplicated in the institution model would be confusing)
    list_display = ['name', 'profile']
    search_fields = ['name', 'profile__institution_website']
    readonly_fields = ['students_impacted_total', 'id']
    ordering = ('name',)
    list_per_page = 200


@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(CustomAdmin):

    list_display = ['institution', 'institution_website', 'reviewed', 'displayed_admin', 'twitter_image_displayed']
    list_filter = ['reviewed', ProfileDisplayedListFilter, 'twitter_image_displayed', ProfileFilledOutListFilter]
    search_fields = ['institution__name','institution_website']
    form = InstitutionProfileAdminForm
    ordering = ('institution__name',)
    list_per_page = 200


class InstitutionProfilePOCAdmin(InstitutionProfileAdmin):
    def get_queryset(self, request):
        return self.model.objects.exclude(poc_name__isnull=True)
    def name_admin(self, obj):
        return obj.institution.name

    list_display = ['name_admin', 'poc_name', 'poc_job', 'poc_email', 'poc_twitter', 'poc_url']
    # #todo -- while 'name_admin' and 'institution' hold the same value, export will work with 'institution' but not with 'name_admin' (possible solution: use of django-import-export app, currently untested) -- see also: https://web.archive.org/web/20170417165123/https://stackoverflow.com/questions/26618420/django-why-cant-i-access-dynamically-generated-attributes-in-classes-in-my-mo
    list_export = ['institution', 'poc_name', 'poc_job', 'poc_email', 'poc_twitter', 'poc_url']
    list_filter = []  # turn off filtering to save screen space
    actions = [export_as_csv_action(fields=list_export)]
    list_per_page = 10000  # why show them all? to make export easier...


create_modeladmin(InstitutionProfilePOCAdmin, model=InstitutionProfile, name='institutionprofile-poc', custom_verbose_plural='institutional profiles: points of contact')


class InstitutionAccesLinkAdmin(InstitutionAdmin):
    def get_queryset(self, request):
        self.request = request  # expose "request": make it possible to access the request object outside of this function, i.e. in "access_link_full_admin" (to check if request is secure / served via https)
        return self.model.objects.all()

    def source_id_admin(self, obj):
        return obj.profile.source_id

    def access_link_full_admin(self, obj):
        protocol = 'https://' if self.request.is_secure() else 'http://'
        return protocol + Site.objects.get_current().domain + reverse('institution', kwargs={'uuid': obj.access_uuid})
        # or "domain": `request.META.HTTP_HOST` -- or: `"{0}://{1}{2}".format(request.scheme, request.get_host(), request.path)`

    list_display = ['name', 'source_id_admin', 'access_link_full_admin']
    list_export =  ['name', 'access_uuid'] # refuses to export 'access_link_full_admin'
    actions = [export_as_csv_action(fields=list_export)]
    list_per_page = 10000  # why show them all? to make export easier...

create_modeladmin(InstitutionAccesLinkAdmin, model=Institution, name='institution-accesslink', custom_verbose_plural='institutions: access links')


@admin.register(Policy)
class PolicyAdmin(CustomAdmin):
    list_display = ['name', 'institution', 'reviewed', 'displayed_admin']
    list_filter = ['reviewed', ProfileDisplayedListFilter]
    form = PolicyAdminForm


@admin.register(Program)
class ProgramAdmin(CustomAdmin):
    list_display = ['name', 'institution', 'reviewed', 'displayed_admin']
    search_fields = ['name']
    list_filter = ['reviewed', ProfileDisplayedListFilter]
    form = ProgramAdminForm


@admin.register(Resource)
class ResourceAdmin(CustomAdmin):
    list_display = ['name', 'institution', 'reviewed', 'displayed_admin']
    search_fields = ['name']
    list_filter = ['reviewed', ProfileDisplayedListFilter]
    form = ResourceAdminForm


@admin.register(Tag)
class TagAdmin(CustomAdmin):
    list_display = ['name', 'slug', 'type', 'created_at']
    search_fields = ['name', 'slug', 'description']
    list_filter = ['type']

    def get_readonly_fields(self, request, obj=None):
        """ Disable slug modification after the slug is saved """
        fields = super().get_readonly_fields(request)
        if obj:
            return fields + ['slug']
        return fields

    def get_prepopulated_fields(self, request, obj=None):
        """ Prepopulate the slug when creating a new object """
        if not obj:
            return {'slug': ['name']}
        return {}

    def get_form(self, request, obj=None, **kwargs):
        """ Get the form according to tag type """
        if obj is None:
            return TagAdminForm

        if obj.type == Tag.TYPE_MEMBERSHIP:
            return TagMembershipAdminForm
        elif obj.type == Tag.TYPE_PROJECT:
            return TagProjectAdminForm
        elif obj.type == Tag.TYPE_PERSON:
            return TagPersonAdminForm
        elif obj.type == Tag.TYPE_SYSTEM:
            return TagSystemAdminForm
        elif obj.type == Tag.TYPE_GENERAL:
            return TagGeneralAdminForm

        return super().get_form(request, obj, **kwargs)


@admin.register(AccessLink)
class AccessLinkAdmin(CustomAdmin):
    list_display = ['institution', 'type', 'created_at']
    list_filter = ['type']
    search_fields = ['institution__name', 'text_raw']

    def get_fields(self, request, obj=None):
        """Get all fields but reviewed/hidden"""
        return super().get_fields(request, obj)[2:]

admin.site.site_header = 'Connect OER Admin'
admin.site.site_title = 'Connect OER Admin'
admin.site.index_title = 'Home'
