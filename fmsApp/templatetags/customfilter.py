from atexit import register
from django import template
from cryptography.fernet import Fernet
from django.conf import settings
import os


register = template.Library()

@register.filter
def replaceBlank(value,stringVal = ""):
    value = str(value).replace(stringVal, '')
    return value

@register.filter
def encryptdata(value):
    fernet = Fernet(settings.ID_ENCRYPTION_KEY)
    value = fernet.encrypt(str(value).encode())
    return value

@register.filter
def basename(value):
    if hasattr(value, 'name'):
        return os.path.basename(value.name)
    else:
        return os.path.basename(value)
