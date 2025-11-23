from rest_framework import serializers
from .models import PerfilUsuario
from .services import AuthService


class UsuarioCompletoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = PerfilUsuario
        fields = ['id', 'nome_completo', 'cpf', 'cargo', 'filial', 'ativo', 'username', 'password', 'email', 'usuario_id_auth']
        read_only_fields = ['usuario_id_auth']

    def create(self, validated_data):
        auth_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email')
        }

        user_auth = AuthService.criar_usuario_auth(**auth_data)
        
        validated_data['usuario_id_auth'] = user_auth['id']
        perfil = PerfilUsuario.objects.create(**validated_data)
        
        return perfil
