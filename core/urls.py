from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signin/",views.signin),
    path("signout/",views.signin),
    path("create_plan/",views.create_plan),
    path("change_plan/",views.change_plan),
    path("create_issue/",views.create_issue),
]