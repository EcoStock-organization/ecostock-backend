from rest_framework import serializers
from .models import Produto, Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao']

class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    
    id_categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', required=False
    )

    class Meta:
        model = Produto
        fields = [
            'id', 'codigo_barras', 'nome', 'descricao', 
            'tipo_produto', 'esta_ativo', 
            'categoria_nome', 'id_categoria'
        ]
