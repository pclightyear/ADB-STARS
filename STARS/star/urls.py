from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('test_db/', views.test_db),
    path('profile/', views.profile),
    path('profile/submit', views.profile_submit),
    path('register/submit', views.register_submit),
    path('login/submit', views.login_submit),
    path('home/', views.home)
]