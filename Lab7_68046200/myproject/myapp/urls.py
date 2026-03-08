from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact),
    path('form/', views.form),
]