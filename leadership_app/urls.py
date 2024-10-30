from django.urls import path
from . import views

urlpatterns = [
    path('message/', views.prompt_chat, name="message"),
    path('', views.home, name='home'),
    path('completion', views.test_completion, name='completion'),
]
