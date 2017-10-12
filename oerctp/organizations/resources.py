from import_export import resources, fields
from .models import AnnualImpactReport, Abstract, Institution, InstitutionProfile, Program, Policy, Event, Resource, Tag

class AnnualImpactReportResource(resources.ModelResource):
    class Meta:
        model = AnnualImpactReport
        # fields = 'one two three four'.split()
        # exclude = ('something',)
        # export_order = ('three','two','one',)

    def get_queryset(self):
        return self._meta.model.objects.order_by('id') # sort


class AbstractResource(resources.ModelResource):
    class Meta:
        model = Abstract

    def get_queryset(self):
        return self._meta.model.objects.order_by('id') # sort


class InstitutionResource(resources.ModelResource):
    class Meta:
        model = Institution

    def get_queryset(self):
        return self._meta.model.objects.exclude(profile__filled_in_by__isnull=True).exclude(profile__filled_in_by='').order_by('id') # sort


class InstitutionProfileResource(resources.ModelResource):

    subject_engagement_list = fields.Field(attribute='subject_engagement_directorypage')

    class Meta:
        model = InstitutionProfile
        export_fields = 'id access_uuid updated_at created_at reviewed hidden filled_in_by acknowledgments institution_website institution_twitter twitter_image_displayed twitter_image_url poc_name poc_job poc_email poc_twitter poc_url poc_visibility overview_raw campus_engagement library_engagement subject_engagement subject_engagement_list url_oer url_libguide taskforce staff staff_location catalog oer_included oerdegree_offered source_data source_id sparc_member address city state_province zip country main_url enrollment level control highest_degree carnegie type size location_type system_source_id congressional_district longitude latitude instcat notes private_comments'.strip().split()
        fields = export_fields
        export_order = export_fields

    def get_queryset(self):
        return self._meta.model.objects.exclude(filled_in_by__isnull=True).exclude(filled_in_by='').order_by('id') # sort


class ProgramResource(resources.ModelResource):
    class Meta:
        model = Program

    def get_queryset(self):
        return self._meta.model.objects.order_by('id') # sort


class PolicyResource(resources.ModelResource):
    class Meta:
        model = Policy

    def get_queryset(self):
        return self._meta.model.objects.order_by('id') # sort


class EventResource(resources.ModelResource):
    class Meta:
        model = Event

    def get_queryset(self):
        return self._meta.model.objects.order_by('id') # sort


class ResourceResource(resources.ModelResource):
    class Meta:
        model = Resource

    def get_queryset(self):
        return self._meta.model.objects.order_by('id') # sort


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag

    def get_queryset(self):
        return self._meta.model.objects.order_by('id') # sort
