from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PerfilUsuario


class TestesCriacaoUsuario(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='admin_teste', password='123')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    @patch('usuario.services.AuthService.criar_usuario_auth')
    def test_criar_usuario_e_perfil_sucesso(self, mock_criar_auth):
        mock_criar_auth.return_value = {'id': 999, 'username': 'novo_user'}

        url = reverse('usuario:criar-usuario')
        data = {
            "nome": "Funcionário Teste",
            "email": "func@teste.com",
            "password": "senha_forte_123",
            "cargo": "GERENTE",
            "cpf": "11122233344"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_criar_auth.assert_called_once()

        perfil = PerfilUsuario.objects.get(cpf="11122233344")
        self.assertEqual(perfil.usuario_id_auth, 999)
