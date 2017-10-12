from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        regex=r'^login/(?P<login_uuid>[0-9a-z-]+)/$',
        view=views.UUIDLogin.as_view(),
        name='login',
    ),
    url(
        regex=r'institutions/$',
        view=views.UserDetailView.as_view(),
        name='detail',
    ),
]
