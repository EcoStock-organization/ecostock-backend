from django.db import models

from filial.models import Filial
from produto.models import Produto


class ItemEstoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="itens_estoque")

    quantidade_atual = models.FloatField(default=0.0)
    preco_venda_atual = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_minima_estoque = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("produto", "filial")

    def __str__(self):
        return f"{self.produto.nome} (Filial: {self.filial.nome})"
