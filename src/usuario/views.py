from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PerfilUsuario
from .serializers import UsuarioCompletoSerializer
from .services import AuthService


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
                cargo=dados.get('cargo', 'CAIXA'),
                filial_id=dados.get('filial') 
            )

            serializer = self.get_serializer(perfil)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": f"Erro ao criar usuário: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
