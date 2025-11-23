from django.db import models
from filial.models import Filial


class PerfilUsuario(models.Model):
    class Cargo(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        GERENTE = 'GERENTE', 'Gerente'
        OPERADOR = 'OPERADOR', 'Operador de Caixa'

    usuario_id_auth = models.IntegerField(unique=True, help_text="ID do usuário no serviço de Autenticação")
    
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    cargo = models.CharField(max_length=20, choices=Cargo.choices, default=Cargo.GERENTE)
    
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True)
    
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome_completo} ({self.cargo})"
