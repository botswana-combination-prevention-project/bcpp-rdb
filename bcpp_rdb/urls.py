from django.conf import settings
from django.views import static
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView
from django_crypto_fields.admin import crypto_fields_admin

from edc_base.views import LoginView, LogoutView

from .views import HomeView

urlpatterns = [
    url(r'^update-csv-file/(?P<task_name>.*)/$', HomeView.as_view(), name='update-csv-file'),
    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'login', LoginView.as_view(), name='login_url'),
    url(r'logout', LogoutView.as_view(pattern_name='login_url'), name='logout_url'),
    url(r'^edc/', include('edc_base.urls')),
    url(r'^admin/$', RedirectView.as_view(pattern_name='home_url')),
    url(r'^admin/', crypto_fields_admin.urls),
    url(r'^admin/', admin.site.urls),
    url(r'^home/', HomeView.as_view(), name='home_url'),
    url(r'^', HomeView.as_view(), name='home_url'),
]
