from rest_framework import generics, permissions
from django.db.models import Count, Q
from .models import Filial
from .serializers import FilialSerializer

class FilialListCreateView(generics.ListCreateAPIView):
    serializer_class = FilialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Filial.objects.filter(esta_ativa=True).annotate(
            total_produtos=Count('itens_estoque', distinct=True),
            total_vendas=Count('venda', filter=Q(venda__status='FINALIZADA'), distinct=True)
        )

class FilialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Filial.objects.annotate(
            total_produtos=Count('itens_estoque', distinct=True),
            total_vendas=Count('venda', filter=Q(venda__status='FINALIZADA'), distinct=True)
    )
    serializer_class = FilialSerializer
    permission_classes = [permissions.IsAuthenticated]
