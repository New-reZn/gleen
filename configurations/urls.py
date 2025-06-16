from django.urls import path

from . import views

urlpatterns = [
    path("settings/",views.setting),
    path("change_profile/",views.change_profile),
    #profile CRUD
    path("search_plans/",views.search_plans),
    path("sort_plan/",views.sort_plans),
    path("plan_modification/<int:plan_id>/",views.update_plan),
    path("plan_deletion/<int:plan_id>/",views.delete_plan),
    #user CRUD
    path("create_user/",views.create_user),
    path("search_users/",views.search_users),
    path("sort_user/",views.sort_users),
    path("user_modification/<int:user_id>/",views.update_user),
    path("user_deletion/<int:user_id>/",views.delete_user),
    #status CRUD
    path("create_status/",views.create_status),
    path("search_status/",views.search_status),
    path("sort_status/",views.sort_status),
    path("status_modification/<int:status_id>/",views.update_status),
    path("status_deletion/<int:status_id>/",views.delete_status),
]