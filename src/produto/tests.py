from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Produto, Categoria


class TestesAPIProduto(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword123")

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.categoria = Categoria.objects.create(
            nome="Bebidas",
            descricao="Sucos e Refrigerantes"
        )

        self.produto = Produto.objects.create(
            codigo_barras="1111111111111",
            nome="Produto de Teste",
            descricao="Descricao teste",
            tipo_produto="UNITARIO",
            categoria=self.categoria,
            esta_ativo=True
        )

    def test_listar_produtos_autenticado_sucesso(self):
        url = reverse("produto:produto-lista-criar")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nome"], "Produto de Teste")
        self.assertEqual(response.data[0]["categoria_nome"], "Bebidas")

    def test_listar_produtos_nao_autenticado_falha(self):
        self.client.credentials()
        url = reverse("produto:produto-lista-criar")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_criar_produto_sucesso(self):
        url = reverse("produto:produto-lista-criar")
        data = {
            "codigo_barras": "2222222222222",
            "nome": "Produto Novo Criado no Teste",
            "descricao": "Descricao",
            "tipo_produto": "PESAVEL",
            "id_categoria": self.categoria.id
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Produto.objects.count(), 2)
        self.assertEqual(response.data["nome"], "Produto Novo Criado no Teste")
        self.assertEqual(response.data["id_categoria"], self.categoria.id)

    def test_criar_produto_codigo_barras_duplicado_falha(self):
        url = reverse("produto:produto-lista-criar")
        data = {
            "codigo_barras": "1111111111111",
            "nome": "Produto Duplicado",
            "tipo_produto": "UNITARIO",
            "id_categoria": self.categoria.id
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("codigo_barras", response.data)

    def test_deletar_produto_soft_delete_sucesso(self):
        url = reverse("produto:produto-detalhe", kwargs={"pk": self.produto.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.produto.refresh_from_db()
        self.assertEqual(Produto.objects.count(), 1)

        self.assertEqual(self.produto.esta_ativo, False)

        response_lista = self.client.get(reverse("produto:produto-lista-criar"))
        self.assertEqual(response_lista.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_lista.data), 0)

    def test_criar_produto_dados_invalidos_parametrizado(self):
        url = reverse("produto:produto-lista-criar")
        
        casos_de_teste = [
            (
                {"codigo_barras": "9001", "nome": "", "tipo_produto": "UNITARIO"}, 
                "nome"
            ),
            (
                {"codigo_barras": "12345678901234567", "nome": "Prod Longo", "tipo_produto": "UNITARIO"}, 
                "codigo_barras"
            ),
            (
                {"codigo_barras": "9002", "nome": "Prod Tipo Ruim", "tipo_produto": "LIQUIDO_ESTRANHO"}, 
                "tipo_produto"
            ),
            (
                {"nome": "Sem Codigo", "tipo_produto": "UNITARIO"}, 
                "codigo_barras"
            ),
        ]

        for dados_invalidos, campo_erro in casos_de_teste:
            with self.subTest(dados=dados_invalidos):
                response = self.client.post(url, dados_invalidos, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(campo_erro, response.data)
