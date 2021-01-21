from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('neo4jdb_test', views.neo4jdb_test),
    path('test_db', views.test_db),
    path('profile', views.profile),
    path('profile/submit', views.profile_submit),
    path('register', views.register),
    path('register/submit', views.register_submit),
    path('login', views.login),
    path('login/submit', views.login_submit),
    path('logout', views.logout),
    path('home', views.home),
    path('home/project-info-target', views.home_project_info_target),
    path('home/project-info-target/submit', views.home_project_info_target_submit),
    path('join-project', views.join_project),
    path('join-project/project-info-target', views.join_project_info),
    path('manage-project', views.manage_project),
    path('manage-project/project-info-target-equipment', views.manage_project_info),
    path('create-project', views.create_project),
    path('create-project/submit', views.create_project_submit),
    path('schedule', views.schedule),
    path('schedule/target-schedule', views.target_schedule),
    path('equipment/', views.equipment),
    path('equipment/add-equipment', views.add_equipment),
    path('equipment/add-equipment/submit', views.equipment_add_equipment_submit),
    path('relation',views.relation)
]