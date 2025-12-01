from rest_framework import serializers
from .models import Filial

class FilialSerializer(serializers.ModelSerializer):
    total_produtos = serializers.IntegerField(read_only=True)
    total_vendas = serializers.IntegerField(read_only=True)

    class Meta:
        model = Filial
        fields = [
            "id", "nome", "cep", "logradouro", "cidade",
            "estado", "gerente_id", "esta_ativa",
            "total_produtos", "total_vendas"
        ]
        read_only_fields = ["esta_ativa"]
