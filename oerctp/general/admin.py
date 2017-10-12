from django.contrib import admin

from taggit.models import Tag


admin.site.unregister(Tag)
