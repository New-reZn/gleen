from django.contrib.auth.models import Group

# !imporatant : could not migrate until commented out

Admins,_ = Group.objects.get_or_create(name='Admins')
Developers,_ = Group.objects.get_or_create(name='Developers')
Reporters,_ = Group.objects.get_or_create(name='Reporters')