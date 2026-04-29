from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from django.db.models import Sum
from .models import Moradia, Usuario, DespesaGeral, DespesaDetalhe, DespesaRateio, Pagamento, Tarefa, TarefaResponsavel
from .serializers import (
    MoradiaSerializer, UsuarioSerializer, DespesaGeralSerializer, 
    DespesaDetalheSerializer, DespesaRateioSerializer, PagamentoSerializer, 
    TarefaSerializer, TarefaResponsavelSerializer
)
from rest_framework.permissions import IsAuthenticated

class MoradiaViewSet(viewsets.ModelViewSet):
    queryset = Moradia.objects.all()
    serializer_class = MoradiaSerializer
    
    permission_classes = [IsAuthenticated] 

    @action(detail=False, methods=['post'], url_path='entrar')
    def entrar_com_convite(self, request):
        codigo = request.data.get('codigo_convite')
        
        if not codigo:
            return Response({"erro": "Código de convite não fornecido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            moradia = Moradia.objects.get(codigo_convite=codigo)
            usuario = request.user
            usuario.id_moradia = moradia
            usuario.save()

            serializer = self.get_serializer(moradia)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Moradia.DoesNotExist:
            return Response({"erro": "Moradia não encontrada com este código."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='resumo')
    def resumo_dashboard(self, request):
        usuario = request.user
        moradia = usuario.id_moradia

        if not moradia:
            return Response({"erro": "Usuário não pertence a nenhuma moradia."}, status=404)

        total_casa = DespesaDetalhe.objects.filter(id_moradia=moradia).aggregate(Sum('valor_total'))['valor_total__sum'] or 0

        meu_debito = DespesaRateio.objects.filter(
            id_usuario_devedor=usuario, 
            id_despesa_detalhe__status='pendente'
        ).aggregate(Sum('valor_proporcional'))['valor_proporcional__sum'] or 0

        minhas_tarefas = Tarefa.objects.filter(
            id_moradia=moradia, 
            status=False, 
            tarefaresponsavel__id_usuario=usuario
        ).count()

        return Response({
            "id_moradia": moradia.pk,
            "usuario_nome": usuario.nome_completo,
            "republica_nome": moradia.nome,
            "total_gastos_casa": float(total_casa),
            "meu_saldo_devedor": float(meu_debito),
            "tarefas_pendentes": minhas_tarefas,
            "codigo_convite": moradia.codigo_convite
        })

    @action(detail=True, methods=['get'])
    def moradores(self, request, pk=None):
        moradia = self.get_object()
        moradores = Usuario.objects.filter(id_moradia=moradia)
        dados = [{"id_usuario": m.id_usuario, "nome_completo": m.nome_completo} for m in moradores]
        return Response(dados)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Usuario.objects.filter(id_usuario=self.request.user.id_usuario)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        usuario = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        
        nova_senha = request.data.get('nova_senha')
        senha_antiga = request.data.get('senha_antiga')

        if nova_senha:
            if not senha_antiga:
                return Response({"erro": "Você precisa informar a senha antiga para criar uma nova."}, status=400)
            
            if not usuario.check_password(senha_antiga):
                return Response({"erro": "A senha antiga está incorreta."}, status=400)
            
            # Se passou pelos testes, troca a senha
            usuario.set_password(nova_senha)
            request.data.pop('nova_senha', None)
            request.data.pop('senha_antiga', None)
            
        serializer = self.get_serializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class DespesaGeralViewSet(viewsets.ModelViewSet):
    queryset = DespesaGeral.objects.all()
    serializer_class = DespesaGeralSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        if usuario.id_moradia:
            return self.queryset.filter(id_moradia=usuario.id_moradia)
        return self.queryset.none()

    def perform_create(self, serializer):
        # Quando for salvar, injeta automaticamente a moradia do usuário logado
        serializer.save(id_moradia=self.request.user.id_moradia)

class DespesaDetalheViewSet(viewsets.ModelViewSet):
    serializer_class = DespesaDetalheSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DespesaDetalhe.objects.filter(id_moradia=self.request.user.id_moradia).order_by('-data_vencimento')

    def perform_create(self, serializer):

        despesa = serializer.save(
            id_usuario_credor=self.request.user,
            id_moradia=self.request.user.id_moradia
        )

        moradores_ids = self.request.data.get('moradores_ids', [])
        
        if moradores_ids:
            valor_total = Decimal(str(despesa.valor_total))
            valor_fatia = valor_total / len(moradores_ids)

            for m_id in moradores_ids:
                DespesaRateio.objects.create(
                    id_despesa_detalhe=despesa,
                    id_usuario_devedor_id=m_id, 
                    valor_proporcional=valor_fatia
                )

    @action(detail=False, methods=['get'])
    def balanco(self, request):
        usuario = request.user

        receber = DespesaRateio.objects.filter(
            id_despesa_detalhe__id_usuario_credor=usuario,
            id_despesa_detalhe__status='pendente'
        ).exclude(id_usuario_devedor=usuario).aggregate(total=Sum('valor_proporcional'))['total'] or 0.00

        pagar = DespesaRateio.objects.filter(
            id_usuario_devedor=usuario,
            id_despesa_detalhe__status='pendente'
        ).exclude(id_despesa_detalhe__id_usuario_credor=usuario).aggregate(total=Sum('valor_proporcional'))['total'] or 0.00

        return Response({
            "total_receber": receber,
            "total_pagar": pagar,
            "saldo_liquido": receber - pagar
        })

class DespesaRateioViewSet(viewsets.ModelViewSet):
    queryset = DespesaRateio.objects.all()
    serializer_class = DespesaRateioSerializer

class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer

class TarefaViewSet(viewsets.ModelViewSet):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer

class TarefaResponsavelViewSet(viewsets.ModelViewSet):
    queryset = TarefaResponsavel.objects.all()
    serializer_class = TarefaResponsavelSerializer