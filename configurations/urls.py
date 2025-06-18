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
    #priority CRUD
    path("create_priority/",views.create_priority),
    path("search_priority/",views.search_priority),
    path("sort_priority/",views.sort_priority),
    path("priority_modification/<int:priority_id>/",views.update_priority),
    path("priority_deletion/<int:priority_id>/",views.delete_priority),
    #types CRUD
    path("create_types/",views.create_types),
    path("search_types/",views.search_types),
    path("sort_types/",views.sort_types),
    path("types_modification/<int:type_id>/",views.update_types),
    path("types_deletion/<int:type_id>/",views.delete_types),
]