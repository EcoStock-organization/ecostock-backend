from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Sum, F, FloatField
from django.db.models.functions import TruncMonth, Coalesce
from django.utils import timezone
from datetime import timedelta
import logging

# Configura logger para ver erros no terminal do docker
logger = logging.getLogger(__name__)

# Models
from venda.models import Venda, ItemVenda
from estoque.models import ItemEstoque
from filial.models import Filial

# Serializers
from venda.serializers import VendaSerializer
from estoque.serializers import ItemEstoqueSerializer

class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            total_revenue = Venda.objects.filter(status='FINALIZADA').aggregate(soma=Sum('valor_total'))['soma'] or 0
            total_sales = Venda.objects.filter(status='FINALIZADA').count()
            low_stock_items = ItemEstoque.objects.filter(quantidade_atual__lte=F('quantidade_minima_estoque')).count()
            active_branches = Filial.objects.filter(esta_ativa=True).count()

            return Response({
                "totalRevenue": float(total_revenue),
                "totalSales": total_sales,
                "lowStockItems": low_stock_items,
                "activeBranches": active_branches,
                "revenueGrowth": 12.5, 
                "salesGrowth": 8.2
            })
        except Exception as e:
            logger.error(f"Erro no DashboardMetrics: {str(e)}")
            return Response({"error": str(e)}, status=500)

class RecentSalesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VendaSerializer

    def get_queryset(self):
        return Venda.objects.filter(status='FINALIZADA').order_by('-data_venda')[:5]

class StockAlertsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemEstoqueSerializer

    def get_queryset(self):
        return ItemEstoque.objects.filter(quantidade_atual__lte=F('quantidade_minima_estoque'))

# --- RELATÓRIOS ---

class SalesChartDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            six_months_ago = timezone.now() - timedelta(days=180)
            
            sales_data = Venda.objects.filter(
                status='FINALIZADA',
                data_venda__gte=six_months_ago
            ).annotate(
                month=TruncMonth('data_venda')
            ).values('month').annotate(
                receita=Sum('valor_total')
            ).order_by('month')

            formatted_data = []
            for entry in sales_data:
                if entry['month']: # Garante que mês não é nulo
                    receita_float = float(entry['receita'] or 0)
                    formatted_data.append({
                        "month": entry['month'].strftime('%b'),
                        "receita": receita_float,
                        "custo": receita_float * 0.6
                    })
            
            return Response(formatted_data)
        except Exception as e:
            logger.error(f"Erro no SalesChartData: {str(e)}")
            return Response({"error": str(e)}, status=500)

class CategoryPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # CORREÇÃO CRÍTICA: output_field=FloatField() é necessário ao multiplicar Decimal por Float
            category_data = ItemVenda.objects.filter(
                venda__status='FINALIZADA'
            ).values(
                'produto__categoria__nome'
            ).annotate(
                total=Sum(
                    F('preco_vendido') * F('quantidade_vendida'),
                    output_field=FloatField()
                )
            ).order_by('-total')

            formatted_data = []
            for entry in category_data:
                name = entry['produto__categoria__nome'] or "Outros"
                total_val = float(entry['total'] or 0)
                
                formatted_data.append({
                    "name": name,
                    "value": round(total_val, 2)
                })

            return Response(formatted_data)
        except Exception as e:
            logger.error(f"Erro no CategoryPerformance: {str(e)}")
            return Response({"error": str(e)}, status=500)