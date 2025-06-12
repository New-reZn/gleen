from django.urls import path

from . import views

urlpatterns = [
    path("settings/",views.setting),
    path("change_profile/",views.change_profile),
    path("search_plans/",views.search_plans),
    path("sort_plan/",views.sort_plans),
    path("plan_deletion/<int:plan_id>/",views.delete_plan),
    path("plan_modification/<int:plan_id>/",views.update_plan),
]