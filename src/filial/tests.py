from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Filial
from estoque.models import ItemEstoque
from produto.models import Produto


class TestesAPIFilial(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="userteste_filial", password="testpassword123"
        )

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.filial = Filial.objects.create(
            nome="Filial Teste Setup",
            cep="70000-000",
            logradouro="Rua Teste",
            cidade="Brasilia",
            estado="DF",
            gerente_id=1,
        )

    def test_listar_filiais_autenticado_sucesso(self):
        url = reverse("filial:filial-lista-criar")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nome"], "Filial Teste Setup")

    def test_listar_filiais_nao_autenticado_falha(self):
        self.client.credentials()  # Limpa a autenticação
        url = reverse("filial:filial-lista-criar")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_criar_filial_sucesso(self):
        url = reverse("filial:filial-lista-criar")
        data = {
            "nome": "Filial Nova (Criada no Teste)",
            "cep": "71000-000",
            "logradouro": "Rua Nova",
            "cidade": "Taguatinga",
            "estado": "DF",
            "gerente_id": 2,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Filial.objects.count(), 2)
        self.assertEqual(response.data["nome"], "Filial Nova (Criada no Teste)")

    def test_criar_filial_nome_faltando_falha(self):
        url = reverse("filial:filial-lista-criar")
        data = {
            # "nome": "Faltando"
            "cep": "71000-000",
            "cidade": "Taguatinga",
            "estado": "DF",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nome", response.data)

    def test_atualizar_filial_patch_sucesso(self):
        url = reverse("filial:filial-detalhe", kwargs={"pk": self.filial.pk})
        data = {"nome": "Filial Teste ATUALIZADA"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.filial.refresh_from_db()
        self.assertEqual(self.filial.nome, "Filial Teste ATUALIZADA")

    def test_deletar_filial_hard_delete_com_cascade(self):
        prod = Produto.objects.create(
            codigo_barras="999", nome="Prod Cascade", tipo_produto="UNITARIO"
        )
        ItemEstoque.objects.create(
            filial=self.filial, produto=prod, 
            quantidade_atual=10, preco_venda_atual=10, quantidade_minima_estoque=5
        )

        url = reverse('filial:filial-detalhe', kwargs={'pk': self.filial.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertFalse(Filial.objects.filter(pk=self.filial.pk).exists())

        self.assertFalse(ItemEstoque.objects.filter(filial=self.filial).exists())
