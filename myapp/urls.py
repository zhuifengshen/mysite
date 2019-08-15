from django.urls import path
from . import views


app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('your-name/', views.get_name, name='your_name'),
]
