from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("/setup/registerOrg",views.registerOrg,name="registerOrg")
]