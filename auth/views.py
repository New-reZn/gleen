from django.shortcuts import render,redirect
from django.http import HttpResponse

# Create your views here.

def index(request):
    #TODO another "if" when not set up 
    
    print(request.user.is_authenticated)
    
    if not request.user.is_authenticated:
        return redirect("/signin")
        
    return HttpResponse("gleen welcomes you")

def signin(request):
    return render(request,"auth/signin.html")