# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    login_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username

    def change_uuid(self):
        self.login_uuid = uuid.uuid4()
        self.save()

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def can_review(self):
        return self.groups.filter(name__in=['Trusted User', 'SPARC Staff']).exists() or self.is_superuser
