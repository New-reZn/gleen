from django.urls import path

from . import views

urlpatterns = [
    path("settings/",views.setting),
    path("change_profile/",views.change_profile)
]