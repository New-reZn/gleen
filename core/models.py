from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    image = models.ImageField(default="global/user.svg")
    is_admin = models.BooleanField(default=False)
    is_developer = models.BooleanField(default=False)
    is_reporter = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    
class Plan(models.Model):
    creator=models.ForeignKey("core.User", verbose_name="creator", on_delete=models.CASCADE,related_name="created_plans")
    
    name = models.CharField(max_length=100,null=False,unique=True)
    desc = models.TextField(null=False)
    
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class ChartObject(models.Model):
    #create/update ChartObject whenever issuse status is updated
    plan=models.ForeignKey("core.Plan", verbose_name="creator", on_delete=models.CASCADE)
    
    status= models.ForeignKey("core.Status",verbose_name="status", on_delete=models.CASCADE)
    
    created_on=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{ChartObject.objects.all().count()} {self.status}(s) on {self.created_on.strftime('%Y-%m-%d %H:%M:%S')}"
    
class Issues(models.Model):
    creator=models.ForeignKey("core.User", verbose_name="creator", on_delete=models.CASCADE,related_name="created_issue")
    plan=models.ForeignKey("core.Plan", verbose_name="plan", on_delete=models.CASCADE)
    
    assignees = models.ManyToManyField("core.User",verbose_name="assignees",related_name="assigned_to")
    
    priority = models.ForeignKey('core.Priority', on_delete=models.CASCADE,null=True)
    status = models.ForeignKey('core.Status', on_delete=models.CASCADE)
    type = models.ForeignKey('core.Types', on_delete=models.CASCADE,null=True)
    
    name = models.CharField(max_length=100,null=False,unique=True) 
    desc = models.TextField(null=False)
    
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    
    is_locked=models.BooleanField(default=False)
    is_pinned=models.BooleanField(default=False)
    
    pinned_for=models.ManyToManyField("core.User",verbose_name="pin",related_name="pinned_for")
    
    def save(self, *args, **kwargs):
        
        updater = kwargs.pop('updater', None)
        
        if not self.pk:
            super().save(*args, **kwargs)
            return
            
        
        og_issue = Issues.objects.get(pk=self.pk)
        
        og_assignees=og_issue.assignees.all()
        new_assignees=self.assignees.all()
        
        print("original : ",og_assignees)
        print("new : ",new_assignees)
        
        if set(og_assignees)!=set(new_assignees):
            
            added_assignees=[x for x in new_assignees if x not in og_assignees]
            
            Activities.objects.create(issue=self,subject=updater,verb="assigned issue to",object=", ".join(added_assignees),type="assigned")
            
            removed_assignees=[x for x in og_assignees if x not in new_assignees]
            
            Activities.objects.create(issue=self,subject=updater,verb="unassigned issue from",object=", ".join(removed_assignees),type="unassigned")
        
        if og_issue.status!=self.status:    
            ChartObject.objects.create(plan=self.plan,status=self.status)
            Activities.objects.create(issue=self,subject=updater,verb="changed status to",object=self.status,type="status")
            
        if og_issue.priority!=self.priority:
            Activities.objects.create(issue=self,subject=updater,verb="changed priority to",object=self.priority,type="priority")
            
        if og_issue.type!=self.type:
            Activities.objects.create(issue=self,subject=updater,verb="changed type to",object=self.type,type="type")
        
        if og_issue.is_pinned!=self.is_pinned:
            if self.is_pinned:
                Activities.objects.create(issue=self,subject=updater,verb="pinned",object=self.name,type="pinned")
            else:
                Activities.objects.create(issue=self,subject=updater,verb="unpinned",object=self.name,type="pinned")
            
        if og_issue.is_locked!=self.is_locked:
            if self.is_locked:
                Activities.objects.create(issue=self,subject=updater,verb="locked",object=self.name,type="locked")
            else:
                Activities.objects.create(issue=self,subject=updater,verb="unlocked",object=self.name,type="locked")
        
        if og_issue.name!=self.name:
            Activities.objects.create(issue=self,subject=updater,verb=f"changed issue name to",object=self.name,type="name",previous_name=og_issue.name)
        
        if og_issue.desc!=self.desc:
            Activities.objects.create(issue=self,subject=updater,verb=f"changed issue description to",object=self.desc,type="description",previous_desc=og_issue.desc)
        
        super().save(*args, **kwargs)
                    
    def __str__(self):
        return self.name


class Priority(models.Model):
    creator=models.ForeignKey("core.User", verbose_name="creator", on_delete=models.CASCADE,related_name="created_priority")
    plan=models.ManyToManyField("core.Plan", verbose_name="plan")
    
    name = models.CharField(max_length=100,null=False,unique=True)
    color = models.CharField(max_length=10,null=False) 
    desc = models.TextField(null=False)

    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Status(models.Model):
    creator=models.ForeignKey("core.User", verbose_name="creator", on_delete=models.CASCADE,related_name="created_status")
    plan=models.ManyToManyField("core.Plan", verbose_name="plan")
    
    name = models.CharField(max_length=100,null=False,unique=True)
    color = models.CharField(max_length=10,null=False) 
    desc = models.TextField(null=False)

    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    
class Types(models.Model):
    creator=models.ForeignKey("core.User", verbose_name="creator", on_delete=models.CASCADE,related_name="created_type")
    plan=models.ManyToManyField("core.Plan", verbose_name="plan")
    
    name = models.CharField(max_length=100,null=False,unique=True)
    color = models.CharField(max_length=10,null=False) 
    desc = models.TextField(null=False)

    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Activities(models.Model):
    issue=models.ForeignKey("core.Issues", verbose_name="issue", on_delete=models.CASCADE)
    
    subject=models.ForeignKey("core.User", verbose_name="creator", on_delete=models.CASCADE)
    verb=models.CharField(max_length=50)
    object=models.CharField(max_length=50)
    
    MODIFICATION_TYPE=[
        ("assigned","Assigned"),
        ("unassigned","Unassigned"),
        ("status","Status"),
        ("priority","Priority"),
        ("type","Type"),
        ("pinned","Pinned"),
        ("locked","Locked"),
        ("name","Name"),
        ("description","Description")
    ]
    
    type=models.CharField(max_length=20,null=False,choices=MODIFICATION_TYPE)
    previous_name=models.CharField(max_length=100,null=True,blank=True)
    previous_desc=models.TextField(null=True,blank=True)
    
    created_on=models.DateTimeField(auto_now_add=True)
    
    @property
    def model_name(self):
        return self._meta.model_name
    
    def __str__(self):
        return f"{self.subject} {self.verb} {self.object} on {self.created_on}"

class Comment(models.Model):
    creator=models.ForeignKey("core.User", verbose_name="creator", on_delete=models.CASCADE,related_name="created_comment")
    issue=models.ForeignKey("core.Issues", verbose_name="issue", on_delete=models.CASCADE)
    
    comment=models.TextField(null=False)
    
    commenting_on = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,related_name="replying_to")
    
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    
    
    @property
    def model_name(self):
        return self._meta.model_name
    
    def __str__(self):
        return f"{self.creator} commented \"{self.comment}\" on \"{self.issue.name}\""

class Files(models.Model):
    comment=models.ForeignKey("core.Comment", verbose_name="comment", on_delete=models.CASCADE)
    
    upload=models.FileField(upload_to="files",unique=True)
    
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.upload.name}"
