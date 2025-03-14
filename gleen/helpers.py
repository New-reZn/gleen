from setup.models import GlobalSettings
from django.shortcuts import redirect
import re
import unicodedata
import uuid


def sanitize_filename(filename):
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')

    filename = re.sub(r'[/\0:]', '_', filename)

    filename = filename.strip('. ')

    filename = filename[:255]

    return str(uuid.uuid4())+filename


def gleen_authenticate(view_func):
    def wrapper(request, *args, **kwargs):
        
        if not GlobalSettings.objects.all().exists():
            return redirect('/setup')
        
        if not request.user.is_authenticated:
            return redirect("/signin")
        
        return view_func(request, *args, **kwargs)
    return wrapper
