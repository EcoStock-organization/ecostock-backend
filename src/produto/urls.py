from django.urls import path

from .views import (
    ProdutoListCreateView, 
    ProdutoDetailView,
    CategoriaListCreateView,
    CategoriaDetailView
)

app_name = "produto"

urlpatterns = [
    path("", ProdutoListCreateView.as_view(), name="produto-lista-criar"),
    path("<int:pk>/", ProdutoDetailView.as_view(), name="produto-detalhe"),
    path('categorias/', CategoriaListCreateView.as_view(), name='categoria-lista-criar'),
    path('categorias/<int:pk>/', CategoriaDetailView.as_view(), name='categoria-detalhe'),
]
