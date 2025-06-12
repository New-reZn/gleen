from collections import defaultdict
from django.shortcuts import render,redirect
from django.http import HttpResponse
from setup.models import GlobalSettings
from gleen.helpers import gleen_authenticate,admin_privilege,get_object_or_none,htmx_required
from django.contrib.auth import authenticate, login, logout
from itertools import chain
from operator import attrgetter
from core.models import *
from core.groups import *
from django.conf import settings
from django.db.models import Count
from datetime import timedelta
import datetime

# Create your views here.

@gleen_authenticate
def index(request):
    cookies_current_plan=request.COOKIES.get("current_plan")
    
    config=GlobalSettings.objects.first()
    
    if Plan.objects.all().count()==0:
        data={
            "config":config,
            "title":f"{config.name}",
            "icon":f"{config.image.url}",
            "plan":None
        }
        
        return render(request,"home.html",data)
    
    if cookies_current_plan == None:
        current_plan=Plan.objects.latest('updated_on')
    else:
        current_plan=Plan.objects.filter(id=cookies_current_plan).first()
        
        if not current_plan:
            current_plan=Plan.objects.latest('updated_on')
    
    issues=current_plan.issues_set.all()
    ChartObjects=current_plan.chartobject_set.all()
    
    status=current_plan.status_set.all().order_by("created_on")
    
    mappings = {s.name: [] for s in status}
    
    end_date = datetime.date.today()  
    start_date = end_date - timedelta(days=30)
   
    days = (end_date - start_date).days + 1
    date_mapping=[]
    skip_day=1
    
    for day_offset in range(0,days,skip_day+1):
        
        current_date = start_date + timedelta(days=day_offset)
        date_mapping.append(current_date.strftime("%b %d"))
        
        count=(
            ChartObjects
            .filter(plan=current_plan)
            .filter(created_on__date__lte=current_date)
            .values('status__name')
            .annotate(count=Count('id'))
        )
        
        if not not count :
            for i in count:
                mappings[i["status__name"]].append(i["count"])
        else:
            for i in mappings.keys():
                mappings[i].append(0)
    
    data={
        "config":config,
        "title":f"{config.name}",
        "icon":f"{config.image.url}",
        "plan":current_plan,
        "issues":issues,
        "chartdata":mappings,
        "chartdate":date_mapping,
        "status":status
    }
    
    response=render(request,"home.html",data)
    
    response.set_cookie(
            key='current_plan',
            value=current_plan.id,
            max_age=2592000,       
            secure=settings.DEBUG,      
            httponly=True,     
            samesite='Lax'   
        )
    return response

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
        
        plan=Plan.objects.create(creator=request.user,name=name,desc=desc)
        plan.save()
        
        priorities_data=[
            {
                "creator":request.user,
                "name":"Critical",
                "color":"#FF0000",
                "desc":"Needs Critical evaluation"
            },
            {
                "creator":request.user,
                "name":"High",
                "color":"#FF7A00",
                "desc":"Major functionality broken"
            },
            {
                "creator":request.user,
                "name":"Medium",
                "color":"#FFD600",
                "desc":"Important but not blocking"
            },
            {
                "creator":request.user,
                "name":"Low",
                "color":"#9EFF00",
                "desc":"Minor issue"
            },
            {
                "creator":request.user,
                "name":"Lowest",
                "color":"#24FF00",
                "desc":"Nice to have"
            },
        ]
        
        status_data=[
            {
                "creator":request.user,
                "name":"Todo",
                "color":"#3fb950",
                "desc":"This item hasn't been started"
            },
            {
                "creator":request.user,
                "name":"In Progress",
                "color":"#d29922",
                "desc":"This is actively being worked on"
            },
            {
                "creator":request.user,
                "name":"Done",
                "color":"#ab7df8",
                "desc":"This has been completed"
            },
        ]
        
        types_data=[
            {
                "creator":request.user,
                "name":"bug",
                "color":"#d73a4a",
                "desc":"Something isn't working"
            },
            {
                "creator":request.user,
                "name":"documentation",
                "color":"#0075ca",
                "desc":"Improvements or additions to documentation"
            },
            {
                "creator":request.user,
                "name":"enhancement",
                "color":"#a2eeef",
                "desc":"New feature or request"
            },
            {
                "creator":request.user,
                "name":"help wanted",
                "color":"#008672",
                "desc":"Extra attention is needed"
            },
            {
                "creator":request.user,
                "name":"invalid",
                "color":"#e4e669",
                "desc":"This doesn't seem right"
            },
            {
                "creator":request.user,
                "name":"question",
                "color":"#d876e3",
                "desc":"Further information is requested"
            },
        ]
        
        priorities_name=set()
        status_name=set()
        types_name=set()    
        
        for priority in priorities_data:
            priorities_name.add(priority["name"])
            
        for status in status_data:
            status_name.add(status["name"])
            
        for type in types_data:
            types_name.add(type["name"])
            
        existing_priorities=Priority.objects.filter(name__in=priorities_name)
        existing_priorities_names = set(priority.name for priority in existing_priorities)
        
        existing_status=Status.objects.filter(name__in=status_name)
        existing_status_names = set(status.name for status in existing_status)
        
        existing_types=Types.objects.filter(name__in=types_name)
        existing_types_names = set(type.name for type in existing_types)
        
        new_priorities_names=priorities_name-existing_priorities_names
        new_status_names=status_name-existing_status_names
        new_types_names=types_name-existing_types_names
        
        if len(new_priorities_names)>0 and len(new_status_names)>0 and len(new_types_names)>0:
            new_priorities_data = [priority for priority in priorities_data if priority["name"] in new_priorities_names]
            new_status_data = [status for status in status_data if status["name"] in new_status_names]
            new_types_data = [type for type in types_data if type["name"] in new_types_names]
        
            priorities_objects = [
                Priority(
                    creator=priority["creator"],
                    name=priority["name"],
                    color=priority["color"],
                    desc=priority["desc"]
                )
                for priority in new_priorities_data
            ]
            
            status_objects = [
                Status(
                    creator=status["creator"],
                    name=status["name"],
                    color=status["color"],
                    desc=status["desc"]
                )
                for status in new_status_data
            ]
            
            type_objects = [
                Types(
                    creator=type["creator"],
                    name=type["name"],
                    color=type["color"],
                    desc=type["desc"]
                )
                for type in new_types_data
            ]
            
            Priority.objects.bulk_create(priorities_objects)
            Status.objects.bulk_create(status_objects)
            Types.objects.bulk_create(type_objects)
            
            for priority_object in priorities_objects:
                print(priority_object,priority_object.plan)
                priority_object.plan.add(plan)
                
            for status_object in status_objects:
                status_object.plan.add(plan)
                
            for type_object in type_objects:
                type_object.plan.add(plan)
            
        if existing_priorities.count()>0:
            for existing_priority in existing_priorities:
                existing_priority.plan.add(plan)
                existing_priority.save()
        
        if existing_status.count()>0:
            for existing_status in existing_status:
                existing_status.plan.add(plan)
                existing_status.save()
                
        if existing_types.count()>0:
            for existing_type in existing_types:
                existing_type.plan.add(plan)
                existing_type.save()
        
        response=redirect(request.META.get('HTTP_REFERER', '/'))
        
        response.set_cookie(
            key='current_plan',
            value=plan.id,
            max_age=2592000,       
            secure=settings.DEBUG,      
            httponly=True,     
            samesite='Lax'   
        )
        
        return response
    
def change_plan(request):
    if request.method=="GET" and request.htmx:
        data={
            "plans":Plan.objects.all(),
        }
        return render(request,"component/change_plan.html",data)
    elif request.method=="POST":
        plan_id = request.POST['plan_id']    
        
        plan=Plan.objects.filter(id=plan_id).first()
        
        if not plan:
            return HttpResponse("wrong request")
        
        response=redirect(request.META.get('HTTP_REFERER', '/'))
        
        response.set_cookie(
            key='current_plan',
            value=plan.id,
            max_age=2592000,      
            secure=settings.DEBUG,        
            httponly=True,     
            samesite='Lax'   
        )
        
        return response
    
@admin_privilege
def create_issue(request,status_id=None):
    if request.method=="GET" and request.htmx:
        cookies_current_plan=request.COOKIES.get("current_plan")
        if cookies_current_plan != None:
            current_plan=Plan.objects.filter(id=cookies_current_plan).first()
            if not current_plan:
                return HttpResponse("wrong request")
        else:
            current_plan=Plan.objects.latest('updated_on')
        
        status=get_object_or_none(current_plan.status_set,id=status_id)
        if status==None:
            status=current_plan.status_set.first()
        
        data={
            "plan":current_plan,
            "assignees":User.objects.all(),
            "types":current_plan.types_set.all(),
            "priorities":current_plan.priority_set.all(),
            "status":current_plan.status_set.all(),
            "current_status":status.id      
        }
        
        return render(request,"component/create_issue.html",data)
    elif request.method=="POST":
        
        assignees_input=request.POST.getlist('assignees')
        
        type_input=request.POST.get('type')
        
        title_input=request.POST.get('title')
        
        desc_input=request.POST.get('desc')
        
        files_input=request.FILES.getlist('files')
        
        priority_input=request.POST.get('priority')
        
        cookies_current_plan=request.COOKIES.get("current_plan")
        
        if cookies_current_plan != None:
            current_plan=Plan.objects.filter(id=cookies_current_plan).first()
        
            if not current_plan:
                return HttpResponse("wrong request")
        else:
            return HttpResponse("The issue did not had a plan")

        if status_id :
            default_status=get_object_or_none(current_plan.status_set,id=status_id)
        else:
            default_status=get_object_or_none(current_plan.status_set,name="Todo")
        
        default_priority=get_object_or_none(current_plan.priority_set,name=priority_input)
        
        default_type=get_object_or_none(current_plan.types_set,name=type_input)
        
        issue = Issues(
            creator=request.user,
            plan=current_plan,
            name=title_input,
            desc=desc_input
        )
        
        for assingee_id in assignees_input:
            assingee=User.objects.filter(id=assingee_id).first()
            if not assingee:
                return HttpResponse("wrong request")
            issue.assignees.add(assingee)
            
        
        if default_status==None:
            default_status=current_plan.status_set.all().order_by('created_on').first()
            
        issue.status=default_status
        
        if default_priority:
            issue.priority=default_priority
        else:
            try:
                issue.priority=current_plan.priority_set.get(name="Medium")
            except:
                issue.priority=current_plan.priority_set.first()
        
        if default_type:
            issue.type=default_type
        else:
            try:
                issue.type=current_plan.types_set.get(name="enhancement")
            except:
                issue.type=current_plan.types_set.first()
            
        issue.save(updater=request.user)
        ChartObject.objects.create(plan=current_plan,status=default_status)
        
        comment=Comment.objects.create(
            creator=request.user,
            issue=issue,
            comment=desc_input,
        )
        
        for fileObject in files_input:
            Files.objects.create(
                comment=comment,
                upload=fileObject
            )
            
        
        return redirect("/") 
    return redirect("/") 

def create_chart(request):
    if not (request.method=="POST" and request.htmx):
        return HttpResponse("wrong request")
    
    cookies_current_plan=request.COOKIES.get("current_plan")
    
    if cookies_current_plan != None:
        current_plan=Plan.objects.filter(id=cookies_current_plan).first()
        
        if not current_plan:
            return HttpResponse("wrong request")
    else:
        return HttpResponse("wrong request")
        
    text=request.POST.get("search").strip()
    time=request.POST.get("time").strip()
    
    if text=="":
        ChartObjects=ChartObject.objects.all()
    else:
        ChartObjects=ChartObject.objects.filter(status__name__icontains=text)
    
    
    status=current_plan.status_set.all()
    
    mappings = {s.name: [] for s in status}
    
    if time=="" or time=="1m":
        end_date = datetime.date.today()  
        start_date = end_date - timedelta(days=30)
    
        days = (end_date - start_date).days + 1
        date_mapping=[]
        skip_day=1
        
        for day_offset in range(0,days,skip_day+1):
            
            current_date = start_date + timedelta(days=day_offset)
            date_mapping.append(current_date.strftime("%b %d"))
            
            count=(
                ChartObjects
                .filter(plan=current_plan)
                .filter(created_on__date__lte=current_date)
                .values('status__name')
                .annotate(count=Count('id'))
            )
            
            if not not count :
                for i in count:
                    mappings[i["status__name"]].append(i["count"])
            else:
                for i in mappings.keys():
                    mappings[i].append(0)
            
    elif time=="2w":
        end_date = datetime.date.today()  
        start_date = end_date - timedelta(days=14)
    
        days = (end_date - start_date).days + 1
        date_mapping=[]
        skip_day=0
        
        for day_offset in range(0,days,skip_day+1):
            
            current_date = start_date + timedelta(days=day_offset)
            date_mapping.append(current_date.strftime("%b %d"))
            
            count=(
                ChartObjects
                .filter(plan=current_plan)
                .filter(created_on__date__lte=current_date)
                .values('status__name')
                .annotate(count=Count('id'))
            )
            
            if not not count :
                for i in count:
                    mappings[i["status__name"]].append(i["count"])
            else:
                for i in mappings.keys():
                    mappings[i].append(0)        
                
    elif time=="3m":
        end_date = datetime.date.today()  
        start_date = end_date - timedelta(days=90)
    
        days = (end_date - start_date).days + 1
        date_mapping=[]
        skip_day=3
        
        for day_offset in range(0,days,skip_day+1):
            
            current_date = start_date + timedelta(days=day_offset)
            date_mapping.append(current_date.strftime("%b %d"))
            
            count=(
                ChartObjects
                .filter(plan=current_plan)
                .filter(created_on__date__lte=current_date)
                .values('status__name')
                .annotate(count=Count('id'))
            )
            
            if not not count :
                for i in count:
                    mappings[i["status__name"]].append(i["count"])
            else:
                for i in mappings.keys():
                    mappings[i].append(0)
                       
    elif time=="MAX":
        end_date = datetime.date.today()
        
        earliest=ChartObject.objects.earliest("created_on")
        start_date = earliest.created_on.date()

        print(start_date,end_date)
        
        days = (end_date - start_date).days + 1
        date_mapping=[]
        skip_day=0
        
        if days<=7:
            start_date = earliest.created_on.date()-timedelta(days=2)
            days = (end_date - start_date).days + 1
        elif days<=30:
            skip_day=1   
        elif days<=90:
            skip_day=3
        else:
            skip_day=(days//30)-1
            
        for day_offset in range(0,days,skip_day+1):
            
            current_date = start_date + timedelta(days=day_offset)
            date_mapping.append(current_date.strftime("%b %d"))
            
            count=(
                ChartObjects
                .filter(plan=current_plan)
                .filter(created_on__date__lte=current_date)
                .values('status__name')
                .annotate(count=Count('id'))
            )
            
            if not not count :
                for i in count:
                    mappings[i["status__name"]].append(i["count"])
            else:
                for i in mappings.keys():
                    mappings[i].append(0)
                    
    else:
        return HttpResponse("wrong request")
    
    return render(request,"component/chart.html",{"chartdata":mappings,"chartdate":date_mapping})

@htmx_required
def kanban_change(request):
    if request.method=="POST" and (request.user.is_admin or request.user.is_developer):
        status_id=request.POST.get("status")
        issue_id=request.POST.get("latest_issue")
        
        status=Status.objects.filter(id=status_id).first()
        
        if not status:
            return HttpResponse("wrong request")
        
        issue=Issues.objects.filter(id=issue_id).first()
        if not issue:
            return HttpResponse("wrong request")
        
        issue.status=status
        issue.save(updater=request.user)
        
        print("new_status:",status,"new_issues:",issue)
        return HttpResponse("ok")
    
@htmx_required
def view_issue(request,issue_id):
    if request.method=="GET":
        cookies_current_plan=request.COOKIES.get("current_plan")
        if cookies_current_plan != None:
            current_plan=Plan.objects.filter(id=cookies_current_plan).first()
            
            if not current_plan:
                return HttpResponse("wrong request")
            
        else:
            current_plan=Plan.objects.latest('updated_on')
        
        issue=Issues.objects.filter(id=issue_id).first()
        
        if not issue:
            return HttpResponse("wrong request")
        
        comments=Comment.objects.filter(issue=issue)
        logs=Activities.objects.filter(issue=issue)
        
        thread_data=sorted(chain(comments,logs),key=attrgetter('created_on'))
        
        assigneed_assignees=issue.assignees.all().union(
            User.objects.filter(pk=issue.creator.pk)
        )
        
        if not issue:
            return HttpResponse("wrong request")

        
        data={
            "plan":current_plan,
            "assignees":User.objects.all(),
            "assigneed_assignees":assigneed_assignees,
            "types":current_plan.types_set.all(),
            "priorities":current_plan.priority_set.all(),
            "status":current_plan.status_set.all(),      
            "issue":issue,
            "thread":thread_data,
        }
        

        return render(request,"component/view_issue.html",data)
    elif request.method=="POST" :
        comment=request.POST.get("comment")

        issue=Issues.objects.filter(id=issue_id).first()
        
        if not issue:
            return HttpResponse("failed to comment")
        
        Comment.objects.create(
            creator=request.user,
            issue=issue,
            comment=comment
        )
    
        return HttpResponse("")
        
    return redirect("/")

def change_detail(request,issue_id):
    if request.method=="POST":
        priority=request.POST.get("priority")
        status=request.POST.get("status")
        add_assignees=request.POST.getlist('add-assignees')
        type=request.POST.get("type")
        
        issue=Issues.objects.filter(id=issue_id).first()
        priority=Priority.objects.filter(name=priority).first()
        type=Types.objects.filter(name=type).first()
        status=Status.objects.filter(name=status).first()
        
        if not issue or not priority or not status or not type:
            return redirect("/")
        
        issue.assignees.clear()
        for i in add_assignees:
            assignee=User.objects.filter(id=i).first()
            if assignee==issue.creator:
                pass
            if not assignee:
                return redirect("/")
            issue.assignees.add(assignee)
            
        print("here",priority)
        issue.priority=priority
        issue.type=type
        issue.status=status
        
        issue.save(updater=request.user)
        
    return redirect("/")

def board_search(request):
    if request.htmx and request.method=="POST":
        text=request.POST.get("search")
        
        if text=="":
            status=Status.objects.all()
        else:
            status=Status.objects.filter(name__icontains=text)
            
        issues=Issues.objects.filter(status__in=status)
        
        return render(request,"component/kanban.html",{"status":status,"issues":issues})
        
def table_search(request):
    if request.htmx and request.method=="POST":
        text=request.POST.get("search")
        
        if text=="":
            issues=Issues.objects.all()
        else:
            issues=Issues.objects.filter(name__icontains=text)
        
        return render(request,"component/table.html",{"issues":issues})
