from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/",views.registerOrg),
    path("create/",views.setup),
]