from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from oerctp.organizations.models import AccessLink


class Command(BaseCommand):
    help = 'Removes access links older than 7 days.'

    def handle(self, *args, **options):
        deadline = timezone.now() - timedelta(days=7)
        links = AccessLink.objects.filter(created_at__lte=deadline)

        self.stdout.write('{} access links are going to be deleted!'.format(links.count()))
        links.delete()
        self.stdout.write(self.style.SUCCESS('Access links successfully deleted!'))
