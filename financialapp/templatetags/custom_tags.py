from django import template
from datetime import timedelta, date
# from num2words import num2words
from financialapp.models import *
import base64

register = template.Library()


@register.filter
def is_checkbox(field):
    # print('----------- ',field.field.widget.__class__.__name__)
    return field.field.widget.__class__.__name__ == "CheckboxInput"

@register.filter
def is_select(field):
    return field.field.widget.__class__.__name__ == "Select"

@register.filter
def is_file(field):
    return field.field.widget.__class__.__name__ in ["FileInput", "ClearableFileInput","ImageField", "Textarea", "ModelMultipleChoiceField"]

@register.filter
def is_charfield(field):
    return field.field.__class__.__name__ == "TextInput"

@register.filter
def is_emailfield(field):
    return field.field.__class__.__name__ == "EmailField"

@register.filter
def is_charfield_100(field):
    is_what = False
    try:
        if field.field.__class__.__name__ == "CharField":
            if field.field.max_length <= 100:
                is_what = True
    except:
        pass
    return is_what

@register.filter
def is_charfield_200(field):
    is_what = False
    try:
        # print('-----', field.label, field.field.__class__.__name__, field.field.max_length, type( field.field.max_length))
        if field.field.__class__.__name__ == "CharField":
            if field.field.max_length == None or field.field.max_length >= 200:
                is_what = True
    except:
        pass
    return is_what

@register.filter
def is_booleanfield(field):
    return field.field.__class__.__name__ == "BooleanField"

@register.filter
def is_many_to_many(field):
    return field.field.__class__.__name__ == "ModelMultipleChoiceField"

@register.filter
def is_document(field):
    return field.field.__class__.__name__ == "ClearableFileInput"
