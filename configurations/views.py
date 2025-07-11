from django.shortcuts import redirect, render, HttpResponse
from core.models import *
from setup.models import GlobalSettings
from gleen.helpers import admin_privilege,htmx_required,get_object_or_none, sanitize_filename
from django.db.models import Q
from core.groups import *
from django.core.files.base import ContentFile
import os
from django.core.files.storage import default_storage
from .models import NotificationPreferences

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
        "prefs":NotificationPreferences.objects.get_or_create(user=request.user)[0]
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
            
            NotificationPreferences.objects.create(user)
            
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
        
        if name and status.name!=name:
            status.name = name.strip()
        
        if desc and status.desc!=desc:
            status.desc = desc.strip()
        
        if color and status.color!=color:
            status.color = color.strip() 
        
        try:
            plans=Plan.objects.filter(id__in=plans)
            
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
    
    selected_plan_ids = list(
        status.plan.values_list('id', flat=True)
    )

    return render(request,"component/modify_status.html",{
        "status":status,
        "plans":Plan.objects.all(),
        "selected_plan_ids": selected_plan_ids,
    })

@htmx_required
@admin_privilege
def create_priority(request):
    
    if request.method=="POST":
        name= request.POST["name"]
        desc= request.POST["desc"]
        color= request.POST["color"]
        
        plans= request.POST.getlist("plans")
        creator = request.user
        
        try:
            
            plans=Plan.objects.filter(id__in=plans)
            
            priority=Priority.objects.create(creator=creator,name=name,desc=desc,color=color)
            
            if plans:
                priority.plan.set(plans)
                priority.save()
                
            response = HttpResponse()
            response["HX-Redirect"] = "/settings/"
            return response
        
        except Exception as e:
            return HttpResponse(f"<p class='p-2'>{str(e)}</p>")
        
    return render(request,"component/create_priority.html",{"plans":Plan.objects.all()})

@htmx_required
def search_priority(request):
    if request.method=="POST":
        search=request.POST['search'].strip()
        
        if search=="":
            priority=Priority.objects.all()
        else:
            priority=Priority.objects.filter(Q(name__icontains=search)|Q(desc__icontains=search))
        
        return render(request,"component/priority_table.html",{"priorities":priority})
    else:
        return HttpResponse("<p>wrong request</p>")
    
@htmx_required
def sort_priority(request):
    if request.method=="POST":
        search=request.POST["search"]
        choices=request.POST.getlist("choices-plan-status")
        sort=request.POST['sort'].strip()
        
        plans=Plan.objects.filter(id__in=choices)
        
        priority = Priority.objects.all()

        if search:
            priority = priority.filter(Q(name__icontains=search) | Q(desc__icontains=search))

        if plans:
            priority = priority.filter(plan__id__in=choices).distinct()
        
        if sort=="1":
            priority=priority.order_by("created_on")
        elif sort=="2":
            priority=priority.order_by("updated_on")
        elif sort=="3":
            priority=priority.order_by("name")
            
        return render(request,"component/priority_table.html",{"priorities":priority})
    else:
        return HttpResponse("<p>wrong request</p>")
    
@htmx_required
def delete_priority(request,priority_id):
    
    if request.method=="POST" and request.user.is_admin:
        priority=get_object_or_none(Priority,id=priority_id)
        if priority:
            priority.delete()
        return redirect("/settings/")
    
    priority=get_object_or_none(Priority,id=priority_id)
    
    if not priority or not request.user.is_admin:
        return redirect("/settings/")
    
    return render(request,"component/confirm_deletion.html",{
      "object":priority,
      "type":"priority",
      "deletion_url":f"/priority_deletion/{priority.id}/"
    })

@htmx_required
@admin_privilege
def update_priority(request,priority_id):
    
    if request.method=="POST":
        name= request.POST["name"]
        desc= request.POST["desc"]
        color= request.POST["color"]
        
        plans= request.POST.getlist("plans")
        
        priority = get_object_or_none(Priority,id=priority_id)
        
        if name and priority.name!=name:
            priority.name = name.strip()
        
        if desc and priority.desc!=desc:
            priority.desc = desc.strip()
        
        if color and priority.color!=color:
            priority.color = color.strip() 
        
        try:
            plans=Plan.objects.filter(id__in=plans)
            
            priority.plan.set(plans)    
            priority.save()
            
            response = HttpResponse()
            response["HX-Redirect"] = "/settings/"
            return response
        
        except Exception as e:
            return HttpResponse(f"<p class='p-2'>{str(e)}</p>")
    
    priority=get_object_or_none(Priority,id=priority_id)
    
        
    if not priority:
        response = HttpResponse()
        response["HX-Redirect"] = "/settings/"
        return response
    
    selected_plan_ids = list(
        priority.plan.values_list('id', flat=True)
    )

    return render(request,"component/modify_priority.html",{
        "priority":priority,
        "plans":Plan.objects.all(),
        "selected_plan_ids": selected_plan_ids,
    })

@htmx_required
@admin_privilege
def create_types(request):
    
    if request.method=="POST":
        name= request.POST["name"]
        desc= request.POST["desc"]
        color= request.POST["color"]
        
        plans= request.POST.getlist("plans")
        creator = request.user
        
        try:
            
            plans=Plan.objects.filter(id__in=plans)
            
            type=Types.objects.create(creator=creator,name=name,desc=desc,color=color)
            
            if plans:
                type.plan.set(plans)
                type.save()
                
            response = HttpResponse()
            response["HX-Redirect"] = "/settings/"
            return response
        
        except Exception as e:
            return HttpResponse(f"<p class='p-2'>{str(e)}</p>")
        
    return render(request,"component/create_types.html",{"plans":Plan.objects.all()})

@htmx_required
def search_types(request):
    if request.method=="POST":
        search=request.POST['search'].strip()
        
        if search=="":
            types=Types.objects.all()
        else:
            types=Types.objects.filter(Q(name__icontains=search)|Q(desc__icontains=search))
        
        return render(request,"component/types_table.html",{"types":types})
    else:
        return HttpResponse("<p>wrong request</p>")
    
@htmx_required
def sort_types(request):
    if request.method=="POST":
        search=request.POST["search"]
        choices=request.POST.getlist("choices-plan-status")
        sort=request.POST['sort'].strip()
        
        plans=Plan.objects.filter(id__in=choices)
        
        types = Types.objects.all()

        if search:
            types = types.filter(Q(name__icontains=search) | Q(desc__icontains=search))

        if plans:
            types = types.filter(plan__id__in=choices).distinct()
        
        if sort=="1":
            types=types.order_by("created_on")
        elif sort=="2":
            types=types.order_by("updated_on")
        elif sort=="3":
            types=types.order_by("name")
            
        return render(request,"component/types_table.html",{"types":types})
    else:
        return HttpResponse("<p>wrong request</p>")
    
@htmx_required
def delete_types(request,type_id):
    
    if request.method=="POST" and request.user.is_admin:
        types=get_object_or_none(Types,id=type_id)
        if types:
            types.delete()
        return redirect("/settings/")
    
    types=get_object_or_none(Types,id=type_id)
    
    if not types or not request.user.is_admin:
        return redirect("/settings/")
    
    return render(request,"component/confirm_deletion.html",{
      "object":types,
      "type":"type",
      "deletion_url":f"/types_deletion/{types.id}/"
    })

@htmx_required
@admin_privilege
def update_types(request,type_id):
    
    if request.method=="POST":
        name= request.POST["name"]
        desc= request.POST["desc"]
        color= request.POST["color"]
        
        plans= request.POST.getlist("plans")
        
        types = get_object_or_none(Types,id=type_id)
        
        if name and types.name!=name:
            types.name = name.strip()
        
        if desc and types.desc!=desc:
            types.desc = desc.strip()
        
        if color and types.color!=color:
            types.color = color.strip() 
        
        try:
            plans=Plan.objects.filter(id__in=plans)
            
            types.plan.set(plans)    
            types.save()
            
            response = HttpResponse()
            response["HX-Redirect"] = "/settings/"
            return response
        
        except Exception as e:
            return HttpResponse(f"<p class='p-2'>{str(e)}</p>")
    
    types=get_object_or_none(Types,id=type_id)
    
        
    if not types:
        response = HttpResponse()
        response["HX-Redirect"] = "/settings/"
        return response
    
    selected_plan_ids = list(
        types.plan.values_list('id', flat=True)
    )

    return render(request,"component/modify_types.html",{
        "types":types,
        "plans":Plan.objects.all(),
        "selected_plan_ids": selected_plan_ids,
    })

def update_notification_preference(request):
    prefs = request.user.notification_preferences

    if request.method == "POST":
        # For each boolean field, update from POST (“True” if present)
        for field in [
            "issue_assigned", "issue_unassigned", "issue_status",
            "issue_priority", "issue_type", "issue_pinned",
            "issue_unpinned", "issue_locked", "issue_unlocked",
            "issue_name", "issue_desc",
        ]:
            setattr(prefs, field, field in request.POST)
        prefs.save()
    return redirect("/settings/")