from django.shortcuts import redirect, render
from core.models import *
from setup.models import GlobalSettings
from gleen.helpers import admin_privilege

# Create your views here.

def setting(request):
    
    config=config=GlobalSettings.objects.first()
        
    return render(request,"setting.html",{
        "title":f"{config.name}:Settings",
        "icon":config.image.url,
        "config":config,
        "users":User.objects.all(),
        "plans":Plan.objects.all(),
        "issues":Issues.objects.all(),
        "priorities":Priority.objects.all(),
        "types":Types.objects.all(),
    })
    
@admin_privilege
def change_profile(request):
    if request.method=="POST":
        title=request.POST.get("title")
        image=request.FILES.get("img")
        desc=request.POST.get("desc")

        config=GlobalSettings.objects.first()        

        if image:
            config.image=image
        
        if title and config.name!=title:
            config.name=title
            
        if desc and config.goal!=desc:
            config.goal=desc
        
        config.save()
        
    return redirect("/settings/")