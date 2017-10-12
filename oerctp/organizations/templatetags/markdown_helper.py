# markdown filter based on https://web.archive.org/web/20170331191111/https://stackoverflow.com/questions/25135346/using-markdownsafe-in-django-gives-syntax-error

# #todo -- consider using "bleach" https://web.archive.org/web/20170401043601/https://stackoverflow.com/questions/37757474/django-rendering-markdown-sanitizied-with-bleach

# #todo -- bleach has "linkify" function -- see https://web.archive.org/web/20170401044238/https://raw.githubusercontent.com/vchrisb/emc_phoenix3/4ee59cc3ff3dfdc62a460308e157d702371df69c/content/templatetags/markdown_filter.py

import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=False)
@stringfilter
def markdown_to_html(value):
    extensions = ["nl2br", ]

    value='\n'+value  # if the text starts with heading, make sure we catch it
    value=value.replace('\n# ', '\n#### ')
    value=value.replace('\n## ', '\n#### ')
    value=value.replace('\n### ', '\n#### ')

    return mark_safe(markdown.markdown(force_text(value),
                                       extensions,
                                       safe_mode=False,
                                       enable_attributes=False))
