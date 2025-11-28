from rest_framework import serializers
from .models import Venda, ItemVenda
from estoque.models import ItemEstoque
from django.db import transaction

class ItemVendaSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    
    class Meta:
        model = ItemVenda
        fields = ['id', 'produto', 'produto_nome', 'quantidade_vendida', 'preco_vendido']

class VendaSerializer(serializers.ModelSerializer):
    itens = ItemVendaSerializer(source='itens_venda', many=True, read_only=True)
    
    class Meta:
        model = Venda
        fields = ['id', 'data_venda', 'valor_total', 'status', 'forma_pagamento', 'filial', 'usuario_id', 'itens']
        read_only_fields = ['valor_total', 'status', 'data_venda', 'usuario_id']

class AdicionarItemVendaSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField()
    quantidade = serializers.FloatField(min_value=0.01)

    def validate(self, data):
        venda = self.context['venda']
        
        if venda.status != Venda.StatusVenda.ABERTA:
             raise serializers.ValidationError("Não é possível adicionar itens a uma venda finalizada.")

        try:
            item_estoque = ItemEstoque.objects.get(
                filial=venda.filial,
                produto_id=data['produto_id']
            )
        except ItemEstoque.DoesNotExist:
            raise serializers.ValidationError("Produto não encontrado no estoque desta filial.")

        if item_estoque.quantidade_atual < data['quantidade']:
            raise serializers.ValidationError(f"Estoque insuficiente. Disponível: {item_estoque.quantidade_atual}")

        data['item_estoque'] = item_estoque
        return data

    def create(self, validated_data):
        venda = self.context['venda']
        item_estoque = validated_data['item_estoque']
        quantidade = validated_data['quantidade']
        produto = item_estoque.produto

        with transaction.atomic():
            # 1. Cria ou recupera o item na venda
            item_venda, created = ItemVenda.objects.get_or_create(
                venda=venda,
                produto=produto,
                defaults={
                    'quantidade_vendida': 0,
                    'preco_vendido': item_estoque.preco_venda_atual
                }
            )
            
            # 2. Atualiza a quantidade
            item_venda.quantidade_vendida += quantidade
            item_venda.save()
            
            # 3. Recalcula o total da venda
            venda.calcular_valor_total()
            
            return item_venda