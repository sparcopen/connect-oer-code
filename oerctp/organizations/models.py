import ast
import uuid
import markdown

from django.db import models
from django.shortcuts import reverse
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from django.core.validators import MinValueValidator, MaxLengthValidator

from django.contrib.humanize.templatetags.humanize import intcomma

from .validators import none_validator, twitter_handle_validator, MinChoicesValidator, \
    MaxChoicesValidator, no_validator, date_year_validator, ack_checked_validator, \
    na_validator, notsure_unknown_validator, unknown_validator


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    pass


class ModelMixinManager(models.Model):
    def active(self):
        return self.get_queryset().filter(reviewed=True, hidden=False)

    def to_review(self, user=None):
        queryset = self.get_queryset().filter(reviewed=False)
        if user:  # todo: test it!
            queryset = queryset.filter(institution__editors=user)

        return queryset


class ModelMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    access_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    reviewed = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    @property
    def displayed(self):
        return not self.hidden

    filled_in_by = models.EmailField(
        verbose_name='Your Email Address',
        help_text='Please enter your e-mail address, so we have a record of who has filled out this form. '
                  'Please provide your institutional (.edu) account, if available. Email addresses will be '
                  'treated according to the SPARC Privacy Policy.',
        null=True,
    )

    acknowledgments = models.BooleanField(
        verbose_name='Acknowledgments',
        help_text='By checking the box below, you acknowledge that the data entered in this form (EXCEPT email '
                  'addresses and where otherwise noted) will be published as Open Data under a Creative Commons '
                  'Zero 1.0 Public Domain Dedication. E-mail addresses and other private information will be '
                  'treated according to the SPARC Privacy Policy available at http://sparcopen.org/privacy-policy. '
                  'You also agree that you have the requisite approvals from your institution to share any '
                  'information, content or data you have shared. You also acknowledge that data submitted through '
                  'this form may be edited for clarity and to conform with guidelines, and will be displayed on the '
                  'SPARC website according to SPARC’s discretion. You may return to this form to edit your responses '
                  'at any time.',
        default=False,
        validators=[ack_checked_validator],
    )

    objects = ModelMixinManager()

    def reset_access_uuid(self):
        self.access_uuid = uuid.uuid4()
        self.save()

    def save(self, *args, **kwargs):
        """Save object. If it was saved by a an admin, SPARC staff or a trusted user review is not necessary."""

        user = kwargs.pop('user', None)
        if user is None or not (user.groups.filter(name__in=['Trusted User', 'SPARC Staff']).exists() or user.is_superuser):
            self.reviewed = False

        super().save(*args, **kwargs)

    class Meta:
        abstract = True

    def class_name(self):
        return self.__class__.__name__


class TagMixin(models.Model):
    _tags_raw = TaggableManager(through='UUIDTaggedItem', blank=True)

    @property
    def tags(self):
        tags = list(self._tags_raw.all().all().values_list('slug', flat=True))
        return Tag.objects.filter(slug__in=tags).order_by('type', 'name')

    class Meta:
        abstract = True


class AnnualImpactReport(ModelMixin, models.Model):
    institution = models.ForeignKey('Institution', related_name='annual_reports')

    YEAR_CHOICES = (
        ('ay2018', '2017-2018'),
        ('ay2017', '2016-2017'),
        ('ay2016', '2015-2016'),
        ('ay2015', '2014-2015'),
        ('ay2014', '2013-2014'),
        ('ay2013', '2012-2013'),
        ('ay2012', '2011-2012'),
        ('ay2011', '2010-2011'),
        ('ay2010', '2009-2010'),
        ('ay2009', '2008-2009'),
        ('ay2008', '2007-2008'),
    )

    year = models.CharField(
        verbose_name='Academic Year',
        help_text='Please select the academic year of this report.',
        max_length=6,
        choices=YEAR_CHOICES,
    )

    impact_students = models.IntegerField(
        verbose_name='Students Using OER',
        help_text='Please provide the number of student enrollments in courses that used OER in place of traditional '
                  'textbooks during the Academic Year indicated above. Please see our FAQ for a full explanation of what to include and what not to include.',
        validators=[MinValueValidator(0)],
    )

    impact_faculty = models.IntegerField(
        verbose_name='Faculty Using OER',
        help_text='Please provide the number of faculty that used OER in place of traditional textbooks during the '
                  'Academic Year indicated above. Please count each faculty member only once per academic year. '
                  'This is optional.',
        blank=True, null=True,
        validators=[MinValueValidator(0)],
    )

    impact_courses = models.IntegerField(
        verbose_name='Courses Using OER',
        help_text='Please provide the number of courses that used OER in place of traditional textbooks in at least '
                  'one section during the Academic Year indicated above. Please count each course only once per '
                  'academic year, regardless of the number of sections or semesters taught. This is optional.',
        blank=True, null=True,
        validators=[MinValueValidator(0)],
    )

    public_notes = models.TextField(
        verbose_name='Description of Methodology',
        help_text='Please use this space to explain to readers how you calculated the numbers above, including any relevant links. This is optional, but at least a brief explanation is encouraged.',
        blank=True, null=True,
        validators=[MaxLengthValidator(3000)],
    )

    private_notes = models.TextField(
        verbose_name='Private Notes (Not Published)',
        help_text='Please use this field for any additional notes about how you calculated the numbers in this section. '
                  'This information may be useful to you and others who come back to update this form in the future. '
                  'This field is private and for your use only, and will not be shared publicly.',
        blank=True, null=True,
        validators=[MaxLengthValidator(30000)],
    )

    AWARENESS_CHOICES = (
        ('10', '10 (Highest)'),
        ('9', '9'),
        ('8', '8'),
        ('7', '7'),
        ('6', '6'),
        ('5', '5'),
        ('4', '4'),
        ('3', '3'),
        ('2', '2'),
        ('1', '1 (Lowest)'),
        ('unknown', 'Not sure'),
    )

    awareness_rating_admin = models.CharField(
        verbose_name='Administration',
        choices=AWARENESS_CHOICES,
        max_length=10,
    )
    awareness_rating_faculty = models.CharField(
        verbose_name='Faculty',
        choices=AWARENESS_CHOICES,
        max_length=10,
    )
    awareness_rating_library = models.CharField(
        verbose_name='Library',
        choices=AWARENESS_CHOICES,
        max_length=10,
    )
    awareness_rating_students = models.CharField(
        verbose_name='Students',
        choices=AWARENESS_CHOICES,
        max_length=10,
    )

    private_comments = models.TextField(
        verbose_name='Private Comments',
        help_text='Please use this space for any additional comments you would like to add.',
        blank=True, null=True,
        validators=[MaxLengthValidator(3000)],
    )

    @property
    def name(self):
        return self.year

    def __str__(self):
        year = dict(self.YEAR_CHOICES)[self.year]
        return 'Report for year {year} for {institution}'.format(year=year, institution=self.institution)

    class Meta:
        unique_together = [('institution', 'year')]

    def get_absolute_url(self):
        return reverse('impact_report', kwargs={'uuid': self.access_uuid})


from django.core.validators import MinLengthValidator, MaxLengthValidator


class Abstract(ModelMixin, models.Model):
    institution = models.ForeignKey('Institution', related_name='additional_languages')

    abstract_raw = models.TextField(
        verbose_name='Abstract',
        validators=[MinLengthValidator(300), MaxLengthValidator(3000)],
    )

    LANGUAGE_CHOICES = (
        ('ak', 'Akan'),
        ('am', 'Amharic'),
        ('ar', 'Arabic'),
        ('as', 'Assamese'),
        ('az', 'Azerbaijani'),
        ('be', 'Belarusian'),
        ('bn', 'Bengali'),
        ('my', 'Burmese'),
        ('km', 'Central Khmer'),
        ('ny', 'Chichewa; Chewa; Nyanja'),
        ('zh', 'Chinese'),
        ('hr', 'Croatian'),
        ('cs', 'Czech'),
        ('nl', 'Dutch; Flemish'),
        ('fr', 'French'),
        ('ff', 'Fulah'),
        ('de', 'German'),
        ('el', 'Greek, Modern (1453-)'),
        ('gu', 'Gujarati'),
        ('ht', 'Haitian; Haitian Creole'),
        ('ha', 'Hausa'),
        ('hi', 'Hindi'),
        ('hu', 'Hungarian'),
        ('ig', 'Igbo'),
        ('it', 'Italian'),
        ('ja', 'Japanese'),
        ('jv', 'Javanese'),
        ('kn', 'Kannada'),
        ('kk', 'Kazakh'),
        ('rw', 'Kinyarwanda'),
        ('ko', 'Korean'),
        ('ku', 'Kurdish'),
        ('mg', 'Malagasy'),
        ('ms', 'Malay'),
        ('ml', 'Malayalam'),
        ('mr', 'Marathi'),
        ('ne', 'Nepali'),
        ('or', 'Oriya'),
        ('om', 'Oromo'),
        ('pa', 'Panjabi; Punjabi'),
        ('fa', 'Persian'),
        ('pl', 'Polish'),
        ('pt', 'Portuguese'),
        ('ps', 'Pushto; Pashto'),
        ('qu', 'Quechua'),
        ('ro', 'Romanian; Moldavian; Moldovan'),
        ('ru', 'Russian'),
        ('sr', 'Serbian'),
        ('sn', 'Shona'),
        ('sd', 'Sindhi'),
        ('si', 'Sinhala; Sinhalese'),
        ('so', 'Somali'),
        ('es', 'Spanish; Castilian'),
        ('su', 'Sundanese'),
        ('sv', 'Swedish'),
        ('tl', 'Tagalog'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('th', 'Thai'),
        ('tr', 'Turkish'),
        ('tk', 'Turkmen'),
        ('ug', 'Uighur; Uyghur'),
        ('uk', 'Ukrainian'),
        ('ur', 'Urdu'),
        ('uz', 'Uzbek'),
        ('vi', 'Vietnamese'),
        ('xh', 'Xhosa'),
        ('yo', 'Yoruba'),
        ('zu', 'Zulu'),
        ('other', 'Other, please specify'),
    )

    language = models.CharField(
        max_length=100,
        # DO NOT include "choices" (because we're displaying a custom multifield)
    )

    private_comments = models.TextField(
        verbose_name='Private Comments',
        help_text='Please use this space for any additional comments you would like to add.',
        blank=True, null=True,
        validators=[MaxLengthValidator(3000)],
    )

    @property
    def abstract(self):
        return self.abstract_raw
        # return markdown.markdown(self.abstract_raw)

    @property
    def name(self):
        """Language of the text. This method is created just for code consistency"""
        try:
            import ast
            lang = ast.literal_eval(self.language)
            if lang[0] == 'other':
                return lang[1]
            return dict(self.LANGUAGE_CHOICES)[lang[0]]
        except (ValueError, KeyError):
            return 'Unknown language'

    @property
    def slug(self):
        from django.utils.text import slugify
        return slugify(self.name)

    def __str__(self):
        return 'Abstract for {institution} in {lang}'.format(institution=self.institution, lang=self.name)

    class Meta:
        unique_together = [('institution', 'language')]

    def get_absolute_url(self):
        return reverse('language', kwargs={'uuid': self.access_uuid})


class InstitutionProfile(ModelMixin, models.Model):
    class Meta:
        verbose_name = 'institutional profile'
        verbose_name_plural = 'institutional profiles'

    institution_website = models.URLField(
        verbose_name='Institution Website',
        help_text='Please provide the URL of the official website for your institution.',
        max_length=255,
        null=True,
    )

    institution_twitter = models.CharField(
        verbose_name='Institution Twitter Account',
        help_text='Please provide the official twitter handle for your institution. Your entry must be a valid '
                  'twitter account and begin with the character “@”. The profile image associated with this account '
                  'will be displayed on your Institution’s directory page.',
        max_length=255,
        blank=True, null=True,
        validators=[twitter_handle_validator]
    )

    twitter_image_displayed = models.BooleanField(default=True)

    # store the logo URL in the database, so that we don't have to hit Twitter API during each visit to each page
    twitter_image_url = models.URLField(max_length=255, blank=True, null=True,)

    @property
    def institution_twitter_username(self):
        if self.institution_twitter.startswith('@'):
            return self.institution_twitter[1:]
        else:
            return self.institution_twitter

    @property
    def institution_twitter_url(self):
        return 'https://twitter.com/' + self.institution_twitter_username

    poc_name = models.CharField(
        verbose_name='Point of Contact',
        help_text='Please provide the name of the person who should be listed as the Point of Contact '
                  'for your Institution for the purposes of this project.',
        max_length=255,
        null=True,
    )

    poc_job = models.CharField(
        verbose_name='Point of Contact Job Title and Department',
        help_text='Please list the Point of Contact’s job title and department within the institution, if applicable.',
        max_length=255,
        null=True,
    )

    poc_email = models.EmailField(
        verbose_name='Point of Contact Email Address',
        help_text='Help Text: Please provide the institutional (.edu) account, if available. '
                  'Email addresses will be treated according to the SPARC Privacy Policy and will not be made '
                  'visible online.',
        max_length=255,
        null=True,
    )

    poc_twitter = models.CharField(
        verbose_name='Point of Contact Twitter Account',
        help_text='Please provide the twitter username of the Point of Contact, starting with “@”. If this is not '
                  'applicable, or you do not wish for it to be displayed in the directory, please leave this blank.',
        max_length=255,
        blank=True, null=True,
    )

    @property
    def poc_twitter_username(self):
        if self.poc_twitter.startswith('@'):
            return self.poc_twitter[1:]
        else:
            return self.poc_twitter

    @property
    def poc_twitter_url(self):
        return 'https://twitter.com/' + self.poc_twitter_username

    poc_url = models.URLField(
        verbose_name='Point of Contact Website',
        help_text='Please provide a link to a biography or more information about the Point of Contact. '
                  'Please ensure to include the “http” or “https” prefix, and only one link is permitted per box. '
                  'Otherwise, please leave this question blank.',
        max_length=255,
        blank=True, null=True,
    )

    POC_VISIBILITY_CHOICES=(
        ('visible', 'Yes, make my Point of Contact visible'),
        ('private', 'No, please keep my Point of Contact private'),
    )

    poc_visibility = models.CharField(
        verbose_name='Point of Contact Visibility',
        help_text='Please select below whether you would like the above information about the Point of Contact '
                  '(except for e-mail address) to be listed in your institution’s directory page and open data. '
                  'Note that the Point of Contact will still receive information about the project through '
                  'the secure contact form.',
        max_length=255,
        choices=POC_VISIBILITY_CHOICES,
        null=True,
    )

    @property
    def poc_visible(self):
        print(self.poc_visibility)
        if self.poc_visibility == "visible":
            return True
        return False

    overview_raw = models.TextField(
        verbose_name='Institutional Overview',
        help_text='Please provide a brief abstract about your institution and its efforts relating to OER. '
                  'Your abstract might address the general status of OER efforts, and any specific highlights or '
                  'prominent programs (note you will also have the chance to describe programs in detail in the '
                  'Campus Activities section). If you wish to add links or formatting to your abstract, you may do so '
                  'using markdown syntax. Please carefully test your text using a Markdown editor such as '
                  'http://markdown.pioul.fr before saving your text. Maximum 4000 characters (approx. 600 words).',
        validators=[MinLengthValidator(300), MaxLengthValidator(4000)],
        null=True,
    )

    CAMPUS_ENGAGEMENT_CHOICES = (
        ('dept', 'Academic Department'),
        ('div', 'Academic Division'),
        ('it', 'Academic/Information Technology'),
        ('alumni', 'Alumni Association'),
        ('disability', 'Assistive Technology or Disability Services Office'),
        ('store', 'Campus Store'),
        ('comms', 'Communications Office'),
        ('elearning', 'E-Learning/Distance Education'),
        ('fac_champ', 'Faculty Champions(s)'),
        ('fac_sen', 'Faculty Senate or Union'),
        ('library', 'Library'),
        ('student_grp', 'Other Student Group(s)'),
        ('admin', 'Senior Administration'),
        ('student_gov', 'Student Government'),
        ('student_serv', 'Student Services'),
        ('tlc', 'Teaching and Learning Center'),
        ('other', 'Other'),
        ('none', 'None of the Above'),
    )

    campus_engagement = models.TextField(
        verbose_name='Which of the following entities are actively engaged in efforts to '
                     'advance OER on campus?',
        help_text='Please select all that apply. You will have the '
                  'opportunity to indicate which entities are involved in specific projects under Campus Activities, '
                  'and you may return to update this information at any time.',
        validators=[none_validator],
        # DO NOT include "choices" (because we're displaying checkboxes)
        null=True,
    )

    @property
    def campus_engagement_directorypage(self):  # nomalized for displaying on the webpage
        # ast.literal_eval converts string (value saved in the database) to list
        try:
            lst = ast.literal_eval(self.campus_engagement)
            dct = dict(self.CAMPUS_ENGAGEMENT_CHOICES)
            if len(lst) == 1 and lst[0] == "other":
                return None
            if len(lst) == 1 and lst[0] == "none":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
                # print("K : " + item)
                # print("V : " + dct.get(item))
            return output
        except ValueError:
            return None

    LIBRARY_ENGAGEMENT_CHOICES = (
        ('admin', 'Administration'),
        ('collections', 'Collections & Technical Services'),
        ('reference', 'Public Service/Reference'),
        ('scholcomm', 'Scholarly Communication'),
        ('liaisons', 'Subject Liaisons'),
        ('tl', 'Teaching & Learning'),
        ('press', 'University Press'),
        ('other', 'Other'),
        ('unknown', 'Not Sure'),
        ('na', 'Not Applicable'),
    )

    library_engagement = models.TextField(
        verbose_name='If the Library is actively engaged in advancing OER, which department is leading these efforts?',
        help_text='Please select the best option. If there are multiple departments, you may select up to three.',
        validators=[MinChoicesValidator(1), MaxChoicesValidator(3), na_validator, notsure_unknown_validator],
        # DO NOT include "choices" (because we're displaying checkboxes)
        null=True,
    )

    @property
    def library_engagement_directorypage(self):
        try:
            lst = ast.literal_eval(self.library_engagement)
            dct = dict(self.LIBRARY_ENGAGEMENT_CHOICES)
            if len(lst) == 1 and lst[0] == "other":
                return None
            if len(lst) == 1 and lst[0] == "unknown":
                return None
            if len(lst) == 1 and lst[0] == "na":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
            return output
        except ValueError:
            return None

    SUBJECT_ENGAGEMENT_CHOICES = (
        ('un08', 'Agriculture, forestry, fisheries and veterinary'),
        ('un073', 'Architecture and construction'),
        ('un021', 'Arts'),
        ('un051', 'Biological and related sciences'),
        ('un041', 'Business and administration'),
        ('un0531', 'Chemistry'),
        ('un0532', 'Earth sciences'),
        ('un0311', 'Economics'),
        ('un01', 'Education'),
        ('un071', 'Engineering and engineering trades'),
        ('un052', 'Environment'),
        ('un00', 'Generic programs and qualifications'),
        ('un091', 'Health (incl. medicine, nursing)'),
        ('un0222', 'History and archaeology'),
        ('un06', 'Information and Communication Technologies (ICTs)'),
        ('un0321', 'Journalism and reporting'),
        ('un0231', 'Languages'),
        ('un042', 'Law'),
        ('un0322', 'Library, information and archival studies'),
        ('un0232', 'Literature and linguistics'),
        ('un072', 'Manufacturing and processing'),
        ('un054', 'Mathematics and statistics'),
        ('un0223', 'Philosophy and ethics'),
        ('un0533', 'Physics'),
        ('un0312', 'Political sciences and civics'),
        ('un0313', 'Psychology'),
        ('un0221', 'Religion and theology'),
        ('un10', 'Services'),
        ('un031', 'Social and behavioral sciences'),
        ('un0314', 'Sociology and cultural studies'),
        ('un092', 'Welfare (incl. social work)'),
        ('un99', 'Other'),
    )

    subject_engagement = models.TextField(
        verbose_name='In which of the following academic subjects would you consider OER to have the most traction '
                     'at your institution?',
        help_text='Please select the academic subjects where OER seems to have the most traction on campus to date, '
                  'generally speaking.',
        # DO NOT include "choices" (because we're displaying checkboxes)
        validators=[none_validator],
        null=True,
    )

    @property
    def subject_engagement_directorypage(self):
        try:
            lst = ast.literal_eval(self.subject_engagement)
            dct = dict(self.SUBJECT_ENGAGEMENT_CHOICES)
            if len(lst) == 1 and lst[0] == "other":
                return None
            if len(lst) == 1 and lst[0] == "na":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
            return output
        except ValueError:
            return None

    url_oer = models.URLField(
        verbose_name='Does your institution have a webpage dedicated to OER information and/or activities on campus?',
        help_text='If so, please enter the link in the box below. Please ensure to include the “http” or “https” '
                  'prefix, and only one link is permitted per box. Otherwise, please leave this question blank.',
        max_length=255,
        blank=True, null=True,
    )

    url_libguide = models.URLField(
        verbose_name='Does your institution have a LibGuide or other research guide dedicated to OER?',
        help_text='If so, please enter the link in the box below. Please ensure to include the “http” or “https” '
                  'prefix, and only one link is permitted per box. Otherwise, please leave this question blank.',
        max_length=255,
        blank=True, null=True,
    )

    TASKFORCE_CHOICES=(
        ('yes_1', 'Yes, with OER as the primary focus'),
        ('yes_2', 'Yes, with OER as a secondary focus'),
        ('no', 'No'),
        ('unknown', 'Not Sure'),
    )

    taskforce = models.CharField(
        verbose_name='Does your institution have a formal institution-wide task force, committee or other entity with '
                     'an OER focus?',
        help_text='If yes, you will have the opportunity to add additional information about this under '
                  'Campus Activities.',
        max_length=255,
        choices=TASKFORCE_CHOICES,
        null=True,
    )

    STAFF_CHOICES=(
        ('yes_title', 'Yes, OER is in the job title'),
        ('yes_description', 'Yes, OER is in the job description or official duties but not the job title'),
        ('no_previous', 'No, but there used to be'),
        ('no_never', 'No, never'),
        ('unknown', 'Not sure'),
    )

    staff = models.CharField(
        verbose_name='Does your institution currently have a faculty or staff position that is explicitly '
                     'dedicated to work on OER?',
        help_text='Please only answer yes if OER (or equivalent term such as “open education”) appears explicitly in '
                  'the job title, job description, or official duties. If there are multiple staff, select the first '
                  'option that applies.',
        max_length=255,
        choices=STAFF_CHOICES,
        null=True,
    )

    STAFF_LOCATION_CHOICES=(
        ('dept', 'Academic Department'),
        ('div', 'Academic Division'),
        ('it', 'Academic/Information Technology'),
        ('alumni', 'Alumni Association'),
        ('disability', 'Assistive Technology or Disability Services Office'),
        ('store', 'Campus Store'),
        ('comms', 'Communications Office'),
        ('elearning', 'E-Learning/Distance Education'),
        ('fac_champ', 'Faculty Champions(s)'),
        ('fac_sen', 'Faculty Senate or Union'),
        ('library', 'Library'),
        ('student_grp', 'Other Student Group(s)'),
        ('admin', 'Senior Administration'),
        ('student_gov', 'Student Government'),
        ('student_serv', 'Student Services'),
        ('tlc', 'Teaching and Learning Center'),
        ('other', 'Other'),
        ('none', 'None of the Above'),
    )

    staff_location = models.TextField(
        verbose_name='If yes, where is the position located within the institution?',
        help_text='Please select the option that best describes where the position is located within the institution, or select None of the Above. '
                  'If there are multiple positions, you may select additional options as appropriate.',
        # DO NOT include "choices" (because we're displaying checkboxes)
        validators=[none_validator],
        null=True,
    )

    @property
    def staff_location_directorypage(self):
        try:
            lst = ast.literal_eval(self.staff_location)
            dct = dict(self.STAFF_LOCATION_CHOICES)
            if len(lst) == 1 and lst[0] == "other":
                return None
            if len(lst) == 1 and lst[0] == "none":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
            return output
        except ValueError:
            return None

    CATALOG_CHOICES=(
        ('oer', 'OER (open course content)'),
        ('free', 'Cost-free course content, including OER'),
        ('affordable', 'Affordable course content, including cost-free course content and OER'),
        ('none', 'None of the above'),
        ('unknown', 'Not sure'),
    )

    catalog = models.TextField(
        verbose_name='Does your institution mark the Course Catalog students use for registration to indicate courses '
                     'using any of the following?',
        help_text='Please select an option. If multiple options are applicable, please select the first one that '
                  'applies.',
        # DO NOT include "choices" (because we're displaying checkboxes)
        validators=[none_validator, notsure_unknown_validator],
        null=True,
    )

    OER_INCLUDED_CHOICES = (
        ('store', 'Campus Store Policy'),
        ('design', 'Course/Curriculum Design/Redesign'),
        ('ip', 'Intellectual Property Policy'),
        ('library', 'Library Services'),
        ('fac_orientation', 'New Faculty Orientation'),
        ('stud_orientation', 'New Student Orientation'),
        ('pd', 'Professional Development'),
        ('teacher_training', 'Teacher Training Programs'),
        ('tenure', 'Tenure and Promotion Policy'),
        ('up', 'University Press/Publishing'),
        ('none', 'None of the Above'),
    )

    oer_included = models.TextField(
        verbose_name='Are mechanisms to support OER explicitly included in any of the following at your institution?',
        help_text='Please select all that apply. You will have the opportunity to add additional information about '
                  'any options you select under the Campus Activities section.',
        # DO NOT include "choices" (because we're displaying checkboxes)
        validators=[none_validator],
        null=True,
    )

    @property
    def oer_included_directorypage(self):
        try:
            lst = ast.literal_eval(self.oer_included)
            dct = dict(self.OER_INCLUDED_CHOICES)
            if len(lst) == 1 and lst[0] == "none":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
            return output
        except ValueError:
            return None

    OERDEGREE_OFFERED_CHOICES = (
        ('offering', 'An OER degree pathway is currently offered'),
        ('developing', 'An OER degree pathway is under development, but not yet currently offered'),
        ('none', 'No OER degree pathway is currently offered or under development at this time'),
        ('unknown', 'Not sure'),
    )

    oerdegree_offered = models.CharField(
        verbose_name='Does your institution offer a degree pathway that uses OER in every course?',
        help_text='Please select below if your institution offers such a degree pathway. Sometimes these are referred '
                  'to as “Z-Degree” or “Zero Textbook Cost Degree” programs.',
        choices=OERDEGREE_OFFERED_CHOICES,
        max_length=100,
        validators=[none_validator, no_validator],
        null=True,
    )

    # FYI: Additional Data Fields (not questions, but supposed to be in database)
    # Note by Nicole: These are the fields that we are planning to add into the database via Open Data from the US
    # (and hopefully Canadian) government. I've left most of the fields as optional, since we're not sure how much data
    # we can actually get from Canada.

    source_data = models.CharField(
        verbose_name='Source of Data',
        max_length=255,
        blank=True, null=True,
    )

    source_id = models.CharField(
        verbose_name='Unique ID in Data Source',
        max_length=255,
        blank=True, null=True,
    )

    sparc_member = models.NullBooleanField(default=None)

    address = models.CharField(
        verbose_name='Address',
        max_length=255,
        blank=True, null=True,
    )

    city = models.CharField(
        verbose_name='City',
        max_length=255,
        blank=True, null=True,
    )

    STATE_PROVINCE_CHOICES = (
        ('AL', 'USA: Alabama'),
        ('AK', 'USA: Alaska'),
        ('AZ', 'USA: Arizona'),
        ('AR', 'USA: Arkansas'),
        ('CA', 'USA: California'),
        ('CO', 'USA: Colorado'),
        ('CT', 'USA: Connecticut'),
        ('DC', 'USA: Washington, DC'), # added manually
        ('DE', 'USA: Delaware'),
        ('FL', 'USA: Florida'),
        ('GA', 'USA: Georgia'),
        ('HI', 'USA: Hawaii'),
        ('ID', 'USA: Idaho'),
        ('IL', 'USA: Illinois'),
        ('IN', 'USA: Indiana'),
        ('IA', 'USA: Iowa'),
        ('KS', 'USA: Kansas'),
        ('KY', 'USA: Kentucky'),
        ('LA', 'USA: Louisiana'),
        ('ME', 'USA: Maine'),
        ('MD', 'USA: Maryland'),
        ('MA', 'USA: Massachusetts'),
        ('MI', 'USA: Michigan'),
        ('MN', 'USA: Minnesota'),
        ('MS', 'USA: Mississippi'),
        ('MO', 'USA: Missouri'),
        ('MT', 'USA: Montana'),
        ('NE', 'USA: Nebraska'),
        ('NV', 'USA: Nevada'),
        ('NH', 'USA: New Hampshire'),
        ('NJ', 'USA: New Jersey'),
        ('NM', 'USA: New Mexico'),
        ('NY', 'USA: New York'),
        ('NC', 'USA: North Carolina'),
        ('ND', 'USA: North Dakota'),
        ('OH', 'USA: Ohio'),
        ('OK', 'USA: Oklahoma'),
        ('OR', 'USA: Oregon'),
        ('PA', 'USA: Pennsylvania'),
        ('RI', 'USA: Rhode Island'),
        ('SC', 'USA: South Carolina'),
        ('SD', 'USA: South Dakota'),
        ('TN', 'USA: Tennessee'),
        ('TX', 'USA: Texas'),
        ('UT', 'USA: Utah'),
        ('VT', 'USA: Vermont'),
        ('VA', 'USA: Virginia'),
        ('WA', 'USA: Washington'),
        ('WV', 'USA: West Virginia'),
        ('WI', 'USA: Wisconsin'),
        ('WY', 'USA: Wyoming'),
        ('AB', 'Canada: Alberta'),
        ('BC', 'Canada: British Columbia'),
        ('MB', 'Canada: Manitoba'),
        ('NS', 'Canada: Nova Scotia'),
        ('NT', 'Canada: Northwest Territories'),
        ('NB', 'Canada: New Brunswick'),
        ('NL', 'Canada: Newfoundland and Labrador'),
        ('NV', 'Canada: Nunavut'),
        ('ON', 'Canada: Ontario'),
        ('PE', 'Canada: Prince Edward Island'),
        ('QC', 'Canada: Quebec'),
        ('SK', 'Canada: Saskatchewan'),
        ('YK', 'Canada: Yukon'),
    )

    # #fyi -- not forcing choices here to provide maximum flexibility for import
    # (but these choices are imported from here in the filter view)

    state_province = models.CharField(
        verbose_name='State/Province',
        max_length=255,
        blank=True, null=True,
    )

    """
    @property
    def region(self):
        sp = self.state_province
        if ['fl', 'ny'] in sp:
            return 'usa-east'
        elif ['ca', 'wa'] in sp:
            return 'usa-west'
        else:
            return 'other'
    """

    zip = models.CharField(
        verbose_name='Postal Code',
        max_length=255,
        blank=True, null=True,
    )

    COUNTRY_RAW = '''
        Canada
        United States
    '''

    COUNTRY_CHOICES = [((c.strip(), c.strip())) for c in COUNTRY_RAW.strip().split('\n')]

    country = models.CharField(
        verbose_name='Country',
        max_length=255,
        null=True,
    )

    main_url = models.URLField(
        verbose_name='Website',
        max_length=255,
        blank=True, null=True,
    )

    enrollment = models.IntegerField(
        verbose_name='Enrollment',
        blank=True, null=True,
    )

    @property
    # normalized to display numbers in a more natural way ("11319" -> "11,319")
    def enrollment_normalized(self):
        if self.enrollment is not None:
            return intcomma(self.enrollment)
        return None

    LEVEL_RAW = '''
        Four or more years
        At least 2 but less than 4 years
    '''

    LEVEL_CHOICES = [((c.strip(), c.strip())) for c in LEVEL_RAW.strip().split('\n')]

    level = models.CharField(
        verbose_name='Level of Institution',
        max_length=255,
        blank=True, null=True,
    )

    CONTROL_RAW = '''
        Public
        Private not-for-profit
    '''

    CONTROL_CHOICES = [((c.strip(), c.strip())) for c in CONTROL_RAW.strip().split('\n')]

    control = models.CharField(
        verbose_name='Control of Institution',
        max_length=255,
        blank=True, null=True,
    )

    HIGHEST_DEGREE_RAW = '''
        Associate's degree
        Bachelor's degree
        Postbaccalaureate certificate
        Master's degree
        Post-master's certificate
        Doctor's degree
    '''

    HIGHEST_DEGREE_CHOICES = [((c.strip(), c.strip())) for c in HIGHEST_DEGREE_RAW.strip().split('\n')]

    highest_degree = models.CharField(
        verbose_name='Highest Degree Offered',
        max_length=255,
        blank=True, null=True,
    )

    CARNEGIE_RAW = '''
        Associates Colleges
        Baccalaureate Colleges--General
        Baccalaureate Colleges--Liberal Arts
        Baccalaureate/Associates Colleges
        Doctoral/Research Universities--Extensive
        Doctoral/Research Universities--Intensive
        Masters Colleges and Universities I
        Masters Colleges and Universities II
        Medical schools and medical centers
        Other separate health profession schools
        Other specialized institutions
        Schools of art, music, and design
        Schools of business and management
        Schools of engineering and technology
        Schools of law
        Teachers colleges
        Theological seminaries and other specialized faith-related institutions
        Tribal colleges
        No answer
    '''

    CARNEGIE_CHOICES = [((c.strip(), c.strip())) for c in CARNEGIE_RAW.strip().split('\n')]

    carnegie = models.CharField(
        verbose_name='Carnegie Classification',
        max_length=255,
        blank=True, null=True,
    )

    TYPE_RAW = '''
        Private 2-Year
        Private 4-Year
        Private 4-Year, Research University
        Public 2-Year
        Public 4-Year
        Public 4-Year, Research University
        Specialized Institution
        System Office
        Tribal College
    '''

    TYPE_CHOICES = [((c.strip(), c.strip())) for c in TYPE_RAW.strip().split('\n')]

    type = models.CharField(
        verbose_name='Institution Type',
        max_length=255,
        blank=True, null=True,
    )

    SIZE_RAW = '''
        Under 1,000
        1,000 - 4,999
        5,000 - 9,999
        10,000 - 19,999
        20,000 and above
        na
    '''

    SIZE_CHOICES = [((c.strip(), c.strip())) for c in SIZE_RAW.strip().split('\n')]

    size = models.CharField(
        verbose_name='Institution Size',
        max_length=255,
        blank=True, null=True,
    )

    LOCATION_TYPE_RAW = '''
            City: Large
            City: Midsize
            City: Small
            Suburb: Large
            Suburb: Midsize
            Suburb: Small
            Town: Distant
            Town: Fringe
            Town: Remote
            Rural: Distant
            Rural: Fringe
            Rural: Remote
    '''

    LOCATION_TYPE_CHOICES = [((c.strip(), c.strip())) for c in LOCATION_TYPE_RAW.strip().split('\n')]

    location_type = models.CharField(
        verbose_name='Institution Location Type',
        max_length=255,
        blank=True, null=True,
    )

    SYSTEM_SOURCE_ID_RAW = '''
        Alabama Community College System
        Alamo Colleges
        Arizona Board of Regents
        Arkansas State University System
        Auburn University
        Board of Regents, State of Iowa
        Broward County Public Schools
        California Community College System
        California State University
        Carolinas HealthCare System
        Chippewa-Cree Tribal Ordinance
        City Colleges of Chicago
        City University of New York
        Collier County Public School District, Florida
        Colorado Community College System
        Colorado State University System
        Community College System of New Hampshire
        Community Colleges and Workforce Development
        Connecticut State Colleges and Universities
        Connecticut Technical High School System
        Coordinating Board for Higher Education
        Delaware Technical and Community Colleges
        Downey Unified School District
        Eastern New Mexico University
        Florida State Board of Education
        Hillsborough Technical Education Centers
        Idaho State Board of Education
        Illinois Community College System
        Indiana University
        Indiana University-Purdue University
        Iowa Valley Community College District
        Joint Operating Committee of the Somerset County Technology
        Kansas State University System
        Kentucky Community and Technical College System
        Los Angeles Community College District
        Louisiana Community and Technical College System
        Louisiana State University System
        Maine Community College System
        Maricopa Community College District
        Massachusetts Community Colleges
        Mercer County Schools
        Metropolitan Community Colleges
        Minnesota State Colleges and Universities
        Mississippi Institutions of Higher Learning
        Mississippi State Board for Community and Junior Colleges
        Missouri State University
        Montana University System
        Nebraska State College System
        Nevada System of Higher Education
        New Mexico State University System
        New York State Education Department
        North Carolina Community College System
        North Dakota University System
        Ohio University
        Oklahoma Department of Career and Technology Education
        Oklahoma State System of Higher Education
        Orange County Public Schools
        Pasco County Schools
        Pennsylvania State System of Higher Education
        Puerto Rico State Department of Education
        Purdue University
        Regional University System of Oklahoma
        Rhode Island Board of Education
        Rolla Public School District
        San Bernardino Community College District
        San Mateo County Community College District
        South Carolina Commission of Higher Education
        South Carolina Technical College System
        South Dakota Board of Education
        South Dakota Board of Regents
        Southern Arkansas University System
        Southern Illinois University
        Southern University System
        St Louis Community College District
        State of New Jersey
        State University of New York System
        State University System of Florida
        Technical College System of Georgia
        Texas A&M University System
        Texas State Technical College System
        Texas State University System
        Texas Tech University System
        The Ohio State University-Main Campus
        The Pennsylvania State University
        The State University and Community College System of Tennessee
        The University of Alabama System
        The University of Louisiana System
        The University of Tennessee System
        The University of Texas System
        The University System of Ohio
        University of Alaska System of Higher Education
        University of Arkansas System
        University of California
        University of Colorado
        University of Hawaii Board of Regents
        University of Houston System
        University of Illinois Board of Trustees
        University of Maine System
        University of Massachusetts
        University of Michigan
        University of Minnesota
        University of Missouri System
        University of Nebraska
        University of New Mexico
        University of North Carolina
        University of North Texas System
        University of Pittsburgh
        University of Puerto Rico
        University of South Carolina
        University of the District of Columbia
        University of Washington
        University of Wisconsin System
        University System of Georgia
        University System of Maryland
        University System of New Hampshire
        Utah College of Applied Technology
        Utah System of Higher Education
        Vermont State Colleges
        Virginia Community College System
        Washington State Board for Community and Technical Colleges
        West Valley Mission Community College District
        West Virginia Community and Technical College System
        West Virginia Higher Education Policy Commission
        Wisconsin Technical College System
    '''

    SYSTEM_SOURCE_ID_CHOICES = [((c.strip(), c.strip())) for c in SYSTEM_SOURCE_ID_RAW.strip().split('\n')]

    system_source_id = models.CharField(
        verbose_name="Unique ID of Institution's System in the Data Source",
        max_length=255,
        blank=True, null=True,
    )

    CONGRESSIONAL_DISTRICT_RAW = '''
        AK, District 00
        AL, District 01
        AL, District 02
        AL, District 03
        AL, District 04
        AL, District 05
        AL, District 06
        AL, District 07
        AR, District 01
        AR, District 02
        AR, District 03
        AR, District 04
        AS, District 98
        AZ, District 01
        AZ, District 02
        AZ, District 03
        AZ, District 04
        AZ, District 05
        AZ, District 06
        AZ, District 07
        AZ, District 08
        AZ, District 09
        CA, District 01
        CA, District 02
        CA, District 03
        CA, District 04
        CA, District 05
        CA, District 06
        CA, District 07
        CA, District 08
        CA, District 09
        CA, District 10
        CA, District 11
        CA, District 12
        CA, District 13
        CA, District 14
        CA, District 15
        CA, District 16
        CA, District 17
        CA, District 18
        CA, District 19
        CA, District 20
        CA, District 21
        CA, District 22
        CA, District 23
        CA, District 24
        CA, District 25
        CA, District 26
        CA, District 27
        CA, District 28
        CA, District 29
        CA, District 30
        CA, District 31
        CA, District 32
        CA, District 33
        CA, District 34
        CA, District 35
        CA, District 36
        CA, District 37
        CA, District 38
        CA, District 39
        CA, District 40
        CA, District 41
        CA, District 42
        CA, District 43
        CA, District 44
        CA, District 45
        CA, District 46
        CA, District 47
        CA, District 48
        CA, District 49
        CA, District 50
        CA, District 51
        CA, District 52
        CA, District 53
        CO, District 01
        CO, District 02
        CO, District 03
        CO, District 04
        CO, District 05
        CO, District 06
        CO, District 07
        CT, District 01
        CT, District 02
        CT, District 03
        CT, District 04
        CT, District 05
        DC, District 98
        DE, District 00
        FL, District 01
        FL, District 02
        FL, District 03
        FL, District 04
        FL, District 05
        FL, District 06
        FL, District 07
        FL, District 08
        FL, District 09
        FL, District 10
        FL, District 11
        FL, District 12
        FL, District 13
        FL, District 14
        FL, District 15
        FL, District 16
        FL, District 17
        FL, District 18
        FL, District 19
        FL, District 20
        FL, District 21
        FL, District 22
        FL, District 23
        FL, District 24
        FL, District 25
        FL, District 26
        FL, District 27
        GA, District 01
        GA, District 02
        GA, District 03
        GA, District 04
        GA, District 05
        GA, District 06
        GA, District 07
        GA, District 08
        GA, District 09
        GA, District 10
        GA, District 11
        GA, District 12
        GA, District 14
        GU, District 98
        HI, District 01
        HI, District 02
        IA, District 01
        IA, District 02
        IA, District 03
        IA, District 04
        ID, District 01
        ID, District 02
        IL, District 01
        IL, District 02
        IL, District 03
        IL, District 04
        IL, District 05
        IL, District 06
        IL, District 07
        IL, District 08
        IL, District 09
        IL, District 10
        IL, District 11
        IL, District 12
        IL, District 13
        IL, District 14
        IL, District 15
        IL, District 16
        IL, District 17
        IL, District 18
        IN, District 01
        IN, District 02
        IN, District 03
        IN, District 04
        IN, District 05
        IN, District 06
        IN, District 07
        IN, District 08
        IN, District 09
        KS, District 01
        KS, District 02
        KS, District 03
        KS, District 04
        KY, District 01
        KY, District 02
        KY, District 03
        KY, District 04
        KY, District 05
        KY, District 06
        LA, District 01
        LA, District 02
        LA, District 03
        LA, District 04
        LA, District 05
        LA, District 06
        MA, District 01
        MA, District 02
        MA, District 03
        MA, District 04
        MA, District 05
        MA, District 06
        MA, District 07
        MA, District 08
        MA, District 09
        MD, District 01
        MD, District 02
        MD, District 03
        MD, District 04
        MD, District 05
        MD, District 06
        MD, District 07
        MD, District 08
        ME, District 01
        ME, District 02
        MI, District 01
        MI, District 02
        MI, District 03
        MI, District 04
        MI, District 05
        MI, District 06
        MI, District 07
        MI, District 08
        MI, District 09
        MI, District 10
        MI, District 11
        MI, District 12
        MI, District 13
        MI, District 14
        MN, District 01
        MN, District 02
        MN, District 03
        MN, District 04
        MN, District 05
        MN, District 06
        MN, District 07
        MN, District 08
        MO, District 01
        MO, District 02
        MO, District 03
        MO, District 04
        MO, District 05
        MO, District 06
        MO, District 07
        MO, District 08
        MP, District 98
        MS, District 01
        MS, District 02
        MS, District 03
        MS, District 04
        MT, District 00
        NC, District 01
        NC, District 02
        NC, District 03
        NC, District 04
        NC, District 05
        NC, District 06
        NC, District 07
        NC, District 08
        NC, District 09
        NC, District 10
        NC, District 11
        NC, District 12
        NC, District 13
        ND, District 00
        NE, District 01
        NE, District 02
        NE, District 03
        NH, District 01
        NH, District 02
        NJ, District 01
        NJ, District 02
        NJ, District 03
        NJ, District 04
        NJ, District 05
        NJ, District 06
        NJ, District 07
        NJ, District 08
        NJ, District 09
        NJ, District 10
        NJ, District 11
        NJ, District 12
        NM, District 01
        NM, District 02
        NM, District 03
        Not applicable
        NV, District 01
        NV, District 02
        NV, District 03
        NV, District 04
        NY, District 01
        NY, District 02
        NY, District 03
        NY, District 04
        NY, District 05
        NY, District 06
        NY, District 07
        NY, District 08
        NY, District 09
        NY, District 10
        NY, District 11
        NY, District 12
        NY, District 13
        NY, District 14
        NY, District 15
        NY, District 16
        NY, District 17
        NY, District 18
        NY, District 19
        NY, District 20
        NY, District 21
        NY, District 22
        NY, District 23
        NY, District 24
        NY, District 25
        NY, District 26
        NY, District 27
        OH, District 01
        OH, District 02
        OH, District 03
        OH, District 04
        OH, District 05
        OH, District 06
        OH, District 07
        OH, District 08
        OH, District 09
        OH, District 10
        OH, District 11
        OH, District 12
        OH, District 13
        OH, District 14
        OH, District 15
        OH, District 16
        OK, District 01
        OK, District 02
        OK, District 03
        OK, District 04
        OK, District 05
        OR, District 01
        OR, District 02
        OR, District 03
        OR, District 04
        OR, District 05
        PA, District 01
        PA, District 02
        PA, District 03
        PA, District 04
        PA, District 05
        PA, District 06
        PA, District 07
        PA, District 08
        PA, District 09
        PA, District 10
        PA, District 11
        PA, District 12
        PA, District 13
        PA, District 14
        PA, District 15
        PA, District 16
        PA, District 17
        PA, District 18
        PR, District 98
        RI, District 01
        RI, District 02
        SC, District 01
        SC, District 02
        SC, District 03
        SC, District 04
        SC, District 05
        SC, District 06
        SC, District 07
        SD, District 00
        TN, District 01
        TN, District 02
        TN, District 03
        TN, District 04
        TN, District 05
        TN, District 06
        TN, District 07
        TN, District 08
        TN, District 09
        TX, District 01
        TX, District 02
        TX, District 03
        TX, District 04
        TX, District 05
        TX, District 06
        TX, District 07
        TX, District 08
        TX, District 09
        TX, District 10
        TX, District 11
        TX, District 12
        TX, District 13
        TX, District 14
        TX, District 15
        TX, District 16
        TX, District 17
        TX, District 18
        TX, District 19
        TX, District 20
        TX, District 21
        TX, District 22
        TX, District 23
        TX, District 24
        TX, District 25
        TX, District 26
        TX, District 27
        TX, District 28
        TX, District 30
        TX, District 31
        TX, District 32
        TX, District 33
        TX, District 34
        TX, District 35
        TX, District 36
        UT, District 01
        UT, District 02
        UT, District 03
        UT, District 04
        VA, District 01
        VA, District 02
        VA, District 03
        VA, District 04
        VA, District 05
        VA, District 06
        VA, District 07
        VA, District 08
        VA, District 09
        VA, District 10
        VA, District 11
        VI, District 98
        VT, District 00
        WA, District 01
        WA, District 02
        WA, District 03
        WA, District 04
        WA, District 05
        WA, District 06
        WA, District 07
        WA, District 08
        WA, District 09
        WA, District 10
        WI, District 01
        WI, District 02
        WI, District 03
        WI, District 04
        WI, District 05
        WI, District 06
        WI, District 07
        WI, District 08
        WV, District 01
        WV, District 02
        WV, District 03
        WY, District 00
    '''

    CONGRESSIONAL_DISTRICT_CHOICES = [((c.strip(), c.strip())) for c in CONGRESSIONAL_DISTRICT_RAW.strip().split('\n')]

    congressional_district = models.CharField(
        verbose_name='Congressional District (115th)',
        max_length=255,
        blank=True, null=True,
    )

    longitude = models.CharField(
        verbose_name='Longitude',
        max_length=255,
        blank=True, null=True,
    )

    latitude = models.CharField(
        verbose_name='Latitude',
        max_length=255,
        blank=True, null=True,
    )

    INSTCAT_RAW = '''
        Degree-granting, associate's and certificates
        Degree-granting, graduate with no undergraduate degrees
        Degree-granting, not primarily baccalaureate or above
        Degree-granting, primarily baccalaureate or above
        Nondegree-granting, above the baccalaureate
        Nondegree-granting, sub-baccalaureate
        Not applicable
        No answer
    '''

    INSTCAT_CHOICES = [((c.strip(), c.strip())) for c in INSTCAT_RAW.strip().split('\n')]

    instcat = models.CharField(
        verbose_name='Latitude',
        max_length=255,
        blank=True, null=True,
    )

    notes = models.CharField(
        verbose_name='Notes',
        max_length=255,
        blank=True, null=True,
    )

    private_comments = models.TextField(
        verbose_name='Private Comments',
        help_text='Please use this space for any additional comments you would like to add about your institution '
                  'or the answers you’ve given above. Anything you write here will be visible to SPARC and future '
                  'editors of this form, but will otherwise remain private and not made available to the public.',
        blank=True, null=True,
        validators=[MaxLengthValidator(3000)],
    )

    @property
    def overview(self):
        return self.overview_raw
        # return markdown.markdown(self.overview_raw)

    def get_absolute_url(self):
        return reverse('profile', kwargs={'uuid': self.access_uuid})

    def __str__(self):
        return 'Profile {}'.format(self.institution_website)


class Program(ModelMixin, TagMixin, models.Model):
    institution = models.ForeignKey('Institution', related_name='program_set')

    name = models.CharField(
        verbose_name='Program Name',
        help_text='Please provide the official name of the program. If there is no official name, please provide a '
                  'descriptive title that can be used to distinguish the program from other initiatives '
                  'at your institution.',
        max_length=140,
    )

    TYPE_CHOICES = (
        ('awards', 'Award Program'),
        ('campaign', 'Campaign'),
        ('course', 'Course'),
        ('grants', 'Grant Program'),
        ('pilot', 'Pilot Program'),
        ('pd', 'Professional Development Program'),
        ('publishing', 'Publishing/Development Program'),
        ('study', 'Research/Study'),
        ('staff', 'Staff Position'),
        ('committee', 'Task Force/Committee'),
        ('other', 'Other'),
    )

    type = models.CharField(
        verbose_name='Program Type',
        help_text='Please select the option that best describes the type of OER program.',
        max_length=255,
        choices=TYPE_CHOICES,
    )

    @property
    def type_directorypage(self):
        try:
            # if self.type == "other":
            #     return None
            return dict(self.TYPE_CHOICES).get(self.type, None)
        except ValueError:
            return None

    def type_clean(self):
        return dict(self.TYPE_CHOICES).get(self.type, '')

    abstract = models.TextField(
        verbose_name='Program Abstract',
        help_text='Please provide a description of the program. This statement will appear in full on your '
                  'institution’s directory page. You may wish to mention the program goals, partners, and current '
                  'status including any metrics. Maximum 1500 characters (~250 words).',
        validators=[MinLengthValidator(140), MaxLengthValidator(1500)]
    )

    HOME_CHOICES = (
        ('dept', 'Academic Department'),
        ('div', 'Academic Division'),
        ('it', 'Academic/Information Technology'),
        ('alumni', 'Alumni Association'),
        ('disability', 'Assistive Technology or Disability Services Office'),
        ('store', 'Campus Store'),
        ('comms', 'Communications Office'),
        ('elearning', 'E-Learning/Distance Education'),
        ('fac_champ', 'Faculty Champions(s)'),
        ('fac_sen', 'Faculty Senate or Union'),
        ('library', 'Library'),
        ('student_grp', 'Other Student Group(s)'),
        ('admin', 'Senior Administration'),
        ('student_gov', 'Student Government'),
        ('student_serv', 'Student Services'),
        ('tlc', 'Teaching and Learning Center'),
        ('other', 'Other'),
        ('none', 'None of the Above'),
    )

    home = models.CharField(
        verbose_name='Unit Within Institution that Houses Program',
        help_text='Please select the most appropriate unit listed.',
        max_length=255,
        choices=HOME_CHOICES,
    )

    @property
    def home_directorypage(self):
        try:
            if self.home == "other":
                return None
            if self.home == "none":
                return None
            return dict(self.HOME_CHOICES).get(self.home, None)
        except ValueError:
            return None

    def home_clean(self):
        return dict(self.HOME_CHOICES).get(self.home, '')

    PARTNERS_CHOICES = (
        ('dept', 'Academic Department'),
        ('div', 'Academic Division'),
        ('it', 'Academic/Information Technology'),
        ('alumni', 'Alumni Association'),
        ('disability', 'Assistive Technology or Disability Services Office'),
        ('store', 'Campus Store'),
        ('comms', 'Communications Office'),
        ('elearning', 'E-Learning/Distance Education'),
        ('fac_champ', 'Faculty Champions(s)'),
        ('fac_sen', 'Faculty Senate or Union'),
        ('library', 'Library'),
        ('student_grp', 'Other Student Group(s)'),
        ('admin', 'Senior Administration'),
        ('student_gov', 'Student Government'),
        ('student_serv', 'Student Services'),
        ('tlc', 'Teaching and Learning Center'),
        ('other', 'Other'),
        ('none', 'None of the Above'),
    )

    partners = models.TextField(
        verbose_name='Program Partners',
        help_text='Please select any options below that are formal partners in the program. You may include a '
                  'list of partners in the program abstract above.',
        # DO NOT include "choices" (because we're displaying checkboxes)
        validators=[none_validator],
    )

    @property
    def partners_directorypage(self):
        try:
            lst = ast.literal_eval(self.partners)
            dct = dict(self.PARTNERS_CHOICES)
            if len(lst) == 1 and lst[0] == "other":
                return None
            if len(lst) == 1 and lst[0] == "none":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
            return output
        except ValueError:
            return None

    @property
    def partners_clean(self):
        lst = ast.literal_eval(self.partners)
        dct = dict(self.PARTNERS_CHOICES)
        return '; '.join(map(lambda val: dct[val], lst))

    SCOPE_CHOICES = (
        ('oer', 'OER (open course content)'),
        ('free', 'Cost-free course content, including OER'),
        ('affordable', 'Affordable course content, including cost-free course content and OER'),
        ('none', 'None of the above'),
    )

    scope = models.CharField(
        verbose_name='Program Scope',
        help_text='Please select the option below that best describes the scope of the program.',
        max_length=255,
        choices=SCOPE_CHOICES,
    )

    @property
    def scope_directorypage(self):
        try:
            if self.scope == "none":
                return None
            return dict(self.SCOPE_CHOICES).get(self.scope, None)
        except ValueError:
            return None

    @property
    def scope_clean(self):
        return dict(self.SCOPE_CHOICES).get(self.scope, '')

    STRATEGY_CHOICES = (
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('na', 'N/A')
    )

    strategy_adaptation = models.CharField(
        verbose_name='OER Adaptation',
        max_length=10,
        choices=STRATEGY_CHOICES,
    )

    @property
    def strategy_adaptation_clean(self):
        return dict(self.STRATEGY_CHOICES).get(self.strategy_adaptation, '')

    strategy_adoption = models.CharField(
        verbose_name='OER Adoption',
        max_length=10,
        choices=STRATEGY_CHOICES,
    )

    @property
    def strategy_adoption_clean(self):
        return dict(self.STRATEGY_CHOICES).get(self.strategy_adoption, '')

    strategy_awareness = models.CharField(
        verbose_name='OER Awareness',
        max_length=10,
        choices=STRATEGY_CHOICES,
    )

    @property
    def strategy_awareness_clean(self):
        return dict(self.STRATEGY_CHOICES).get(self.strategy_awareness, '')

    strategy_curation = models.CharField(
        verbose_name='OER Curation',
        max_length=10,
        choices=STRATEGY_CHOICES,
    )

    @property
    def strategy_curation_clean(self):
        return dict(self.STRATEGY_CHOICES).get(self.strategy_curation, '')

    strategy_pedagogy = models.CharField(
        verbose_name='OER Pedagogy',
        max_length=10,
        choices=STRATEGY_CHOICES,
    )

    @property
    def strategy_pedagogy_clean(self):
        return dict(self.STRATEGY_CHOICES).get(self.strategy_pedagogy, '')

    strategy_publication = models.CharField(
        verbose_name='OER Publication',
        max_length=10,
        choices=STRATEGY_CHOICES,
    )

    @property
    def strategy_publication_clean(self):
        return dict(self.STRATEGY_CHOICES).get(self.strategy_publication, '')

    strategy_review = models.CharField(
        verbose_name='OER Review/Assessment',
        max_length=10,
        choices=STRATEGY_CHOICES,
    )

    @property
    def strategy_review_clean(self):
        return dict(self.STRATEGY_CHOICES).get(self.strategy_review, '')

    strategy_research = models.CharField(
        verbose_name='OER Research',
        max_length=10,
        choices=STRATEGY_CHOICES,
    )

    @property
    def strategy_research_clean(self):
        return dict(self.STRATEGY_CHOICES).get(self.strategy_research, '')

    @property
    def strategy_fields_list(self):
        output = []
        # introspection (introspecting django model fields)
        for f in self._meta.get_fields():
            if f.name.startswith('strategy_'):
                # # getattr: get the *value* of a field
                # print(f.name, f.verbose_name, getattr(self, f.name))
                output.append((f.name, f.verbose_name),)
        return output

    @property
    def strategy_primary_list(self):
        """
        Returns a list with length 1 (primary OER strategy).
        """
        output = []
        for fieldname, fieldname_verbose in self.strategy_fields_list:
            if getattr(self, fieldname) == 'primary':
                output.append((fieldname, fieldname_verbose),)
        if len(output) == 1:  # exactly one of the fields should have value "primary"
            return output
        else:
            raise ValueError('More than one strategy is marked as primary.')

    @property
    def strategy_secondary_list(self):
        output = []
        for fieldname, fieldname_verbose in self.strategy_fields_list:
            if getattr(self, fieldname) == 'secondary':
                output.append((fieldname, fieldname_verbose),)
        return output

    @property
    def strategy_all_list(self):
        # all strategies (primary + secondary) merged -- can be useful for searching
        # #todo -- consider sorting this alphabetically
        return self.strategy_primary_list + self.strategy_secondary_list

    @property
    def strategy_primary_directorypage(self):
        # Return the value of the first item...
        return self.strategy_primary_list[0][1]

    @property
    def strategy_secondary_directorypage(self):
        return ", ".join(dict(self.strategy_secondary_list).values())

    program_date_start = models.CharField(
        verbose_name='Program Start Date',
        help_text='Please include both month and year for Start Date. The required format is "MM/YYYY".',
        max_length=9,
        validators=[date_year_validator],
    )

    program_date_end = models.CharField(
        verbose_name='Program End Date',
        help_text='Please include both month and year for End Date if applicable. If the program has '
                  'not expired, please leave End Date blank. The required format is "MM/YYYY".',
        max_length=9,
        blank=True, null=True,
        validators=[date_year_validator],
    )

    FUNDING_SOURCE_CHOICES = (
        ('dept', 'Academic department budget'),
        ('alumni', 'Alumni Fund'),
        ('store', 'Campus Store'),
        ('endowment', 'Endowment'),
        ('grants', 'External grants'),
        ('operating', 'Institution’s general operating budget'),
        ('it', 'Institution’s IT budget'),
        ('lib_dept', 'Library departmental budget'),
        ('lib_operating', 'Library’s general operating budget'),
        ('lib_special', 'Library’s special project fund'),
        ('administrator', 'President, Chancellor, or Provost’s budget'),
        ('state', 'State/Province'),
        ('student_fee', 'Student Fees'),
        ('studentgov_fund', 'Student Government Fund'),
        ('unknown', 'Unknown'),
        ('na', 'Not Applicable'),
        ('other', 'Other funding source, please specify'),
    )

    funding_source = models.TextField(
        verbose_name='Source(s) of Program Funding',
        help_text='Please select all sources of program funding below.',
        # DO NOT include "choices" (because we're displaying checkboxes)
        validators=[na_validator, unknown_validator],
    )

    @property
    def funding_source_clean(self):
        lst = ast.literal_eval(self.funding_source)
        dct = dict(self.FUNDING_SOURCE_CHOICES)
        selected = '; '.join(map(lambda val: dct[val], lst[0]))
        custom = ': ' + lst[1] if lst[1] else ''
        return selected + custom

    @property
    def funding_source_directorypage(self): #multiwidget:checkboxes
        lst = ast.literal_eval(self.funding_source)
        dct = dict(self.FUNDING_SOURCE_CHOICES)
        dct['other'] = 'Other'
        if 'na' in lst:
            return None
        selected = ', '.join(map(lambda val: dct[val], lst[0]))
        custom = ': ' + lst[1] if lst[1] else ''
        return (selected + custom).split(', ')

    FUNDING_LIBRARY_CHOICES = (
        ('admin', 'Administration'),
        ('collections', 'Collections & Technical Services'),
        ('reference', 'Public Service/Reference'),
        ('scholcomm', 'Scholarly Communications'),
        ('liaisons', 'Subject Liaisons'),
        ('tl', 'Teaching & Learning'),
        ('press', 'University Press'),
        ('other', 'Other'),
        ('na', 'Not Applicable'),
        ('unknown', 'Not Sure'),
    )

    funding_library = models.TextField(
        verbose_name='If the source of funding includes the Library’s general operating budget or departmental budget, '
                     'please select the Library department(s) from which the funds came. If the source of funding '
                     'includes the Library’s general operating budget or departmental budget, please select the '
                     'Library department(s) from which the funds came.',
        help_text='If this question is not applicable, please select “Not Applicable”.',
        # DO NOT include "choices" (because we're displaying checkboxes)
        validators=[na_validator, notsure_unknown_validator],
    )

    @property
    def funding_library_directorypage(self):
        try:
            lst = ast.literal_eval(self.funding_library)
            dct = dict(self.FUNDING_LIBRARY_CHOICES)
            if len(lst) == 1 and lst[0] == "other":
                return None
            if len(lst) == 1 and lst[0] == "na":
                return None
            if len(lst) == 1 and lst[0] == "unknown":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
            return output
        except ValueError:
            return None

    def funding_library_clean(self):
        lst = ast.literal_eval(self.funding_library)
        dct = dict(self.FUNDING_LIBRARY_CHOICES)
        return '; '.join(map(lambda val: dct[val], lst))

    funding_total = models.IntegerField(
        verbose_name='Total Program Funding to Date',
        help_text='Please provide the total amount of funding that has been allocated to fund the program '
                  'to date. Please enter numbers only (i.e. do not add “$”) and use your local currency '
                  '(i.e. do NOT convert CAD to USD).',
        validators=[MinValueValidator(0)],
    )

    @property
    def funding_total_directorypage(self):
        try:
            amount = int(self.funding_total)
            if amount <= 0:
                return None
            # # "," = thousands separator: https://stackoverflow.com/a/10742904
            return ('$ ' + "{:,}".format(amount))
        except ValueError:
            return None

    savings_total = models.IntegerField(
        verbose_name='Total Student Savings to Date',
        help_text='Please provide the total amount of money that the program has saved students to date. '
                  'If the number is zero, please put 0. Please enter numbers only (i.e. do not add “$”) and use '
                  'your local currency (i.e. do NOT convert CAD to USD). If you do not know or this question is not '
                  'applicable, please leave it blank.',
        blank=True, null=True,
        validators=[MinValueValidator(0)],
    )

    @property
    def savings_total_directorypage(self):
        try:
            amount = int(self.savings_total)
            if amount <= 0:
                return None
            return ('$ ' + "{:,}".format(amount))
        except ValueError:
            return None

    FINANCIAL_SUSTAINABILITY_CHOICES = (
        ('sustainable', 'Program is financially sustainable'),
        ('progress', 'Program has made significant progress toward financial sustainability'),
        ('no_progress', 'Program has not made significant progress toward financial sustainability'),
        ('na', 'Not applicable'),
    )

    financial_sustainability = models.CharField(
        verbose_name='Financial Sustainability',
        help_text='If the program is intended to be financially sustainable, please select the option that '
                  'best describes the current status. If the program is not intended to be financially sustainable or '
                  'this question does not apply, please select “Not applicable”.',
        max_length=255,
        choices=FINANCIAL_SUSTAINABILITY_CHOICES,
    )

    def financial_sustainability_clean(self):
        return dict(self.FINANCIAL_SUSTAINABILITY_CHOICES).get(self.financial_sustainability, '')

    INCENTIVES_VERBOSE_NAME='Incentive(s) Offered by the Program'

    INCENTIVES_HELP_TEXT='Please select any incentives offered by the program to those who participate. For the purposes of this question, please do not count program outcomes as incentives, such as reducing textbook costs for students.'

    INCENTIVES_CHOICES = (
        ('grants', 'Financial incentives (grants, stipends)'),
        ('time', 'Course release time'),
        ('design', 'Instructional design assistance'),
        ('tech', 'Technical assistance'),
        ('pd', 'Professional development'),
        ('letter', 'Letter of commendation'),
        ('award', 'Award or public recognition'),
        ('na', 'Not applicable'),
        ('other', 'Other incentive, please briefly specify'),
    )

    incentives = models.TextField(
        # verbose_name -> defined in admin_forms.py
        # help_text -> defined in admin_forms.py
        # choices -> defined in admin_forms.py
        validators=[na_validator],
    )

    @property
    def incentives_clean(self):
        lst = ast.literal_eval(self.incentives)
        dct = dict(self.INCENTIVES_CHOICES)
        selected = '; '.join(map(lambda val: dct[val], lst[0]))
        custom = ': ' + lst[1] if lst[1] else ''
        return selected + custom

    @property
    def incentives_directorypage(self): #multiwidget:checkboxes
        lst = ast.literal_eval(self.incentives)
        dct = dict(self.INCENTIVES_CHOICES)
        dct['other'] = 'Other'
        if 'na' in lst:
            return None
        selected = ', '.join(map(lambda val: dct[val], lst[0]))
        custom = ': ' + lst[1] if lst[1] else ''
        return (selected + custom).split(', ')

    grant_funding = models.IntegerField(
        verbose_name='Total amount of financial incentives awarded to date',
        blank=True, null=True,
        validators=[MinValueValidator(0)],
    )

    @property
    def grant_funding_directorypage(self):
        try:
            amount = int(self.grant_funding)
            if amount <= 0:
                return None
            return ('$ ' + "{:,}".format(amount))
        except ValueError:
            return None

    grant_number = models.IntegerField(
        verbose_name='Total number of financial incentives awarded to date',
        blank=True, null=True,
        validators=[MinValueValidator(0)],
    )

    @property
    def grant_number_directorypage(self):
        try:
            amount = int(self.grant_number)
            if amount <= 0:
                return None
            return "{:,}".format(amount)  # no "$"
        except ValueError:
            return None

    grant_typical = models.IntegerField(
        verbose_name='Typical amount of each grant',
        blank=True, null=True,
        validators=[MinValueValidator(0)],
    )

    @property
    def grant_typical_directorypage(self):
        try:
            amount = int(self.grant_typical)
            if amount <= 0:
                return None
            return ('$ ' + "{:,}".format(amount))
        except ValueError:
            return None

    INCENTIVES_CONDITIONS_CHOICES = (
        ('open_required', 'Recipients are required to openly license and freely share resources created or adapted'),
        ('open_encouraged', 'Recipients are encouraged to openly license and freely share resources created or adapted'),
        ('none', 'None of the above'),
        ('na', 'Not applicable'),
    )

    incentives_conditions = models.CharField(
        verbose_name='If financial incentives such as grants or stipends are offered, please indicate which of the '
                     'following best describes the conditions for receipt of the incentives.',
        help_text='Please select the option that best describes the conditions below, or select “not applicable” '
                  'if this question does not apply.',
        max_length=255,
        choices=INCENTIVES_CONDITIONS_CHOICES
    )

    @property
    def incentives_conditions_directorypage(self):
        try:
            if self.incentives_conditions == "none":
                return None
            if self.incentives_conditions == "na":
                return None
            return dict(self.INCENTIVES_CONDITIONS_CHOICES).get(self.incentives_conditions, None)
        except ValueError:
            return None

    @property
    def incentives_conditions_clean(self):
        return dict(self.INCENTIVES_CONDITIONS_CHOICES).get(self.incentives_conditions, '')

    url_program = models.URLField(
        verbose_name='Program Webpage',
        max_length=255,
        blank=True, null=True,
    )

    url_mou = models.URLField(
        verbose_name='MOU for Participants',
        max_length=255,
        blank=True, null=True,
    )

    url_assess = models.URLField(
        verbose_name='Assessment Instrument',
        max_length=255,
        blank=True, null=True,
    )

    url_job = models.URLField(
        verbose_name='Job Description',
        max_length=255,
        blank=True, null=True,
    )

    url_other = models.URLField(
        verbose_name='Other Resource',
        max_length=255,
        blank=True, null=True,
    )

    private_comments = models.TextField(
        verbose_name='Private Comments',
        help_text='Please use this space for any additional comments you would like to add about this program '
                  'or the answers you’ve given above. Anything you write here will be visible to SPARC and future '
                  'editors of this form, but will otherwise remain private and not made available to the public.',
        blank=True, null=True,
        validators=[MaxLengthValidator(3000)],
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('activity_program', kwargs={'uuid': self.access_uuid})


class Policy(ModelMixin, TagMixin, models.Model):
    class Meta:
        verbose_name_plural = "policies"

    institution = models.ForeignKey('Institution', related_name='policy_set')

    name = models.CharField(
        verbose_name='Policy Name',
        max_length=255,
    )

    POLICY_TYPE_CHOICES=(
        ('rule', 'Formal Policy (rule, regulation, law, etc.)'),
        ('resolution', 'Resolution/Declaration (faculty senate, position statement, etc.)'),
        ('practice', 'Practice (marking course catalog with OER, fee, etc.)'),
        ('plan', 'Plan (strategic plan that mentions OER, action plan, etc.)'),
        ('other', 'Other'),
    )

    policy_type = models.CharField(
        verbose_name='Policy Type',
        help_text='Please select the option that best describes the policy.',
        max_length=255,
        choices=POLICY_TYPE_CHOICES,
    )

    @property
    def policy_type_directorypage(self):
        try:
            if self.policy_type == "other":
                return None
            # clean up before return (remove instructions in parentheses), e.g.
            # instead of "Resolution/Declaration (faculty senate, position statement, etc.)"
            # only return "Resolution/Declaration"
            raw_policy = dict(self.POLICY_TYPE_CHOICES).get(self.policy_type, None)
            return raw_policy.split('(')[0].strip()
        except ValueError:
            return None

    policy_abstract = models.TextField(
        verbose_name='Policy Abstract',
        help_text='Please provide a brief description of the policy. Maximum 1500 characters (~250 words).',
        blank=True, null=True,
        validators=[MaxLengthValidator(1500)],
    )

    SCOPE_CHOICES=(
        ('oer', 'OER (open course content)'),
        ('free', 'Cost-free course content, including OER'),
        ('affordable', 'Affordable course content, including cost-free course content and OER'),
        ('none', 'None of the above'),
    )

    scope = models.CharField(
        verbose_name='Policy Scope',
        help_text='Please select the option below that best describes the scope of the policy.',
        max_length=255,
        choices=SCOPE_CHOICES,
    )

    @property
    def scope_directorypage(self):
        try:
            if self.scope == "none":
                return None
            return dict(self.SCOPE_CHOICES).get(self.scope, None)
        except ValueError:
            return None

    POLICY_LEVEL_CHOICES=(
        ('state', 'State/province wide'),
        ('system', 'System wide'),
        ('institution', 'Institution wide'),
        ('faculty', 'Faculty Senate'),
        ('student', 'Student Government'),
        ('div', 'Academic Division (i.e. a specific college or faculty within the institution)'),
        ('dept', 'Department'),
        ('program', 'Program'),
        ('other', 'Other'),
    )

    policy_level = models.CharField(
        verbose_name='Policy Governance Level',
        help_text='Please select the level of governance at which the policy applies.',
        max_length=255,
        choices=POLICY_LEVEL_CHOICES,
    )

    @property
    def policy_level_directorypage(self):
        try:
            if self.policy_level == "other":
                return None
            return dict(self.POLICY_LEVEL_CHOICES).get(self.policy_level, None)
        except ValueError:
            return None

    policy_date_start = models.CharField(
        verbose_name='Policy Start Date',
        help_text='Please include both month and year for Start Date. The required format is "MM/YYYY".',
        max_length=9,
        validators=[date_year_validator],
    )

    policy_date_end = models.CharField(
        verbose_name='Policy End Date',
        help_text='Please include both month and year for End Date if applicable. If the policy has '
                  'not expired, please leave End Date blank. The required format is "MM/YYYY".',
        max_length=9,
        blank=True, null=True,
        validators=[date_year_validator],
    )

    POLICY_DEFINITION_CHOICES=(
        ('yes', 'Yes'),
        ('no', 'No'),
        ('na', 'Not Applicable'),
    )

    policy_definition = models.CharField(
        verbose_name='Does the policy explicitly mention the term “open educational resources” or an equivalent term '
                     'that includes the word “open”?',
        max_length=255,
        choices=POLICY_DEFINITION_CHOICES,
    )

    url_text = models.URLField(
        verbose_name='Official Text',
        max_length=255,
        blank=True, null=True,
    )

    url_description = models.URLField(
        verbose_name='Description',
        max_length=255,
        blank=True, null=True,
    )

    url_announcement = models.URLField(
        verbose_name='Announcement',
        max_length=255,
        blank=True, null=True,
    )

    url_report = models.URLField(
        verbose_name='Progress Report',
        max_length=255,
        blank=True, null=True,
    )

    private_comments = models.TextField(
        verbose_name='Private Comments',
        help_text='Please use this space for any additional comments you would like to add about this policy '
                  'or the answers you’ve given above. Anything you write here will be visible to SPARC and future '
                  'editors of this form, but will otherwise remain private and not made available to the public.',
        blank=True, null=True,
        validators=[MaxLengthValidator(3000)],
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('activity_policy', kwargs={'uuid': self.access_uuid})


class Event(ModelMixin, TagMixin, models.Model):
    institution = models.ForeignKey('Institution', related_name='event_set')

    name = models.CharField(
        verbose_name='Event Name',
        help_text='Max 140 characters.',
        max_length=140,
    )

    TYPE_CHOICES = (
        ('talk', 'Talk/Presentation'),
        ('workshop', 'Workshop/Professional Development'),
        ('panel', 'Panel/Roundtable'),
        ('conference', 'Symposium/Conference/Summit'),
        ('webcast', 'Webcast'),
        ('other', 'Other'),
    )

    type = models.TextField(
        verbose_name='Event Type',
        help_text='Please indicate the type of event. Please note that we are looking for only events that '
                  'were directly organized by your institution.',
        # DO NOT include "choices" (because we're displaying a custom multifield)
    )

    @property
    def type_directorypage(self): #multiwidget:radio
        lst = ast.literal_eval(self.type)
        dct = dict(self.TYPE_CHOICES)
        try:
            if lst[0] == 'other':
                return None
                # return 'Other: ' + lst[1]
            else:
                return dct[lst[0]]
        except:
            return None

    abstract = models.TextField(
        verbose_name='Event Abstract',
        help_text='Please provide a brief description of the event. You may wish to cover the topic of the event, '
                  'the names of any speakers, and information about the audience. You will have a chance to share '
                  'URLs in later questions. Maximum 1500 characters.',
        validators=[MinLengthValidator(140), MaxLengthValidator(1500)],
    )

    SCOPE_CHOICES=(
        ('oer', 'OER (open course content)'),
        ('free', 'Cost-free course content, including OER'),
        ('affordable', 'Affordable course content, including cost-free course content and OER'),
        ('none', 'None of the above'),
    )

    scope = models.CharField(
        verbose_name='Event Scope',
        help_text='Please select the option below that best describes the scope of the event.',
        max_length=20,
        choices=SCOPE_CHOICES,
    )

    @property
    def scope_directorypage(self):
        try:
            if self.scope == "none":
                return None
            return dict(self.SCOPE_CHOICES).get(self.scope, None)
        except ValueError:
            return None

    date_start = models.DateField(
        verbose_name='Date of Event (Start Date)',
        help_text='Please include both month and year for Start Date and End Date if applicable. If the event '
                  'concluded on the same day, please leave End Date blank. The required format is "MM/DD/YYYY".',
    )

    date_end = models.DateField(
        verbose_name='Date of Event (End Date)',
        help_text='Please include both month and year for Start Date and End Date if applicable. If the event '
                  'concluded on the same day, please leave End Date blank. The required format is "MM/DD/YYYY".',
        blank=True, null=True,
    )

    attendees = models.IntegerField(
        verbose_name='Approximate Number of Attendees',
        help_text='Please list the approximate number of people who attended the event. Please enter only a number '
                  'without punctuation.',
        blank=True, null=True,
    )

    @property
    def attendees_directorypage(self):
        try:
            amount = int(self.attendees)
            if amount <= 0:
                return None
            return ("{:,}".format(amount))
        except ValueError:
            return None

    hashtag = models.CharField(
        verbose_name='Event Hashtag',
        help_text='If the event had a social media hashtag, please provide it here. Please include the “#” at the '
                  'beginning.',
        max_length=140,
        blank=True, null=True,
    )

    url_summary = models.URLField(
        verbose_name='Event Summary',
        max_length=255,
        blank=True, null=True,
    )

    url_promo = models.URLField(
        verbose_name='Promotional Material',
        blank=True, null=True,
    )

    url_recording = models.URLField(
        verbose_name='Recording',
        max_length=255,
        blank=True, null=True,
    )

    url_slides = models.URLField(
        verbose_name='Slides',
        max_length=255,
        blank=True, null=True,
    )

    url_photos = models.URLField(
        verbose_name='Photos',
        max_length=255,
        blank=True, null=True,
    )

    url_news = models.URLField(
        verbose_name='News Coverage',
        max_length=255,
        blank=True, null=True,
    )

    private_comments = models.TextField(
        verbose_name='Private Comments',
        help_text='Please use this space for any additional comments you would like to add about this event or '
                  'the answers you’ve given above. Anything you write here will be visible to SPARC and future '
                  'editors of this form, but will otherwise remain private and not made available to the public.',
        blank=True, null=True,
        validators=[MaxLengthValidator(3000)],
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('activity_event', kwargs={'uuid': self.access_uuid})


class Resource(ModelMixin, TagMixin, models.Model):
    institution = models.ForeignKey('Institution', related_name='resource_set')

    name = models.CharField(
        verbose_name='Resource Title',
        help_text='Please provide the name of the resource.',
        max_length=140,
    )

    TYPE_CHOICES=(
        ('story', 'Success Story'),
        ('awareness', 'Fact Sheet or Awareness Resource'),
        ('guide', 'Guide (e.g. LibGuide)'),
        ('video', 'Video'),
        ('collection', 'Repository or Collection'),
        ('blog', 'Blog'),
        ('report', 'Report'),
        ('slides', 'Slide Deck'),
        ('article', 'Peer Reviewed Article'),
        ('news', 'News Article'),
        ('plan', 'Plan'),
        ('other', 'Other'),
    )

    type = models.TextField(
        verbose_name='Resource Type',
        help_text='Please select the options that best describe the type of resource. Please note that this category '
                  'is intended for resources about OER, not as a listing of individual OER.',
        # DO NOT include "choices" (because we're displaying checkboxes)
    )

    @property
    def type_directorypage(self):
        try:
            lst = ast.literal_eval(self.type)
            dct = dict(self.TYPE_CHOICES)
            if len(lst) == 1 and lst[0] == "other":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
            return output
        except ValueError:
            return None

    @property
    def type_directorypage_string(self):
        return ', '.join(self.type_directorypage)

    abstract = models.TextField(
        verbose_name='Resource Abstract',
        help_text='Please provide a brief description of the resource. Max 500 characters.',
        max_length=500,
        blank=True, null=True,
    )

    SCOPE_CHOICES=(
        ('oer', 'OER (open course content)'),
        ('free', 'Cost-free course content, including OER'),
        ('affordable', 'Affordable course content, including cost-free course content and OER'),
        ('none', 'None of the above'),
    )

    scope = models.CharField(
        verbose_name='Resource Scope',
        help_text='Please select the option below that best describes the scope of the resource.',
        max_length=20,
        choices=SCOPE_CHOICES,
    )

    citation = models.CharField(
        verbose_name='Resource Citation/Attribution',
        help_text='Please indicate how others should cite or attribute this resource, including title, author,'
                  'and publisher (if any). APA format is preferred for publications.',
        max_length=255,
        blank=True, null=True,
    )

    date = models.CharField(
        verbose_name='Date of Publication',
        help_text='Please include both month and year. If you do not know the date of publication, '
                  'please leave it blank. The required format is "MM/YYYY".',
        max_length=9,
        blank=True, null=True,
        validators=[date_year_validator]
    )

    LICENSE_CHOICES = (
        ('ccby', 'CC BY'),
        ('ccbysa', 'CC BY SA'),
        ('ccbync', 'CC BY NC'),
        ('ccbyncsa', 'CC BY NC SA'),
        ('cc0', 'CC0 Public Domain Dedication'),
        ('gfdl', 'Gnu Free Documentation License'),
        ('pd', 'Public Domain'),
        ('c', 'All Rights Reserved'),
        ('unknown', 'Unknown'),
        ('other', 'Other (please specify)'),
    )

    license = models.TextField(
        verbose_name='Resource License',
        help_text='Please specify the copyright permissions of the work.',
        # DO NOT include "choices" (because we're displaying a custom multifield)
        null=True,
    )

    @property
    def license_directorypage(self): #multiwidget:radio
        lst = ast.literal_eval(self.license)
        dct = dict(self.LICENSE_CHOICES)
        try:
            if lst[0] == 'unknown':
                return None
            elif lst[0] == 'other':
                return None
                # return 'Other: ' + lst[1]
            else:
                return dct[lst[0]]
        except:
            return None

    AUDIENCE_CHOICES=(
        ('faculty', 'Faculty'),
        ('students', 'Students'),
        ('librarians', 'Librarians'),
        ('admin', 'Administration'),
        ('policy', 'Policymakers'),
        ('community', 'Community'),
        ('other', 'Other'),
    )

    audience = models.TextField(
        verbose_name='Intended Audience of Resource',
        help_text='Please select the audience(s) for which the resource is intended. Select all that apply.',
        # DO NOT include "choices" (because we're displaying checkboxes)
    )

    @property
    def audience_directorypage(self):
        try:
            lst = ast.literal_eval(self.audience)
            dct = dict(self.AUDIENCE_CHOICES)
            if len(lst) == 1 and lst[0] == "other":
                return None
            output = []
            for item in lst:
                output.append(dct.get(item))
            return output
        except ValueError:
            return None

    url = models.URLField(
        verbose_name='Link to Access the Resource',
        help_text='Please provide a URL where the resource can be found. Please ensure to include the “http” or '
                  '“https” prefix, and only one link is permitted per box. If the file is not already online, '
                  'you can upload it using a free service such as Internet Archive (https://archive.org/create).',
    )

    private_comments = models.TextField(
        verbose_name='Private Comments',
        help_text='Please use this space for any additional comments you would like to add about this resource or '
                  'the answers you’ve given above. Anything you write here will be visible to SPARC and future '
                  'editors of this form, but will otherwise remain private and not made available to the public.',
        blank=True, null=True,
        validators=[MaxLengthValidator(3000)],
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('activity_resource', kwargs={'uuid': self.access_uuid})


class Institution(ModelMixin, TagMixin, models.Model):
    slug = models.SlugField(blank=True, null=True)
    name = models.CharField(max_length=100)
    profile = models.OneToOneField('InstitutionProfile')
    editors = models.ManyToManyField('users.User', blank=True)

    # program_set field is added via Program model
    # policy_set field is added via Policy model
    # event_set field is added via Event model
    # resource_set field is added via Resource model
    # annual_reports field is added via AnnualImpactReport model
    # additional_languages field is added via ForeignLanguageInstitutionDescription model

    def clean(self):
        if self.slug and Institution.objects.filter(slug=self.slug).exists():
            from django.core.validators import ValidationError
            raise ValidationError({'slug':'Institution with this slug already exists'})
        return super().clean()

    @property
    def students_impacted_total(self):
        return sum(self.annual_reports.all().values_list('impact_students', flat=True))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institution', kwargs={'uuid': self.access_uuid})

    # @property
    # def sparc_member(self):
    #     return 'sparc_member' in self._tags_raw.slugs()


class Tag(ModelMixin, models.Model):
    TYPE_MEMBERSHIP = 'membership'
    TYPE_PROJECT = 'project'
    TYPE_PERSON = 'person'
    TYPE_SYSTEM = 'system'
    TYPE_GENERAL = 'general'
    TYPE_HIDDEN = 'hidden'

    type = models.CharField(
        verbose_name='Type',
        choices=(
            (TYPE_MEMBERSHIP, 'Membership'),
            (TYPE_PROJECT, 'Project'),
            (TYPE_PERSON, 'Person'),
            (TYPE_SYSTEM, 'System'),
            (TYPE_GENERAL, 'General'),
            (TYPE_HIDDEN, 'Hidden'),
        ),
        max_length=20
    )

    name = models.CharField(
        verbose_name='Tag Name',
        max_length=100
    )

    slug = models.SlugField(
        verbose_name='Tag Slug',
        unique=True
    )

    description = models.TextField(
        verbose_name='Description',
        blank=True,
        null=True
    )

    first_name = models.CharField(
        verbose_name='First Name',
        max_length=100,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        verbose_name='Last Name',
        max_length=100,
        blank=True,
        null=True
    )

    job_title = models.CharField(
        verbose_name='Job Title',
        max_length=100,
        blank=True,
        null=True
    )

    department = models.CharField(
        verbose_name='Department',
        max_length=100,
        blank=True,
        null=True
    )

    institution = models.CharField(
        verbose_name='Institution',
        max_length=100,
        blank=True,
        null=True
    )

    zip = models.CharField(
        verbose_name='Postal Code',
        max_length=100,
        blank=True,
        null=True
    )

    country = models.CharField(
        verbose_name='Country',
        max_length=100,
        blank=True,
        null=True
    )

    email = models.EmailField(
        verbose_name='Email Address',
        max_length=100,
        blank=True,
        null=True
    )

    twitter = models.CharField(
        verbose_name='Twitter Handle',
        max_length=100,
        blank=True,
        null=True
    )

    url = models.URLField(
        verbose_name='Website',
        max_length=100,
        blank=True,
        null=True
    )

    profession = models.CharField(
        verbose_name='Profession',
        max_length=100,
        blank=True,
        null=True
    )

    expertise = models.CharField(
        verbose_name='Area of Expertise',
        max_length=100,
        blank=True,
        null=True
    )

    system_name = models.CharField(
        verbose_name='System Name',
        max_length=100,
        blank=True,
        null=True
    )

    system_website = models.URLField(
        verbose_name='System Website',
        max_length=100,
        blank=True,
        null=True
    )

    system_link = models.CharField(
        verbose_name='System Link in Directory',
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class AccessLink(ModelMixin, models.Model):
    IMPACT_REPORT = 'impact-report'
    LANGUAGE = 'language'
    PROFILE = 'profile'
    PROGRAM = 'program'
    POLICY = 'policy'
    EVENT = 'event'
    RESOURCE = 'resource'

    TYPE_CHOICES = [
        (IMPACT_REPORT, 'Impact report'),
        (LANGUAGE, 'Language'),
        (PROFILE, 'Profile'),
        (PROGRAM, 'Program'),
        (POLICY, 'Policy'),
        (EVENT, 'Event'),
        (RESOURCE, 'Resource'),
    ]

    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text_raw = models.TextField(blank=True, null=True)

    @property
    # normalized "type" for printing in templates (#virtualfield)
    # reason: print "impact-report" as "Impact Report" (capitalized, no dash)
    def type_normalized(self):
        return self.type.title().replace('-', ' ')

    @property
    def text(self):
        return self.text_raw
        # return markdown.markdown(self.text_raw)

    def __str__(self):
        return 'Access to {} type {}'.format(self.institution, self.type)

    def get_absolute_url(self):
        return reverse('access', kwargs={'uuid': self.access_uuid})

    @property
    def object_type(self):
        return dict(self.TYPE_CHOICES)[self.type]
