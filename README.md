# Connect OER

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)](https://github.com/pydanny/cookiecutter-django/)

## Installation

This application is using `docker-compose`. The examples below are for the development version of the app using the development version: `dev.yml`.

### Getting your computer ready

- Data is stored in a local directory which is linked to the application. This directory needs to exist first. On a Mac, you need to do the following (otherwise you'll see the error message `Mounts denied: The paths (...) are not shared from OS X and are not known to Docker.`):

```
sudo mkdir -p /srv/docker
sudo chown `whoami`:staff /srv/docker
mkdir -p /srv/docker/oerctp
```

Then in Docker (for Mac) Preferences under File Sharing, add `/srv/docker` to shared paths.

Once done, make sure `./config/settings/.env` exists and has correct settings. Use `env.example` found in this repository as a template for your `.env` file.

### Setting up the application

- After you clone the repository, **initialize the database** (this will be needed to follow the steps below):

  `docker-compose -f dev.yml run django python manage.py migrate`

### Creating users

- To create a **superuser account** (this is required to log in to the administrative area), use the following command:

  `docker-compose -f dev.yml run django python manage.py createsuperuser`

- To create a **normal user account**, go to the Admin interface (log in as `admin`) and click on `Users` and then `Add User`.

TIP: you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Importing initial data

When the database existst (`python manage.py migrate`), the superuser exists (`python manage.py createsuperuser`), you may import initial data to work with (`python manage.py import_institutions`).

### Running the development server

Once everything has been set up, run the development server. Note that since `docker` is being used, `python manage.py runserver` will *not* be used. Instead, execute the following command to bring up all the docker containers:

`docker-compose -f dev.yml up`

At this point, you can open your web browser and navigate to `http://localhost:9112`. To access the administrative area, go to `http://localhost:9112/admin`.

### Setting up the site

The first thing you should do in the admin is to go to "Sites" and make sure that there is exactly one site with the correct "domain name" (e.g. `connect.sparcopen.org`) and human-friendly description (e.g. "Connect OER").

## Working with the application

### Finding access links ("secret links" for librarians)

Log in to the Admin interface at `<your-server>/admin`, e.g. `http://localhost:9112/admin` or `https://connect.sparcopen.org/admin` (`https://connecttest.sparcopen.org/admin`).

After you log in, you'll see the Django Administration page. Click `Institutions` to display the management interface for institutions. In the search box, type the name of the institution you want to find and either hit `Enter` or click on the search icon. On the results page, click the desired institution to edit it. In the edit view, you'll see the `View on Site` button in the upper right corner, just below the Django Admin header. Click on it to display the Institutions's main editing page. This is the same page that the librarians for the institutions will use. To share the link to this page, just click in the browser's address bar, copy the URL and share with the librarian.

### Finding profile links

Log in to the Admin (see above). Click `Institutions` and then choose a profile (click on one or find one using the full text search). Look for the `id` field on the profile detail page (use CTRL-F in browser if convenient). It is a long hexadecimal number containing four dahses (hyphens), called a UUID. You will see the same  string in the URL of the currently displayed institution. Go to `<your-server>/directory/<uuid>/`, e.g. `http://localhost:9112/directory/12345678-90ab-cdef-ba09-87654321`. You will see the profile of the institution, as long as it's not set as hidden (the default is "not hidden") and as long as it has been reviewed (which you need to do manually through `Institutional Profiles` in the Admin, for each institution).

### Finding out which profiles are in the database

Log in to the Admin (see above). Click `Institutional Profiles` (you will see all profiles for all the institutions, even ones that never used the app) and notice the filters on the right hand side. Filter for only those profiles that have been filled out.

You may wonder: but why do we even have institutional profiles that are empty? The reason: the profiles you see in the admin are not entirely empty but contain pre-filled data from open data sources, such as the address, enrollment information, ad so on.

### Displaying submitted profiles on the site

After you display the list of only those profiles that have been filled out (see above), notice the checkboxes showing you the moderation status. Some profiles will have a red "X" under "reviewed". This means that they have not been approved to be displayed live on the site. To change that, open that profile, check the "reviewed" box and hit save button at the bottom. Notice that red "X" has now been changed to a green checkmark, meaning that unless you also set the "hidden" attribute (which has been designed for more permanent blacklisting that even librarians cannot override), this profile will now be available live on the site.

### Exporting institutional POC

Institutional POCs can be displayed through the admin interface (`Institutional profiles: points of contact`). It is also possible to export their contact information in CSV. To do so, select the desired contacts (or check the topmost checkbox to "select all"), choose "Export selected objects as CSV file" from the "Action" drop-down menu and click the "Go" button.

### Adding custom URLs for institutions

Every institution has an identifier which is used for URLs (e.g. in the directory). This is a long string (UUID4) and may look unwieldy. For this reason, it is possible to customize "slugs" for institutions which will be used in URLs instead. So instead of `/directory/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/` the URL may look like `/directory/mit/`. To customize the URL, visit the Admin, click Institutions, choose an institution and edit the "slug" field.

### Backing up and restoring data

Example workflow (run this from project root):

```
COMPOSE_FILE='dev.yml'
# first, make sure that nobody has live access to the database
docker-compose -f ${COMPOSE_FILE} stop
# bring up the DB server temporarily, do a current backup (just in case), list backups to restore from
docker-compose -f ${COMPOSE_FILE} up postgres &
sleep 10s
docker-compose -f ${COMPOSE_FILE} exec postgres backup && \
docker-compose -f ${COMPOSE_FILE} exec postgres list-backups ; \
echo ; \
echo '***now run this:***' ; \
echo 'docker-compose -f ${COMPOSE_FILE} exec postgres restore *FILENAME_FROM_BACKUPS_LIST*' ; \
echo 'docker-compose -f ${COMPOSE_FILE} stop postgres' ; \
echo
```

Restore the latest version:

```
LATEST_BACKUP=`docker-compose -f ${COMPOSE_FILE} exec postgres list-backups | grep backup_ | grep ".sql.gz" | sort --reverse | head -n 1 | tr -dc '[[:print:]]'`
docker-compose -f ${COMPOSE_FILE} exec postgres restore "${LATEST_BACKUP}"
```

### Cleaning up old access links

Execute `docker-compose -f dev.yml run django python manage.py delete_access_links` (note that we need to use `docker-compose run`, not `docker-compose exec`, which was used in the case of backups). In production this command should be scheduled for periodic execution by cron.

### Moving from dev environment to production

Before migration:

```
docker-compose -f dev.yml stop django
docker-compose -f dev.yml up postgres &
docker-compose -f dev.yml exec postgres backup
docker-compose -f dev.yml stop
```

Verify that the container is no longer running: `docker ps`.

Copy the latest backup (which was just created) from `/srv/docker/oerctp/postgres_backup_dev` to `/srv/docker/oerctp/postgres_backup`.

Perform the migration (also back up existing docker image before removing it, just in case -- no need to backup postgres image, we use "vanilla" Postgres):

```
docker system prune --force
docker save oerctp_django | bzip2 > oerctp_django.tar.bz2
docker rmi oerctp_postgres
docker rmi oerctp_django
# we DO NOT need to do `docker rmi oerctp_redis`
# there is no custom redis image either in dev or production
```

Before moving on, make sure `config/settings/.env` file exists and contains correct information. Pay extra attention to setting `DJANGO_ADMIN_URL=^admin/` (production Gunicorn will not run without this) and `DJANGO_SETTINGS_MODULE=config.settings.production`.

Once `.env` file has been set up properly, complete the migration:

```
docker-compose stop postgres
# do a clean restore: make sure postgres data has been removed
rm -rf /srv/docker/oerctp/postgres_data/*
docker-compose up postgres &
docker-compose exec postgres list-backups
docker-compose exec postgres restore <backup_filename.sql.gz>
docker-compose build
docker-compose up
```

### Using the shell

First, run the shell: `docker-compose -f dev.yml run django python manage.py shell`. You will then be able to access the application objects from the command line, like this:

```
from oerctp.organizations.models import Institution

for i in Institution.objects.all():
    print(i)

for i in Institution.objects.filter(name__icontains='stanford'):
    p = i.program_set.all().first()
    print(p.name)

for i in Institution.objects.exclude(profile__poc_name__isnull=True):
    print (i.profile.poc_name)
```

To learn more, visit Django's [excellent documentation](https://docs.djangoproject.com/en/1.10/ref/models/querysets/).

### Deleting stale content types

Did you experiment during development and now Django is complaining about stale content types? Run `docker-compose -f dev.yml run django python manage.py migrate` and answer "yes", confirming you really want to delete this data.

### Understanding how the data is exported

For all exported CSVs *except* `connect_institutionprofiles.csv`, there is an `institution` field which points to the ID field in `connect_institutions.csv` (it is in UUID format). For institutional profiles, this relationship works in the opposite direction, which may be counter-intuitive: in `connect_institutions.csv`, there is a `profile` field which points to the ID field in `connect_institutionprofile.csv`.

### Troubleshooting

**Q**: Help! My app won't start and `docker-compose up` only shows `django_1 | Postgres is unavailable - sleeping` in an infinite loop. What to do?<br>
**A**: Run command `service docker restart` and then try `docker-compose up` again.
