from rest_framework import generics, permissions

from .models import Filial
from .serializers import FilialSerializer


class FilialListCreateView(generics.ListCreateAPIView):
    serializer_class = FilialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Filial.objects.filter(esta_ativa=True)


class FilialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer
    permission_classes = [permissions.IsAuthenticated]
