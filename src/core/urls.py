from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/produtos/", include("produto.urls")),
    path("api/filiais/", include("filial.urls")),
    path("api/filiais/<int:filial_pk>/estoque/", include("estoque.urls")),
    path("api/vendas/", include("venda.urls")),
    path('api/usuarios/', include('usuario.urls')),
]
