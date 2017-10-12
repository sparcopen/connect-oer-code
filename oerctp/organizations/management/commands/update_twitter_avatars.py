import json
from urllib.request import urlopen

from django.core.management.base import BaseCommand

from oerctp.organizations.models import InstitutionProfile

class Command(BaseCommand):
    help = 'Updates URLs for Twitter Avatars where missing.'

    def handle(self, *args, **options):

        for profile in InstitutionProfile.objects.filter(institution_twitter__isnull=False):

            prefix = 'https://'  # all URLs should start with this
            suffix = '#twitter_username=' + profile.institution_twitter_username  # all URLs should end with this -- but why bother? -- avatar URLs don't contain usernames, so if an institution changed its Twitter handle, we would otherwise have no way of knowing what username their avatar URL refers to

            if not (profile.twitter_image_url.startswith(prefix) and profile.twitter_image_url.endswith(suffix)):
            # if True:  # force updates of all images, including those already present
                try:
                    twitter_response_str = urlopen('https://twitter.com/' + profile.institution_twitter_username).read().decode('utf-8')
                    # find "data-resolved-url-large" and extract string between two quotation marks that follow it
                    avatar_url=twitter_response_str.split('data-resolved-url-large')[1].split('"')[1]
                    urlopen('https://web.archive.org/save/' + avatar_url)
                    wayback_response = urlopen('https://archive.org/wayback/available?url=' + avatar_url)
                    wayback_json = json.loads(wayback_response.read().decode('utf-8'))
                    latest_snapshot = wayback_json['archived_snapshots']['closest']['url']
                    latest_snapshot_fixed = latest_snapshot.replace('http://', 'https://')
                    latest_snapshot_fixed += suffix
                    # FYI: "profile.save()" triggers save signal which means the institutional profile will need to be moderated (which may seem confusing to the users) -- to avoid sending the signal and therefore triggering the moderation, use a workaround from https://web.archive.org/web/20170503084040/https://stackoverflow.com/questions/1555060/how-to-save-a-model-without-sending-a-signal (update queryset directly)
                    # profile.twitter_image_url = latest_snapshot_fixed
                    # profile.save()
                    InstitutionProfile.objects.filter(id=profile.id).update(twitter_image_url = latest_snapshot_fixed)
                    print('Avatar updated for ' + str(profile))
                except:
                    print('Updating Twitter Avatar failed for ' + str(profile))
