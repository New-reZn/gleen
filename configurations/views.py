from django.shortcuts import redirect, render, HttpResponse
from core.models import *
from setup.models import GlobalSettings
from gleen.helpers import admin_privilege,htmx_required,get_object_or_none
from django.db.models import Q

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
        
    return redirect("settings/")

@htmx_required
def search_plans(request):
    if request.method=="POST":
        search=request.POST['search'].strip()
        
        if search=="":
            plans=Plan.objects.all()
        else:  
            plans=Plan.objects.filter(Q(name__icontains=search)|Q(desc__icontains=search)|Q(creator__username__icontains=search))
        
        return render(request,"component/plan_table.html",{"plans":plans})
    else:
        return HttpResponse("<p>wrong request</p>")
    
@htmx_required
def sort_plans(request):
    if request.method=="POST":
        search=request.POST['search'].strip()
        sort=request.POST['sort'].strip()
        
        if search=="":
            plans=Plan.objects.all()
        else:  
            plans=Plan.objects.filter(Q(name__icontains=search)|Q(desc__icontains=search)|Q(creator__username__icontains=search))
        
        if sort=="1":
            plans=plans.order_by("created_on")
        elif sort=="2":
            plans=plans.order_by("updated_on")
        elif sort=="3":
            plans=plans.order_by("name")
            
        print(plans,sort,search)
        
        return render(request,"component/plan_table.html",{"plans":plans})
    else:
        return HttpResponse("<p>wrong request</p>")

@htmx_required
def delete_plan(request,plan_id):
    
    if request.method=="POST" and request.user.is_admin:
        plan=get_object_or_none(Plan,id=plan_id)
        if plan:
            plan.delete()
        return redirect("/settings/")
    
    plan=get_object_or_none(Plan,id=plan_id)
    
    if not plan or not request.user.is_admin:
        return redirect("/settings/")
    
    return render(request,"component/confirm_deletion.html",{
      "object":plan,
      "type":"plan",
      "deletion_url":f"/plan_deletion/{plan.id}/"
    })
    

def update_plan(request,plan_id):
    if request.method=="POST" and request.user.is_admin:
        name=request.POST['plan_name']
        desc=request.POST['plan_desc']
        
        plan=get_object_or_none(Plan,id=plan_id)
        
        if plan:
            plan.name=name
            plan.desc=desc
            plan.save()
            
        return redirect("/settings/")
    
    plan=get_object_or_none(Plan,id=plan_id)
    
    if not plan or not request.user.is_admin:
        return redirect("/settings/")
    
    return render(request,"component/modify_plan.html",{
      "plan":plan,
    })
    