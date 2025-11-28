from django.contrib import admin
from django.urls import include, path
from .views import (
    DashboardMetricsView, 
    RecentSalesView, 
    StockAlertsView,
    SalesChartDataView,      # Nova
    CategoryPerformanceView  # Nova
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/produtos/", include("produto.urls")),
    path("api/filiais/", include("filial.urls")),
    path("api/filiais/<int:filial_pk>/estoque/", include("estoque.urls")),
    path("api/vendas/", include("venda.urls")),
    path('api/usuarios/', include('usuario.urls')),
    path('api/relatorios/', include('relatorios.urls')),
    
    # Dashboard
    path('api/dashboard/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('api/dashboard/recent-sales/', RecentSalesView.as_view(), name='dashboard-recent-sales'),
    path('api/dashboard/alerts/', StockAlertsView.as_view(), name='dashboard-alerts'),

    # Relatórios (Charts)
    path('api/reports/sales-chart/', SalesChartDataView.as_view(), name='reports-sales-chart'),
    path('api/reports/category-chart/', CategoryPerformanceView.as_view(), name='reports-category-chart'),
]