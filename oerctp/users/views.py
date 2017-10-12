from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DetailView, View

from .models import User


class UUIDLogin(View):
    def get(self, request, *args, **kwargs):
        login_uuid = kwargs.get('login_uuid')

        try:
            user = User.objects.get(login_uuid=login_uuid)
        except (User.DoesNotExist, ValueError):
            raise Http404('Invalid login uuid!')

        login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
        redirect_url = reverse(settings.LOGIN_REDIRECT_URL)
        return HttpResponseRedirect(redirect_url)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User

    def get_object(self, queryset=None):
        return self.request.user
