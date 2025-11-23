from django.contrib import admin
from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'usuario_id_auth', 'cargo', 'filial', 'ativo')
    list_filter = ('cargo', 'filial', 'ativo')
    search_fields = ('nome_completo', 'cpf', 'usuario_id_auth')
