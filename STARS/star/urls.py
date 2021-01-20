from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('test_db/', views.test_db),
    path('profile/', views.profile),
    path('profile/submit', views.profile_submit),
    path('register/submit', views.register_submit),
    path('login/submit', views.login_submit),
    path('home/', views.home),
    path('home/project-info-target', views.home_project_info_target),
    path('home/project-info-target/submit', views.home_project_info_target_submit),
    path('project/create-project/submit', views.project_create_project_submit),
    path('equipment/', views.equipment),
    path('equipment/add-equipment/submit', views.equipment_add_equipment_submit),
]