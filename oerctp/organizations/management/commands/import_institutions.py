import csv

from django.core.management.base import BaseCommand

from oerctp.organizations.models import InstitutionProfile, Institution


class Command(BaseCommand):
    help = 'Load data'

    def handle(self, *args, **options):

        # source data: https://docs.google.com/spreadsheets/d/12q8xpaGKaKpfieLQ4DIm8wOSyAL36S9benNtPStfvdQ/edit
        with open('data/institutions.csv') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(reader)  # skip csv file header (because the first line contains field names)

            for i, row in enumerate(reader):
                profile, created = InstitutionProfile.objects.get_or_create(source_id=row[0])

                profile_source_id = row[0]
                profile_name = row[1] # display_name
                # profile_name2 = row[2] # official_name

                profile_sparc_member_raw = row[3]
                profile_sparc_member = {'Yes': True, 'SPARC': True, 'No': False}.get(profile_sparc_member_raw.strip(), False) # default is False

                profile_address = row[4]
                profile_city = row[5]
                profile_state_province = row[6]
                profile_country = row[7]
                profile_zip = row[8]
                profile_main_url = row[9]
                profile_level = row[10]
                profile_control = row[11]
                profile_highest_degree = row[12]
                profile_carnegie = row[13]
                profile_location_type = row[14]
                profile_size = row[15]
                profile_system_source_id = row[16]
                profile_congressional_district = row[17]
                profile_longitude = row[18]
                profile_latitude = row[19]

                profile_enrollment_raw = row[20]
                if profile_enrollment_raw.isdigit():
                    profile_enrollment = profile_enrollment_raw
                else:
                    profile_enrollment = None

                profile_type = row[21]
                profile_source_data = row[22]
                profile_instcat = row[23]

                profile_institution_website = profile_main_url # row[9]

                # #todo -- clean up (rewrite): instead of explicitly listing all element *twice* when using "if", iterate over a single list of fields in both locations

                if created:
                    profile.source_id = profile_source_id
                    profile.name = profile_name
                    # profile.name2 = profile_name2
                    profile.sparc_member = profile_sparc_member
                    profile.address = profile_address
                    profile.city = profile_city
                    profile.state_province = profile_state_province
                    profile.country = profile_country
                    profile.zip = profile_zip
                    profile.main_url = profile_main_url
                    profile.level = profile_level
                    profile.control = profile_control
                    profile.highest_degree = profile_highest_degree
                    profile.carnegie = profile_carnegie
                    profile.location_type = profile_location_type
                    profile.size = profile_size
                    profile.system_source_id = profile_system_source_id
                    profile.congressional_district = profile_congressional_district
                    profile.longitude = profile_longitude
                    profile.latitude = profile_latitude
                    profile.enrollment = profile_enrollment
                    profile.type = profile_type
                    profile.source_data = profile_source_data
                    profile.instcat = profile_instcat
                    profile.institution_website = profile_institution_website
                    profile.save()

                    obj = Institution(name=row[1], profile=profile)
                    obj.save()

                # if data exists, use "update" instead of "save" to avoid post_save trigger
                # (save triggers clearing profile moderated status, so updating data would otherwise force moderation)
                else:
                    obj = InstitutionProfile.objects.filter(source_id=profile_source_id)
                    # DOES NOT EXIST: obj.update(name = profile_name)
                    # obj.update(name2 = profile_name2)
                    obj.update(sparc_member = profile_sparc_member)
                    obj.update(address = profile_address)
                    obj.update(city = profile_city)
                    obj.update(state_province = profile_state_province)
                    obj.update(country = profile_country)
                    obj.update(zip = profile_zip)
                    obj.update(main_url = profile_main_url)
                    obj.update(level = profile_level)
                    obj.update(control = profile_control)
                    obj.update(highest_degree = profile_highest_degree)
                    obj.update(carnegie = profile_carnegie)
                    obj.update(location_type = profile_location_type)
                    obj.update(size = profile_size)
                    obj.update(system_source_id = profile_system_source_id)
                    obj.update(congressional_district = profile_congressional_district)
                    obj.update(longitude = profile_longitude)
                    obj.update(latitude = profile_latitude)
                    obj.update(enrollment = profile_enrollment)
                    obj.update(type = profile_type)
                    obj.update(source_data = profile_source_data)
                    obj.update(instcat = profile_instcat)
                    obj.update(institution_website = profile_institution_website)

                self.stdout.write('{} saved.'.format(profile.institution_website))
