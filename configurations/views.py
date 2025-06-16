from django.shortcuts import redirect, render, HttpResponse
from core.models import *
from setup.models import GlobalSettings
from gleen.helpers import admin_privilege,htmx_required,get_object_or_none, sanitize_filename
from django.db.models import Q
from core.groups import *
from django.core.files.base import ContentFile
import os
from django.core.files.storage import default_storage

# Create your views here.

def setting(request):
    
    config=config=GlobalSettings.objects.first()
        
    return render(request,"setting.html",{
        "title":f"{config.name}:Settings",
        "icon":config.image.url,
        "config":config,
        "users":User.objects.all(),
        "plans":Plan.objects.all(),
        "statuses":Status.objects.all(),
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

@htmx_required
@admin_privilege
def create_user(request):
    if request.method=="POST":
        image=request.FILES.get("img")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        role=request.POST.get("role")        
        
        try:
            if role=="1":
                full_path ="admins/user.svg"
                if image:
                    file_path = os.path.join('admins/', sanitize_filename(image.name))
                    full_path=default_storage.save(file_path, ContentFile(image.read()))
                
                user=User.objects.create_superuser(username=username,email=email,password=password,is_admin=True)
                user.image = full_path
                user.groups.add(Admins)
                user.save()
                
            elif role=="2":
                full_path ="devs/user.svg"
                if image:
                    file_path = os.path.join('devs/', sanitize_filename(image.name))
                    full_path=default_storage.save(file_path, ContentFile(image.read()))
                    
                user=User.objects.create_user(username=username,password=password,email=email,is_developer=True)
                user.image = full_path
                user.groups.add(Developers)
                user.save()
                
            else:
                full_path ="reps/user.svg"
                if image:
                    file_path = os.path.join('reps/', sanitize_filename(image.name))
                    full_path=default_storage.save(file_path, ContentFile(image.read()))
                
                user=User.objects.create_user(username=username,email=email,password=password,is_reporter=True)
                user.image = full_path
                user.groups.add(Reporters)
                user.save()
            
            response = HttpResponse()
            response["HX-Redirect"] = "/settings/"
            return response
        except Exception as e:
            return HttpResponse(f"<p class='p-2'>{str(e)}</p>")

@htmx_required
def search_users(request):
    if request.method=="POST":
        search=request.POST['search'].strip()
        
        if search=="":
            users=User.objects.all()
        else:
            users=User.objects.filter(Q(username__icontains=search)|Q(email__icontains=search))
        
        return render(request,"component/user_table.html",{"users":users})
    else:
        return HttpResponse("<p>wrong request</p>")
    
@htmx_required
def sort_users(request):
    if request.method=="POST":
        search=request.POST["search"]
        choices=request.POST.getlist("choices")
        sort=request.POST['sort'].strip()
        
        role={
            "Admin":False,
            "Developer":False,
            "Reporter":False
        }
        
        for choice in choices:
            if choice == "0":
                role["Admin"] = True
            elif choice == "1":
                role["Developer"] = True
            elif choice == "2":
                role["Reporter"] = True
        
        if search=="":
            users=User.objects.all()
        else:  
            users=User.objects.filter(Q(username__icontains=search)|Q(email__icontains=search))
        
        role_q = Q()
        if role["Admin"]:
            role_q |= Q(is_admin=True)
        if role["Developer"]:
            role_q |= Q(is_developer=True)
        if role["Reporter"]:
            role_q |= Q(is_reporter=True)
            
        if role_q:
            users = users.filter(role_q)
        
        if sort=="1":
            users=users.order_by("-last_login")
        elif sort=="2":
            users=users.order_by("date_joined")
        elif sort=="3":
            users=users.order_by("username")
            
        return render(request,"component/user_table.html",{"users":users})
    else:
        return HttpResponse("<p>wrong request</p>")
    
@htmx_required
def delete_user(request,user_id):
    
    if request.method=="POST" and request.user.is_admin:
        user=get_object_or_none(User,id=user_id)
        if user:
            user.delete()
        return redirect("/settings/")
    
    user=get_object_or_none(User,id=user_id)
    
    if not user or not request.user.is_admin:
        return redirect("/settings/")
    
    return render(request,"component/confirm_deletion.html",{
      "object":user,
      "type":"user",
      "deletion_url":f"/user_deletion/{user.id}/"
    })

@htmx_required
@admin_privilege
def update_user(request,user_id):
    
    if request.method=="POST":
        image=request.FILES.get("img")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        role=request.POST.get("role")
        
        user=get_object_or_none(User,id=user_id)
        
        if username and user.username!=username:
            user.username = username.strip()
        
        if email and user.email!=email:
            user.email = email.strip()
        
        if password.strip():
            user.set_password(password.strip()) 
        
        try:
            if role=="1":
                if image:
                    if user.image and default_storage.exists(user.image.name):
                        default_storage.delete(user.image.name)

                    file_path = os.path.join('admins/', sanitize_filename(image.name))
                    full_path = default_storage.save(file_path, ContentFile(image.read()))
                    user.image = full_path
                
                user.is_admin=True
                user.is_developer=False
                user.is_reporter=False
                user.groups.clear()
                user.groups.add(Admins)
                user.save()
                
            elif role=="2":
                if image:
                    if user.image and default_storage.exists(user.image.name):
                        default_storage.delete(user.image.name)

                    file_path = os.path.join('devs/', sanitize_filename(image.name))
                    full_path = default_storage.save(file_path, ContentFile(image.read()))
                    user.image = full_path
                
                user.is_admin=False
                user.is_developer=True
                user.is_reporter=False    
                user.groups.clear()
                user.groups.add(Developers)
                user.save()
                
            else:
                if image:
                    if user.image and default_storage.exists(user.image.name):
                        default_storage.delete(user.image.name)

                    file_path = os.path.join('reps/', sanitize_filename(image.name))
                    full_path = default_storage.save(file_path, ContentFile(image.read()))
                    user.image = full_path

                user.is_admin=False
                user.is_developer=False
                user.is_reporter=True
                user.groups.clear()
                user.groups.add(Reporters)
                user.save()
            
            response = HttpResponse()
            response["HX-Redirect"] = "/settings/"
            return response
        
        except Exception as e:
            return HttpResponse(f"<p class='p-2'>{str(e)}</p>")
    
    user=get_object_or_none(User,id=user_id)
    
        
    if not user:
        response = HttpResponse()
        response["HX-Redirect"] = "/settings/"
        return response

    return render(request,"component/modify_user.html",{
        "user":user,
        "preview_id": f"user_img_modify_preview_{user.id}",
        "input_id":   f"user_img_modify_input_{user.id}",
    })

@htmx_required
@admin_privilege
def create_status(request):
    
    if request.method=="POST":
        name= request.POST["name"]
        desc= request.POST["desc"]
        color= request.POST["color"]
        
        plans= request.POST.getlist("plans")
        creator = request.user
        
        
        try:
            
            plans=Plan.objects.filter(id__in=plans)
            
            status=Status.objects.create(creator=creator,name=name,desc=desc,color=color)
            
            if plans:
                status.plan.set(plans)
                status.save()
                
            response = HttpResponse()
            response["HX-Redirect"] = "/settings/"
            return response
        
        except Exception as e:
            return HttpResponse(f"<p class='p-2'>{str(e)}</p>")
        
    return render(request,"component/create_status.html",{"plans":Plan.objects.all()})

@htmx_required
def search_status(request):
    if request.method=="POST":
        search=request.POST['search'].strip()
        
        if search=="":
            status=Status.objects.all()
        else:
            status=Status.objects.filter(Q(name__icontains=search)|Q(desc__icontains=search))
        
        return render(request,"component/status_table.html",{"statuses":status})
    else:
        return HttpResponse("<p>wrong request</p>")
    
@htmx_required
def sort_status(request):
    if request.method=="POST":
        search=request.POST["search"]
        choices=request.POST.getlist("choices-plan-status")
        sort=request.POST['sort'].strip()
        
        plans=Plan.objects.filter(id__in=choices)
        
        status = Status.objects.all()

        if search:
            status = status.filter(Q(name__icontains=search) | Q(desc__icontains=search))

        if plans:
            status = status.filter(plan__id__in=choices).distinct()
        
        if sort=="1":
            status=status.order_by("created_on")
        elif sort=="2":
            status=status.order_by("updated_on")
        elif sort=="3":
            status=status.order_by("name")
            
        return render(request,"component/status_table.html",{"statuses":status})
    else:
        return HttpResponse("<p>wrong request</p>")
    

@htmx_required
def delete_status(request,status_id):
    
    if request.method=="POST" and request.user.is_admin:
        status=get_object_or_none(Status,id=status_id)
        if status:
            status.delete()
        return redirect("/settings/")
    
    status=get_object_or_none(Status,id=status_id)
    
    if not status or not request.user.is_admin:
        return redirect("/settings/")
    
    return render(request,"component/confirm_deletion.html",{
      "object":status,
      "type":"status",
      "deletion_url":f"/status_deletion/{status.id}/"
    })

@htmx_required
@admin_privilege
def update_status(request,status_id):
    
    if request.method=="POST":
        name= request.POST["name"]
        desc= request.POST["desc"]
        color= request.POST["color"]
        
        plans= request.POST.getlist("plans")
        
        status = get_object_or_none(Status,id=status_id)
        
        print(status)
        if name and status.name!=name:
            status.name = name.strip()
        
        if desc and status.desc!=desc:
            status.desc = desc.strip()
        
        if color and status.color!=color:
            status.color = color.strip() 
        
        try:
            plans=Plan.objects.filter(id__in=plans)
            
            if plans:
                status.plan.set(plans)
                status.save()
            
            response = HttpResponse()
            response["HX-Redirect"] = "/settings/"
            return response
        
        except Exception as e:
            return HttpResponse(f"<p class='p-2'>{str(e)}</p>")
    
    status=get_object_or_none(Status,id=status_id)
    
        
    if not status:
        response = HttpResponse()
        response["HX-Redirect"] = "/settings/"
        return response

    return render(request,"component/modify_status.html",{
        "status":status,
        "plans":Plan.objects.all()
    })
