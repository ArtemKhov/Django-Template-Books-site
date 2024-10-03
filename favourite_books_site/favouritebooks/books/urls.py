from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('addpost/', views.add_post, name='add_post'),
    path('feedback/', views.feedback, name='feedback'),
]