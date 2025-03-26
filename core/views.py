from django.shortcuts import render,redirect
from django.http import HttpResponse
from setup.models import GlobalSettings
from gleen.helpers import gleen_authenticate,admin_privilege
from django.contrib.auth import authenticate, login, logout
from core.models import *
from core.groups import *

# Create your views here.

@gleen_authenticate
def index(request):
    config=GlobalSettings.objects.first()
    
    print(Plan.objects.all())
    
    data={
        "config":config,
        "title":f"{config.name}",
        "icon":f"{config.image.url}",
        "plans":Plan.objects.all(),
    }
    
    return render(request,"home.html",data)


def signin(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']    
        
        user=authenticate(username=username,password=password)
        
        if not user:
            return redirect("/")
            
        login(request,user)        
        
        return redirect("/")    
    
    else:
        config=GlobalSettings.objects.first()
        
        data={
            "config":config,
            "title":f"{config.name} sign In",
            "icon":f"{config.image.url}"  
        }
        
        return render(request,"auth/signin.html",data)

def signout(request):
    logout(request);
    return redirect('/signin')


@admin_privilege
def create_plan(request):
    if request.method=="GET" and request.htmx:
        return render(request,"component/create_plan.html")
    elif request.method=="POST":
        name = request.POST['plan_name']
        desc = request.POST['plan_desc']
        
        Plan.objects.create(creator=request.user,name=name,desc=desc).save()
        
        return redirect(request.META.get('HTTP_REFERER', '/'))