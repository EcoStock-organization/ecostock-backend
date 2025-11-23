from django.urls import path
from .views import CriarUsuarioView


app_name = 'usuario'

urlpatterns = [
    path('criar/', CriarUsuarioView.as_view(), name='criar-usuario'),
]
