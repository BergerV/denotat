from django import template
from diploma2.languages.models import *
register = template.Library()

@register.inclusion_tag('tags/select_lang.html')
def select_lang():
    languages = Language.objects.all()
    return {'languages':languages} 
