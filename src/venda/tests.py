from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from estoque.models import ItemEstoque
from filial.models import Filial
from produto.models import Produto
from usuario.models import PerfilUsuario
from .models import FormaPagamento, ItemVenda, Venda

class TestesAPIVenda(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="userteste_venda", password="testpassword123")
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.filial = Filial.objects.create(
            nome="Filial Venda Teste", cep="70000-000", cidade="Brasilia", estado="DF"
        )

        self.perfil = PerfilUsuario.objects.create(
            usuario_id_auth=self.user.id,
            nome_completo="Testador Vendas",
            cpf="12345678900",
            cargo=PerfilUsuario.Cargo.OPERADOR,
            filial=self.filial,
            ativo=True
        )

        self.produto = Produto.objects.create(
            codigo_barras="8888888888888",
            nome="Produto para Venda",
            tipo_produto="UNITARIO",
        )

        self.item_estoque = ItemEstoque.objects.create(
            filial=self.filial,
            produto=self.produto,
            quantidade_atual=100.0,
            preco_venda_atual=10.00,
            quantidade_minima_estoque=10,
        )

    def test_fluxo_completo_de_venda_e_baixa_de_estoque(self):
        url_criar_venda = reverse("venda:venda-list")
        data_criar_venda = {"filial": self.filial.pk}

        response_criar = self.client.post(url_criar_venda, data_criar_venda, format="json")

        self.assertEqual(response_criar.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Venda.objects.count(), 1)

        venda_id = response_criar.data["id"]

        url_add_item = reverse("venda:venda-adicionar-item", kwargs={"pk": venda_id})
        data_add_item = {"produto_id": self.produto.pk, "quantidade": 10.0}
        
        response_add_item = self.client.post(url_add_item, data_add_item, format="json")

        self.assertEqual(response_add_item.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ItemVenda.objects.count(), 1)

        url_finalizar = reverse("venda:venda-finalizar-venda", kwargs={"pk": venda_id})
        data_finalizar = {"forma_pagamento": FormaPagamento.PIX.value}
        
        response_finalizar = self.client.post(url_finalizar, data_finalizar, format="json")

        self.assertEqual(response_finalizar.status_code, status.HTTP_200_OK)
        self.assertEqual(response_finalizar.data["status"], Venda.StatusVenda.FINALIZADA)
        self.assertEqual(float(response_finalizar.data["valor_total"]), 100.00)

        self.item_estoque.refresh_from_db()
        self.assertEqual(self.item_estoque.quantidade_atual, 90.0)

    def test_adicionar_item_com_estoque_insuficiente_falha(self):
        url_criar_venda = reverse("venda:venda-list")
        data_criar_venda = {"filial": self.filial.pk}

        response_criar = self.client.post(url_criar_venda, data_criar_venda, format="json")
        venda_id = response_criar.data["id"]

        url_add_item = reverse("venda:venda-adicionar-item", kwargs={"pk": venda_id})
        data_add_item = {"produto_id": self.produto.pk, "quantidade": 101.0}

        response_add_item = self.client.post(url_add_item, data_add_item, format="json")

        self.assertEqual(response_add_item.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Estoque insuficiente", str(response_add_item.data))
