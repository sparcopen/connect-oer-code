from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404, redirect, reverse
from django.http import Http404

from .models import Event, Institution, Policy, Program, Resource, Tag


class GetInstitutionMixin:
    def get_object(self):
        try:
            return self.model.objects.get(id=self.kwargs.get('uuid_or_slug'))
        except (ValueError, self.model.DoesNotExist):
            pass

        return get_object_or_404(self.model, slug=self.kwargs.get('uuid_or_slug'))


class DirectoryHomepageView(ListView):
    # model = Institution  # same as `queryset = Institution.objects.all()`
    queryset = Institution.objects.filter(profile__filled_in_by__isnull=False).exclude(profile__filled_in_by__exact='').exclude(profile__hidden=True).exclude(profile__reviewed=False).order_by('name' )
    # # if more complex logic is required:
    # from django.db.models import Q
    # queryset = Institution.objects.exclude(Q(profile__reviewed=True) | Q(something__else=''))
    context_object_name = 'institutions_on_homepage'
    template_name = 'organizations/public/directory_homepage.html'


class InstitutionView(GetInstitutionMixin, DetailView):
    model = Institution
    template_name = 'organizations/public/institution.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.slug and obj.slug != kwargs.get('uuid_or_slug'):
            url = reverse('institution_public', kwargs={'uuid_or_slug': obj.slug})
            return redirect(url)

        return super().dispatch(request, *args, **kwargs)


class InstitutionAbstractView(GetInstitutionMixin, DetailView):
    model = Institution
    template_name = 'organizations/public/institution_abstract.html'

    def get_object(self):
        institution = super().get_object()

        for lang in institution.additional_languages.all():
            if lang.slug == self.kwargs.get('lang'):
                return lang
        raise Http404

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.institution.slug and obj.institution.slug != kwargs.get('uuid_or_slug'):
            url = reverse('institution_public_abstract',
                          kwargs={'uuid_or_slug': obj.institution.slug, 'lang': obj.slug})
            return redirect(url)

        return super().dispatch(request, *args, **kwargs)


class TagView(DetailView):
    model = Tag
    template_name = 'organizations/public/tag.html'

    def get_context_data(self, **kwargs):
        slug = self.kwargs.get('slug')
        context = super().get_context_data(**kwargs)

        context['institutions'] = Institution.objects.filter(_tags_raw__slug=slug)
        context['programs'] = Program.objects.filter(_tags_raw__slug=slug)
        context['policies'] = Policy.objects.filter(_tags_raw__slug=slug)
        context['events'] = Event.objects.filter(_tags_raw__slug=slug)
        context['resources'] = Resource.objects.filter(_tags_raw__slug=slug)
        return context
