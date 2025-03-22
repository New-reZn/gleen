from django.shortcuts import render,redirect
from django.http import HttpResponse
from setup.models import GlobalSettings
from gleen.helpers import gleen_authenticate
from django.contrib.auth import authenticate, login, logout
from core.models import User
from core.groups import *

# Create your views here.

@gleen_authenticate
def index(request):
    config=GlobalSettings.objects.first()
        
    data={
        "config":config,
        "title":f"{config.name}",
        "icon":f"{config.image.url}"  
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