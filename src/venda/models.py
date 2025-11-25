from decimal import Decimal

from django.db import models

from estoque.models import ItemEstoque
from filial.models import Filial
from produto.models import Produto


class FormaPagamento(models.TextChoices):
    CARTAO = "CARTAO", "Cartão"
    DINHEIRO = "DINHEIRO", "Dinheiro"
    PIX = "PIX", "Pix"


class Venda(models.Model):
    class StatusVenda(models.TextChoices):
        ABERTA = "ABERTA", "Aberta"
        FINALIZADA = "FINALIZADA", "Finalizada"
        CANCELADA = "CANCELADA", "Cancelada"

    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    usuario_id = models.IntegerField(
        help_text="ID do usuário (do serviço de Auth) que realizou a venda"
    )

    data_venda = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=StatusVenda.choices, default=StatusVenda.ABERTA
    )
    forma_pagamento = models.CharField(
        max_length=20, choices=FormaPagamento.choices, null=True, blank=True
    )
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Venda #{self.id} (Filial: {self.filial.nome})"

    def calcular_valor_total(self):
        total = sum(
            item.preco_vendido * Decimal(item.quantidade_vendida) for item in self.itens_venda.all()
        )
        self.valor_total = total
        self.save()
        return total

    def finalizar_venda(self, forma: FormaPagamento):
        if self.status != self.StatusVenda.ABERTA:
            raise Exception("Esta venda não pode ser finalizada.")

        self.forma_pagamento = forma
        self.status = self.StatusVenda.FINALIZADA
        self.calcular_valor_total()

        for item_vendido in self.itens_venda.all():
            try:
                item_em_estoque = ItemEstoque.objects.get(
                    filial=self.filial, produto=item_vendido.produto
                )

                if item_em_estoque.quantidade_atual < item_vendido.quantidade_vendida:
                    raise Exception(f"Estoque insuficiente para {item_vendido.produto.nome}")

                item_em_estoque.quantidade_atual -= item_vendido.quantidade_vendida
                item_em_estoque.save()

            except ItemEstoque.DoesNotExist:
                raise Exception(
                    f"Produto {item_vendido.produto.nome} não encontrado no estoque desta filial."
                )

        self.save()


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens_venda")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)

    quantidade_vendida = models.FloatField()

    preco_vendido = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade_vendida}x {self.produto.nome} na Venda #{self.venda.id}"
