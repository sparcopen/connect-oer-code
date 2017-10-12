from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

from . import views, views_public
from .filters import InstitutionFilter, ProgramFilter, PolicyFilter, EventFilter, ResourceFilter, AbstractFilter

from django_filters.views import FilterView


urlpatterns = [
    url(r'^edit/hide-unhide/$', views.HideUnhideView.as_view(), name='hide_unhide'),
    url(r'^edit/(?P<uuid>[^/]+)/$', views.InstitutionView.as_view(), name='institution'),
    url(r'^edit/(?P<pk>[^/]+)/review/(?P<type>[^/]+)/$', views.ReviewView.as_view(), name='review'),
    url(r'^edit/(?P<uuid>[^/]+)/access-links/$', views.AccessLinkListView.as_view(), name='access_links'),
    url(r'^edit/(?P<uuid>[^/]+)/profile/$', views.InstitutionProfileView.as_view(), name='profile'),
    url(r'^edit/(?P<uuid>[^/]+)/activity/program/$', views.ActivityProgramView.as_view(), name='activity_program'),
    url(r'^edit/(?P<uuid>[^/]+)/activity/policy/$', views.ActivityPolicyView.as_view(), name='activity_policy'),
    url(r'^edit/(?P<uuid>[^/]+)/activity/event/$', views.ActivityEventView.as_view(), name='activity_event'),
    url(r'^edit/(?P<uuid>[^/]+)/activity/resource/$', views.ActivityResourceView.as_view(), name='activity_resource'),
    url(r'^edit/(?P<uuid>[^/]+)/new_activity/$', views.AddActivityView.as_view(), name='new_activity'),
    url(r'^edit/(?P<uuid>[^/]+)/language/$', views.LanguageView.as_view(), name='language'),
    url(r'^edit/(?P<uuid>[^/]+)/impact-report/$', views.AnnualImpactReportView.as_view(), name='impact_report'),
    url(r'^edit/(?P<uuid>[^/]+)/add-link/(?P<type>[^/]+)/$', views.AccessLinkView.as_view(), name='add_access'),
    url(r'^edit/(?P<uuid>[^/]+)/link/$', views.AccessFormView.as_view(), name='access'),
    url(r'^edit/(?P<uuid>[^/]+)/link/edit/$', views.EditAccessLinkView.as_view(), name='access_edit'),

    # url(r'^directory/$', views_public.DirectoryHomepageView.as_view(), name='directory_homepage'),
    url(r'^directory/$', FilterView.as_view(filterset_class=InstitutionFilter, template_name='filter/institution_filter.html'), name='filter_institutions'),
    url(r'^directory/(?P<uuid_or_slug>[^/]+)/$', views_public.InstitutionView.as_view(), name='institution_public'),
    url(r'^directory/(?P<uuid_or_slug>[^/]+)/(?P<lang>[^/]+)/$', views_public.InstitutionAbstractView.as_view(),
        name='institution_public_abstract'),
    url(r'^filter/institutions/$', RedirectView.as_view(pattern_name='filter_institutions', permanent=False), name='directory_homepage'),
    url(r'^filter/programs/$', FilterView.as_view(filterset_class=ProgramFilter, template_name='filter/program_filter.html'), name='filter_programs'),
    url(r'^filter/policies/$', FilterView.as_view(filterset_class=PolicyFilter, template_name='filter/policy_filter.html'), name='filter_policies'),
    url(r'^filter/events/$', FilterView.as_view(filterset_class=EventFilter, template_name='filter/event_filter.html'), name='filter_events'),
    url(r'^filter/resources/$', FilterView.as_view(filterset_class=ResourceFilter, template_name='filter/resource_filter.html'), name='filter_resources'),
    url(r'^filter/abstracts/$', FilterView.as_view(filterset_class=AbstractFilter, template_name='filter/abstract_filter.html'), name='filter_abstracts'),
    url(r'^tag/(?P<slug>[^/]+)/$', views_public.TagView.as_view(), name='tag'),

    # for regular download URLs: use login_required
    url(r'^export/impactreports/$', login_required(views.AnnualImpactReportExportView.as_view()), name='export_impactreports'),
    url(r'^export/abstracts/$', login_required(views.AbstractExportView.as_view()), name='export_abstracts'),
    url(r'^export/institutions/$', login_required(views.InstitutionExportView.as_view()), name='export_institutions'),
    url(r'^export/institutionprofiles/$', login_required(views.InstitutionProfileExportView.as_view()), name='export_institutionprofiles'),
    url(r'^export/programs/$', login_required(views.ProgramExportView.as_view()), name='export_programs'),
    url(r'^export/policies/$', login_required(views.PolicyExportView.as_view()), name='export_policies'),
    url(r'^export/events/$', login_required(views.EventExportView.as_view()), name='export_events'),
    url(r'^export/resources/$', login_required(views.ResourceExportView.as_view()), name='export_resources'),
    url(r'^export/tags/$', login_required(views.TagExportView.as_view()), name='export_tags'),
]
