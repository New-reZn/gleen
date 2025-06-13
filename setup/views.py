from django.shortcuts import render, HttpResponse, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from  gleen.helpers import sanitize_filename
from  setup.models import GlobalSettings
from core.models import User
from core.groups import *
import os

# Create your views here.

def index(request):
    if GlobalSettings.objects.all().exists():
        return redirect('/')
    
    data={
        "title":"Gleen setup",
        "icon":"/static/img/logo-sm.svg"  
    }
    
    return render(request,"setup/setup.html",data)

def registerOrg(request):
    if not (request.POST and request.htmx):
        return HttpResponse("<p>wrong request</p>")
    
    name = request.POST.get('name')
    goal = request.POST.get('goal')        
    image = request.FILES.get('img')
    
    if not (name and  goal):
        return HttpResponse("<p>wrong request</p>")
        
    full_path ="global/logo.svg"
    if image:
        file_path = os.path.join('global/', sanitize_filename(image.name))
        full_path=default_storage.save(file_path, ContentFile(image.read()))
        
    content={
        "name":name,
        "goal":goal,
        "path":full_path
    }
    
    return render(request,"component/create_super_admin.html",content)
    

def setup(request):
    if not request.POST:
        return redirect("/setup")
    
    username = request.POST['username']
    password = request.POST['password']
    image = request.FILES.get('img')
    
    org_name = request.POST['orgName']
    org_goal = request.POST['orgGoal']
    org_path = request.POST['orgPath']
    
    GlobalSettings.objects.create(name=org_name,goal=org_goal,image=org_path).save()
    
    full_path ="admins/user.svg"
    
    if image:
        file_path = os.path.join('admins/', sanitize_filename(image.name))
        full_path=default_storage.save(file_path, ContentFile(image.read()))
    
    user=User.objects.create_superuser(username=username,password=password,is_admin=True)
    user.image = full_path
    user.groups.add(Admins)
    
    user.save()
    
    return redirect("/")