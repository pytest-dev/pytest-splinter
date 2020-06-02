"""django_sample_project URL Configuration."""
from django.contrib import admin
try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

urlpatterns = [
    url('^admin/', admin.site.urls),
]
