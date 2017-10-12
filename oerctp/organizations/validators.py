import ast
from datetime import datetime
import string

from django.core.validators import BaseValidator, ValidationError
from django.utils.translation import ungettext_lazy as _

def ack_checked_validator(value):
    if not value:
        raise ValidationError('You must check the box to accept the acknowledgments.')


def twitter_handle_validator(value):
    if len(value) == 0:
        raise ValidationError('Twitter handle cannot cannot be empty.')

    if value[0] != '@':
        raise ValidationError('Twitter handle must start with @.')

    if '@' in value[1:]:
        raise ValidationError('Twitter handle can only contain @ as the first character.')

    if set(value) - set(string.ascii_letters + string.digits + '_' + '@'):
        raise ValidationError('Invalid character(s) in your Twitter handle.')


def none_validator(value):
    try:
        lst = ast.literal_eval(value)
    except ValueError:
        print('chyba je tu1!', value)
        lst = []
    if 'none' in lst and len(lst) > 1:
        raise ValidationError('You cannot choose both "None" ("None of the Above") and another option.')


def no_validator(value):
    try:
        lst = ast.literal_eval(value)
    except ValueError:
        print('chyba je tu!2', value)
        lst = []
    if 'no' in lst and len(lst) > 1:
        raise ValidationError('You cannot choose both "No" and another option.')


def na_validator(value):
    try:
        lst = ast.literal_eval(value)
    except ValueError:
        print('chyba je tu!2a', value)
        lst = []
    if 'na' in lst and len(lst) > 1:
        raise ValidationError('You cannot choose both "Not Applicable" and another option.')


def notsure_unknown_validator(value):
    try:
        lst = ast.literal_eval(value)
    except ValueError:
        print('chyba je tu!2b', value)
        lst = []
    if 'unknown' in lst and len(lst) > 1:
        raise ValidationError('You cannot choose both "Not Sure" and another option.')


def unknown_validator(value):
    try:
        lst = ast.literal_eval(value)
    except ValueError:
        print('chyba je tu!2c', value)
        lst = []
    if 'unknown' in lst and len(lst) > 1:
        raise ValidationError('You cannot choose both "Unknown" and another option.')


# do not delete validators, even if they are unused (they are still referenced from migrations)
def na_or_ns_validator(value):
    try:
        lst = ast.literal_eval(value)
    except ValueError:
        print('chyba je tu!3', value)
        lst = []
    if ('na' in lst or 'unknown' in lst) and len(lst) > 1:
        raise ValidationError('You may not select any other options if you select “Not Sure” or “Not Applicable”')


class MaxChoicesValidator(BaseValidator):
    message = _(
        'Ensure this value has at most %(limit_value)d choice (it has %(show_value)d).',  # NOQA
        'Ensure this value has at most %(limit_value)d choices (it has %(show_value)d).',  # NOQA
        'limit_value'
    )
    code = 'max_choices'

    def compare(self, value, limit):
        return value > limit

    def clean(self, x):
        lst = ast.literal_eval(x)
        return len(lst)


class MinChoicesValidator(BaseValidator):
    message = _(
        'Ensure this value has at least %(limit_value)d choice (it has %(show_value)d).',
        'Ensure this value has at least %(limit_value)d choices (it has %(show_value)d).',
        'limit_value'
    )
    code = 'min_choices'

    def compare(self, value, limit):
        return value < limit

    def clean(self, x):
        lst = ast.literal_eval(x)
        return len(lst)


def date_year_validator(value):
    try:
        datetime.strptime(value, '%m/%Y')
    except ValueError:
        raise ValidationError('Ensure date is in the following format MM/YYYY.')
