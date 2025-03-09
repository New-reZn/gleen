from django.shortcuts import render, HttpResponse, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from  gleen.helpers import sanitize_filename
import os

# Create your views here.

def index(request):
    
    data={
        "title":"Gleen setup",
        "icon":"logo-sm.svg"  
    }
    
    return render(request,"setup/setup.html",data)

def registerOrg(request):
    if request.POST and request.htmx:
        name = request.POST.get('name')
        goal = request.POST.get('goal')        
        image = request.FILES.get('img')
        
        if name and goal:
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
    
    return HttpResponse("<p>😈</p>")