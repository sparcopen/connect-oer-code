from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _

from .models import User


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(User)
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
        ('User Profile', {'fields': ('name', 'login_url')}),
    ) + AuthUserAdmin.fieldsets
    readonly_fields = ['login_url']
    list_display = ['username', 'login_url', 'is_superuser']
    search_fields = ['username', 'name']

    def login_url(self, obj):
        return reverse('users:login', kwargs={'login_uuid': obj.login_uuid})

    def response_change(self, request, obj):
        if 'change_uuid' in request.POST:
            obj.change_uuid()

            msg = _('The login uuid was successfully changed.')
            self.message_user(request, msg, messages.SUCCESS)

            opts = self.model._meta
            redirect_url = reverse(
                'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                args=(obj._get_pk_val(),),
                current_app=self.admin_site.name
            )

            return HttpResponseRedirect(redirect_url)

        return super().response_change(request, obj)
