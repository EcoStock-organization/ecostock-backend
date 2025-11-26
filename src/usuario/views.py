from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PerfilUsuario
from .serializers import UsuarioCompletoSerializer
from .services import AuthService


class IsLocalAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        try:
            perfil = PerfilUsuario.objects.get(usuario_id_auth=request.user.id)
            
            return perfil.cargo == PerfilUsuario.Cargo.ADMIN
            
        except PerfilUsuario.DoesNotExist:
            return False

class CriarUsuarioView(generics.CreateAPIView):
    queryset = PerfilUsuario.objects.all()
    serializer_class = UsuarioCompletoSerializer
    permission_classes = [IsAuthenticated] 

    def create(self, request, *args, **kwargs):
        dados = request.data
        try:
            auth_response = AuthService.criar_usuario_auth(
                username=dados.get('email'), 
                email=dados.get('email'),
                password=dados.get('password')
            )
            auth_user_id = auth_response['id']

            perfil = PerfilUsuario.objects.create(
                usuario_id_auth=auth_user_id,
                nome_completo=dados.get('nome'),
                cpf=dados.get('cpf'),
                cargo=dados.get('cargo', 'OPERADOR'),
                filial_id=dados.get('filial') 
            )

            serializer = self.get_serializer(perfil)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": f"Erro ao criar usuário: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class DetalheUsuarioView(generics.RetrieveDestroyAPIView):
    queryset = PerfilUsuario.objects.all()
    serializer_class = UsuarioCompletoSerializer
    
    permission_classes = [IsLocalAdmin]

    def perform_destroy(self, instance):
        AuthService.deletar_usuario_auth(instance.usuario_id_auth)
        
        instance.delete()
