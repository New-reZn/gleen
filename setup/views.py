from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    
    data={
        "title":"Gleen setup",
        "icon":"logo-sm.svg"  
    }
    
    return render(request,"setup/setup.html",data)

def registerOrg(request):
    
    return HttpResponse("registerorg component")