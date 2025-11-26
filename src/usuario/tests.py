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

class TestesDelecaoUsuario(APITestCase):
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_tester', 
            password='123',
            is_staff=True 
        )
        
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.perfil_admin = PerfilUsuario.objects.create(
            usuario_id_auth=self.admin_user.id,
            nome_completo="Admin do Teste",
            cpf="00000000000",
            cargo=PerfilUsuario.Cargo.ADMIN
        )

        self.perfil_vitima = PerfilUsuario.objects.create(
            usuario_id_auth=500, 
            nome_completo="Funcionário Demitido",
            cpf="99988877700",
            cargo=PerfilUsuario.Cargo.OPERADOR
        )

    @patch('usuario.services.AuthService.deletar_usuario_auth')
    def test_deletar_usuario_fluxo_completo(self, mock_delete_service):
        mock_delete_service.return_value = True
        
        url = reverse('usuario:detalhe-usuario', kwargs={'pk': self.perfil_vitima.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_service.assert_called_once_with(500)
        self.assertFalse(PerfilUsuario.objects.filter(pk=self.perfil_vitima.pk).exists())

    def test_deletar_usuario_sem_permissao(self):
        user_comum = User.objects.create_user(username='comum', password='123')
        refresh_comum = RefreshToken.for_user(user_comum)
        
        PerfilUsuario.objects.create(
            usuario_id_auth=user_comum.id,
            nome_completo="Comum",
            cpf="11111111111",
            cargo=PerfilUsuario.Cargo.OPERADOR
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_comum.access_token}')

        url = reverse('usuario:detalhe-usuario', kwargs={'pk': self.perfil_vitima.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
