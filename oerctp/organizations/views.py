import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import DetailView, UpdateView, View, FormView, TemplateView, ListView

from .forms import (
    InstitutionProfileForm, EventForm, ProgramForm, PolicyForm, ResourceForm, AnnualImpactReportForm, AbstractForm,
    EditAccessLinkForm
)
from .models import (
    Institution, InstitutionProfile, Event, Program, Policy, Resource, AnnualImpactReport,
    Abstract, AccessLink
)

from .resources import AnnualImpactReportResource, AbstractResource, InstitutionResource, InstitutionProfileResource, ProgramResource, PolicyResource, EventResource, ResourceResource, TagResource

# #todo -- there is a lot of repetition with "form_valid": if texts remain the same for all templates, consider cleaning up (create a mixin)


logger = logging.getLogger(__name__)


class ObjectGetterMixin:
    def get_object(self):
        try:
            return self.model.objects.get(access_uuid=self.kwargs.get('uuid'))
        except (self.model.DoesNotExist, ValueError) as e:
            raise Http404(e)


class SaveFormWithUserMixin:
    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class FormGetterMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_template_path'] = self.form_template_path
        return context


class InstitutionView(ObjectGetterMixin, SaveFormWithUserMixin, DetailView):
    model = Institution
    template_name = 'organizations/edit/institution.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['activities'] = []
        context['activities'] += list(self.object.event_set.all())
        context['activities'] += list(self.object.program_set.all())
        context['activities'] += list(self.object.policy_set.all())
        context['activities'] += list(self.object.resource_set.all())

        self.object.profile.name = 'Institutional Profile'
        context['profile_table'] = [self.object.profile]

        return context


class InstitutionProfileView(ObjectGetterMixin, FormGetterMixin, SaveFormWithUserMixin, UpdateView):
    model = InstitutionProfile
    template_name = 'organizations/edit/form.html'
    form_class = InstitutionProfileForm
    form_template_path = 'organizations/edit/form_profile.html'

    def form_valid(self, form):
        messages.success(self.request, '<h4>Confirmation</h4><p>Thanks for submitting this form! Your information has been forwarded to a member of our team for review, and will appear on your institution’s public directory page soon.</p><p>If you have administrative access for your institution, you can close this window. If you were sent a one-time access link to complete this form, please make note of the following permanent link, which will give you access to update the form in the future:</p><p><strong><a id="injectlink" href=""></a><script type="text/javascript">document.getElementById("injectlink").innerHTML=window.location.href;document.getElementById("injectlink").setAttribute("href",window.location.href);</script></strong></p><p>For further information, see our <a href="https://sparcopen.org/our-work/connect-oer/faq">FAQ</a>.</p>')
        return super().form_valid(form)

class AddActivityView(ObjectGetterMixin, DetailView):
    model = Institution
    template_name = 'organizations/edit/institution_add_activity.html'


class ActivityEventView(ObjectGetterMixin, FormGetterMixin, SaveFormWithUserMixin, UpdateView):
    model = Event
    template_name = 'organizations/edit/form.html'
    form_class = EventForm
    form_template_path = 'organizations/edit/form_event.html'

    def form_valid(self, form):
        messages.success(self.request, '<h4>Confirmation</h4><p>Thanks for submitting this form! Your information has been forwarded to a member of our team for review, and will appear on your institution’s public directory page soon.</p><p>If you have administrative access for your institution, you can close this window. If you were sent a one-time access link to complete this form, please make note of the following permanent link, which will give you access to update the form in the future:</p><p><strong><a id="injectlink" href=""></a><script type="text/javascript">document.getElementById("injectlink").innerHTML=window.location.href;document.getElementById("injectlink").setAttribute("href",window.location.href);</script></strong></p><p>For further information, see our <a href="https://sparcopen.org/our-work/connect-oer/faq">FAQ</a>.</p>')
        return super().form_valid(form)


class ActivityProgramView(ObjectGetterMixin, FormGetterMixin, SaveFormWithUserMixin, UpdateView):
    model = Program
    template_name = 'organizations/edit/form.html'
    form_class = ProgramForm
    form_template_path = 'organizations/edit/form_program.html'

    def form_valid(self, form):
        messages.success(self.request, '<h4>Confirmation</h4><p>Thanks for submitting this form! Your information has been forwarded to a member of our team for review, and will appear on your institution’s public directory page soon.</p><p>If you have administrative access for your institution, you can close this window. If you were sent a one-time access link to complete this form, please make note of the following permanent link, which will give you access to update the form in the future:</p><p><strong><a id="injectlink" href=""></a><script type="text/javascript">document.getElementById("injectlink").innerHTML=window.location.href;document.getElementById("injectlink").setAttribute("href",window.location.href);</script></strong></p><p>For further information, see our <a href="https://sparcopen.org/our-work/connect-oer/faq">FAQ</a>.</p>')
        return super().form_valid(form)


class ActivityPolicyView(ObjectGetterMixin, FormGetterMixin, SaveFormWithUserMixin, UpdateView):
    model = Policy
    template_name = 'organizations/edit/form.html'
    form_class = PolicyForm
    form_template_path = 'organizations/edit/form_policy.html'

    def form_valid(self, form):
        messages.success(self.request, '<h4>Confirmation</h4><p>Thanks for submitting this form! Your information has been forwarded to a member of our team for review, and will appear on your institution’s public directory page soon.</p><p>If you have administrative access for your institution, you can close this window. If you were sent a one-time access link to complete this form, please make note of the following permanent link, which will give you access to update the form in the future:</p><p><strong><a id="injectlink" href=""></a><script type="text/javascript">document.getElementById("injectlink").innerHTML=window.location.href;document.getElementById("injectlink").setAttribute("href",window.location.href);</script></strong></p><p>For further information, see our <a href="https://sparcopen.org/our-work/connect-oer/faq">FAQ</a>.</p>')
        return super().form_valid(form)


class ActivityResourceView(ObjectGetterMixin, FormGetterMixin, SaveFormWithUserMixin, UpdateView):
    model = Resource
    template_name = 'organizations/edit/form.html'
    form_class = ResourceForm
    form_template_path = 'organizations/edit/form_resource.html'

    def form_valid(self, form):
        messages.success(self.request, '<h4>Confirmation</h4><p>Thanks for submitting this form! Your information has been forwarded to a member of our team for review, and will appear on your institution’s public directory page soon.</p><p>If you have administrative access for your institution, you can close this window. If you were sent a one-time access link to complete this form, please make note of the following permanent link, which will give you access to update the form in the future:</p><p><strong><a id="injectlink" href=""></a><script type="text/javascript">document.getElementById("injectlink").innerHTML=window.location.href;document.getElementById("injectlink").setAttribute("href",window.location.href);</script></strong></p><p>For further information, see our <a href="https://sparcopen.org/our-work/connect-oer/faq">FAQ</a>.</p>')
        return super().form_valid(form)


class AnnualImpactReportView(ObjectGetterMixin, FormGetterMixin, SaveFormWithUserMixin, UpdateView):
    model = AnnualImpactReport
    template_name = 'organizations/edit/form.html'
    form_class = AnnualImpactReportForm
    form_template_path = 'organizations/edit/form_impact.html'

    def post(self, request, *args, **kwargs):
        """Validate the form, if the model has *unique_together* do additional validation as well"""
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        is_valid = form.is_valid()
        reports = AnnualImpactReport.objects.filter(
            institution=self.object.institution,
            year=form.cleaned_data['year'],
        )
        if reports.exists() and reports[0] != form.instance:
            is_valid = False
            form.add_error('year', 'This year for this institution has already been filled out!')

        if is_valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, '<h4>Confirmation</h4><p>Thanks for submitting this form! Your information has been forwarded to a member of our team for review, and will appear on your institution’s public directory page soon.</p><p>If you have administrative access for your institution, you can close this window. If you were sent a one-time access link to complete this form, please make note of the following permanent link, which will give you access to update the form in the future:</p><p><strong><pre>' + self.request.build_absolute_uri() + '</pre><a href="' + self.request.build_absolute_uri() + '"></strong></p><p>For further information, see our <a href="https://sparcopen.org/our-work/connect-oer/faq">FAQ</a>.</p>')
        return super().form_valid(form)


class LanguageView(ObjectGetterMixin, FormGetterMixin, SaveFormWithUserMixin, UpdateView):
    model = Abstract
    template_name = 'organizations/edit/form.html'
    form_class = AbstractForm
    # #todo -- check if form_template_path works properly
    form_template_path = 'organizations/edit/form_language.html'

    def post(self, request, *args, **kwargs):
        """Validate the form, if the model has *unique_together* do additional validation as well"""
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        is_valid = form.is_valid()
        languages = Abstract.objects.filter(
            institution=self.object.institution,
            language=form.cleaned_data['language'],
        )
        if languages.exists() and languages[0] != form.instance:
            is_valid = False
            form.add_error('language', 'A narrative in this langauge already exists. Please select a different language or edit the existing narrative.')

        if is_valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, '<h4>Confirmation</h4><p>Thanks for submitting this form! Your information has been forwarded to a member of our team for review, and will appear on your institution’s public directory page soon.</p><p>If you have administrative access for your institution, you can close this window. If you were sent a one-time access link to complete this form, please make note of the following permanent link, which will give you access to update the form in the future:</p><p><strong><pre>' + self.request.build_absolute_uri() + '</pre><a href="' + self.request.build_absolute_uri() + '"></strong></p><p>For further information, see our <a href="https://sparcopen.org/our-work/connect-oer/faq">FAQ</a>.</p>')
        """This message appears after the 2nd (second) submission and all subsequent submissions."""
        return super().form_valid(form)


class HideUnhideView(View):
    def post(self, request, *args, **kwargs):
        data = dict(request.POST)

        redirect_response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        try:
            from django.apps import apps
            model = apps.get_model(app_label='organizations', model_name=data['model'][0])
        except (KeyError, LookupError):
            logger.exception('An error occurred')
            messages.error(request, 'An error occurred, we logged it and we will try to fix it ASAP.')
            return redirect_response

        try:
            object = model.objects.get(id=data.get('id')[0])
        except (model.DoesNotExists, ValueError):
            messages.error(request, 'Object not found!')
            return redirect_response

        object.hidden = data.get('status', [''])[0] == 'hide'
        object.save()

        msg = 'The object you selected is now hidden from the Connect OER directory. Click "unhide" to make it visible.' if object.hidden else 'This object is now visible in the Connect OER directory. Click "hide" to hide it again. Note that recent changes may not appear until they are reviewed.'
        messages.success(request, msg)

        return redirect_response


class AccessLinkView(ObjectGetterMixin, DetailView):
    model = Institution
    template_name = 'organizations/edit/access_link.html'

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('type') not in dict(AccessLink.TYPE_CHOICES):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['access_link'] = AccessLink.objects.create(
            institution=self.object,
            type=self.kwargs.get('type')
        )

        return context


class EditAccessLinkView(ObjectGetterMixin, UpdateView):
    model = AccessLink
    form_class = EditAccessLinkForm
    template_name = 'organizations/edit/form.html'

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class AccessLinkListView(ObjectGetterMixin, ListView):
    model = Institution
    template_name = 'organizations/edit/access_link_list.html'

    def get_queryset(self):
        obj = self.get_object()
        return obj.accesslink_set.all()

    def post(self, request, *args, **kwargs):
        to_delete = dict(request.POST).get('_selected_items', [])
        messages.success(request, 'Access links successfully deleted!')
        AccessLink.objects.filter(id__in=to_delete).delete()
        return self.get(request, *args, **kwargs)


class AccessFormView(ObjectGetterMixin, FormGetterMixin, DetailView, FormView):
    model = AccessLink
    template_name = 'organizations/edit/access.html'
    form_template_path = None  # template is assigned in get_form_class

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            view = TemplateView.as_view(template_name='organizations/edit/link_not_found.html')
            return view(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        """Get the right form according to *type* from access link object"""
        self.object = self.get_object()

        if self.object.type == AccessLink.IMPACT_REPORT:
            self.form_template_path = 'organizations/edit/form_impact.html'
            return AnnualImpactReportForm

        if self.object.type == AccessLink.LANGUAGE:
            self.form_template_path = 'organizations/edit/form_language.html'
            return AbstractForm

        if self.object.type == AccessLink.PROFILE:
            self.form_template_path = 'organizations/edit/form_profile.html'
            return InstitutionProfileForm

        if self.object.type == AccessLink.PROGRAM:
            self.form_template_path = 'organizations/edit/form_program.html'
            return ProgramForm

        if self.object.type == AccessLink.POLICY:
            self.form_template_path = 'organizations/edit/form_policy.html'
            return PolicyForm

        if self.object.type == AccessLink.EVENT:
            self.form_template_path = 'organizations/edit/form_event.html'
            return EventForm

        if self.object.type == AccessLink.RESOURCE:
            self.form_template_path = 'organizations/edit/form_resource.html'
            return ResourceForm

        raise Http404('No form class found for this type of link!')

    def form_valid(self, form):
        """Save the object and delete the access link"""
        obj = form.save(commit=False)
        obj.institution = self.object.institution
        obj.save()

        self.object.delete()

        return HttpResponseRedirect(obj.get_absolute_url())

    def post(self, request, *args, **kwargs):
        """Validate the form, if the model has *unique_together* do additional validation as well"""
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        is_valid = form.is_valid()

        model = type(form.save(commit=False)) if is_valid else None

        if model is Abstract:
            if Abstract.objects.filter(
                institution=self.object.institution,
                language=form.cleaned_data['language'],
            ).exists():
                is_valid = False
                form.add_error('language', 'This language for this institution was already filled out!')
        elif model is AnnualImpactReport:
            if AnnualImpactReport.objects.filter(
                institution=self.object.institution,
                year=form.cleaned_data['year'],
            ).exists():
                is_valid = False
                form.add_error('year', 'This year for this institution was already filled out!')

        if is_valid:
            """This message appears after the 1st submission ONLY (i.e., when an access link is used for the first time)."""
            messages.success(request, '<h4>Confirmation</h4><p>Thanks for submitting this form! Your information has been forwarded to a member of our team for review, and will appear on your institution’s public directory page soon.</p><p>If you have administrative access for your institution, you can close this window. If you were sent a one-time access link to complete this form, please make note of the following permanent link, which will give you access to update the form in the future:</p><p><strong><a id="injectlink" href=""></a><script type="text/javascript">document.getElementById("injectlink").innerHTML=window.location.href;document.getElementById("injectlink").setAttribute("href",window.location.href);</script></strong></p><p>For further information, see our <a href="https://sparcopen.org/our-work/connect-oer/faq">FAQ</a>.</p>')

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ReviewView(LoginRequiredMixin, SaveFormWithUserMixin, UpdateView):

    def get_review_metadata(self):
        """Return model, form and template_name as a tuple for reviewed object"""
        type_ = self.kwargs.get('type', '')

        try:
            from django.apps import apps
            model = apps.get_model(app_label='organizations', model_name=type_)
        except LookupError:
            logger.exception('An error occurred')
            raise Http404

        from .forms import ReviewProgramForm, ReviewInstitutionProfileForm, ReviewEventForm
        from .forms import ReviewPolicyForm, ReviewResourceForm, ReviewAnnualImpactReportForm
        from .forms import AbstractForm

        if type_ == 'Program':
            form = ReviewProgramForm
            template_name = 'organizations/edit/review_program.html'
        elif type_ == 'Event':
            form = ReviewEventForm
            template_name = 'organizations/edit/review_todo.html'  # todo: create template
        elif type_ == 'Policy':
            form = ReviewPolicyForm
            template_name = 'organizations/edit/review_todo.html'  # todo: create template
        elif type_ == 'Resource':
            form = ReviewResourceForm
            template_name = 'organizations/edit/review_todo.html'  # todo: create template
        elif type_ == 'InstitutionProfile':
            form = ReviewInstitutionProfileForm
            template_name = 'organizations/edit/review_todo.html'  # todo: create template
        elif type_ == 'AnnualImpactReport':
            form = ReviewAnnualImpactReportForm
            template_name = 'organizations/edit/review_todo.html'  # todo: create template
        elif type_ == 'Abstract':
            form = AbstractForm
            template_name = 'organizations/edit/review_todo.html'  # todo: create template
        else:
            raise Http404('Improperly configured type!')

        return model, form, template_name

    def get_success_url(self):
        return self.object.institution.get_absolute_url()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_review():
            raise Http404

        self.model, self.form_class, self.template_name = self.get_review_metadata()
        return super().dispatch(request, *args, **kwargs)


class AnnualImpactReportExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = AnnualImpactReportResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_impactreports.csv'
        return response


class AbstractExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = AbstractResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_abstracts.csv'
        return response


class InstitutionExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = InstitutionResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_institutions.csv'
        return response


class InstitutionProfileExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = InstitutionProfileResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_institutionprofiles.csv'
        return response


class ProgramExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = ProgramResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_programs.csv'
        return response


class PolicyExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = PolicyResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_policies.csv'
        return response


class EventExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = EventResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_events.csv'
        return response


class ResourceExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = ResourceResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_resources.csv'
        return response


class TagExportView(View):

    def get(self, request, *args, **kwargs ):
        dataset = TagResource().export()
        response = HttpResponse(dataset.csv, content_type='csv')
        response['Content-Disposition'] = 'attachment; filename=connect_tags.csv'
        return response
