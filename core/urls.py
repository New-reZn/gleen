from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signin/",views.signin),
    path("signout/",views.signin),
    path("create_plan/",views.create_plan),
    path("change_plan/",views.change_plan),
    path("create_issue/",views.create_issue),
    path("create_issue/<int:status_id>/",views.create_issue),
    path("create_chart/",views.create_chart),
    path("kanban_change/",views.kanban_change),
    path("view_issue/<int:issue_id>/",views.view_issue),
    path("change_issue_details/<int:issue_id>/",views.change_detail),
    path("board_search/",views.board_search),
    path("table_search/",views.table_search),
    path("pin_issue/<int:issue_id>/",views.pin_issue),
    path("delete_issue/<int:issue_id>/",views.delete_issue),
    path("lock_issue/<int:issue_id>/",views.lock_issue),
]