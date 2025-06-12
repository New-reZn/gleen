from setup.models import GlobalSettings
from django.shortcuts import redirect,HttpResponse
from django.shortcuts import _get_queryset
import re
import unicodedata
import uuid

def get_object_or_none(Class, *args, **kwargs):
    queryset = _get_queryset(Class)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None

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


def htmx_required(view_func):
    def wrapper(request, *args, **kwargs):
        
        if not request.user.is_authenticated:
            return HttpResponse("<p>invalid call</p>")
        
        if request.htmx:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse("<p>invalid call</p>")
        
    return wrapper


def admin_privilege(view_func):
    def wrapper(request, *args, **kwargs):
        
        if request.user.is_admin:
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return HttpResponse("<p>invalid call</p>")
        
    return wrapper


def dev_privilege(view_func):
    def wrapper(request, *args, **kwargs):
        
        if request.user.is_developer:
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return HttpResponse("<p>invalid call</p>")
        
    return wrapper

def rep_privilege(view_func):
    def wrapper(request, *args, **kwargs):
        
        if request.user.is_reporter:
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return HttpResponse("<p>invalid call</p>")
        
    return wrapper
