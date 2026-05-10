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

        # 1. Busca o Gasto Total da Casa
        total_casa = DespesaDetalhe.objects.filter(id_moradia=moradia).aggregate(Sum('valor_total'))['valor_total__sum'] or 0

        # 2. Busca tudo o que eu tenho a RECEBER
        receber_qs = DespesaRateio.objects.filter(
            id_despesa_detalhe__id_usuario_credor=usuario, id_despesa_detalhe__status='pendente'
        ).exclude(id_usuario_devedor=usuario).values(
            'id_usuario_devedor__nome_completo'
        ).annotate(total=Sum('valor_proporcional'))

        # 3. Busca tudo o que eu tenho a PAGAR
        pagar_qs = DespesaRateio.objects.filter(
            id_usuario_devedor=usuario, id_despesa_detalhe__status='pendente'
        ).exclude(id_despesa_detalhe__id_usuario_credor=usuario).values(
            'id_despesa_detalhe__id_usuario_credor__nome_completo'
        ).annotate(total=Sum('valor_proporcional'))

        # 4. A MÁGICA DA COMPENSAÇÃO (O Cruzamento de Dados)
        saldos = {}
        
        for item in receber_qs:
            nome = item['id_usuario_devedor__nome_completo']
            saldos[nome] = saldos.get(nome, 0) + float(item['total'])
            
        for item in pagar_qs:
            nome = item['id_despesa_detalhe__id_usuario_credor__nome_completo']
            saldos[nome] = saldos.get(nome, 0) - float(item['total'])

        total_receber_liquido = 0
        total_pagar_liquido = 0

        # Separa os valores líquidos
        for valor in saldos.values():
            if valor > 0:
                total_receber_liquido += valor
            elif valor < 0:
                total_pagar_liquido += abs(valor)

        # 5. Busca as Tarefas Pendentes
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
            "meu_saldo_devedor": total_pagar_liquido, # Agora envia o valor compensado
            "meu_saldo_receber": total_receber_liquido, # Agora envia o valor compensado
            "tarefas_pendentes": minhas_tarefas,
            "codigo_convite": moradia.codigo_convite
        })

    @action(detail=False, methods=['get'], url_path='graficos')
    def graficos_dashboard(self, request):
        usuario = request.user
        moradia = usuario.id_moradia

        if not moradia:
            return Response({"erro": "Sem moradia."}, status=404)

        from django.db.models import Sum, Count
        import datetime
        
        # Pega o mês e o ano atuais para o histórico padrão da tela inicial
        hoje = datetime.datetime.now()
        mes_atual = hoje.month
        ano_atual = hoje.year

        # 1. Dados para o Gráfico de Pizza (Quem pagou as contas concluídas do mês)
        gastos = DespesaDetalhe.objects.filter(
            id_moradia=moradia,
            data_vencimento__month=mes_atual,
            data_vencimento__year=ano_atual
        ).values('id_usuario_credor__nome_completo').annotate(total=Sum('valor_total'))

        grafico_despesas = [
            {"nome": item['id_usuario_credor__nome_completo'], "valor": float(item['total'])}
            for item in gastos
        ]

        # 2. Dados para o Gráfico de Barras (Quem concluiu mais tarefas no mês)
        tarefas_feitas = TarefaResponsavel.objects.filter(
            id_tarefa__id_moradia=moradia,
            id_tarefa__status=True,
            id_tarefa__data_limite__month=mes_atual,
            id_tarefa__data_limite__year=ano_atual
        ).values('id_usuario__nome_completo').annotate(total=Count('id_tarefa'))

        grafico_tarefas = [
            {"nome": item['id_usuario__nome_completo'], "total": item['total']}
            for item in tarefas_feitas
        ]

        return Response({
            "mes_atual": mes_atual,
            "ano_atual": ano_atual,
            "grafico_despesas": grafico_despesas,
            "grafico_tarefas": grafico_tarefas
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
            
        def perform_update(self, serializer):
            despesa = serializer.save()
            
            moradores_ids = self.request.data.get('moradores_ids')
            
            if moradores_ids is not None:
                DespesaRateio.objects.filter(id_despesa_detalhe=despesa).delete()
                
                if len(moradores_ids) > 0:
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

        receber_bruto = DespesaRateio.objects.filter(
            id_despesa_detalhe__id_usuario_credor=usuario,
            id_despesa_detalhe__status='pendente'
        ).exclude(id_usuario_devedor=usuario).aggregate(total=Sum('valor_proporcional'))['total'] or 0.00

        pagar_bruto = DespesaRateio.objects.filter(
            id_usuario_devedor=usuario,
            id_despesa_detalhe__status='pendente'
        ).exclude(id_despesa_detalhe__id_usuario_credor=usuario).aggregate(total=Sum('valor_proporcional'))['total'] or 0.00

        # Transformamos com float() para garantir que a matemática não quebre
        receber = float(receber_bruto)
        pagar = float(pagar_bruto)

        return Response({
            "total_receber": receber,
            "total_pagar": pagar,
            "saldo_liquido": receber - pagar
        })
        
    @action(detail=False, methods=['get'])
    def balanco(self, request):
        usuario = request.user
        moradia = usuario.id_moradia

        # 1. Busca o Gasto Total da Casa para o card fixo
        total_casa = DespesaDetalhe.objects.filter(id_moradia=moradia).aggregate(Sum('valor_total'))['valor_total__sum'] or 0

        # 2. Busca tudo o que eu tenho a RECEBER
        receber_qs = DespesaRateio.objects.filter(
            id_despesa_detalhe__id_usuario_credor=usuario, id_despesa_detalhe__status='pendente'
        ).exclude(id_usuario_devedor=usuario).values(
            'id_usuario_devedor__nome_completo'
        ).annotate(total=Sum('valor_proporcional'))

        # 3. Busca tudo o que eu tenho a PAGAR
        pagar_qs = DespesaRateio.objects.filter(
            id_usuario_devedor=usuario, id_despesa_detalhe__status='pendente'
        ).exclude(id_despesa_detalhe__id_usuario_credor=usuario).values(
            'id_despesa_detalhe__id_usuario_credor__nome_completo'
        ).annotate(total=Sum('valor_proporcional'))

        saldos = {}
        
        # Soma o que me devem (+)
        for item in receber_qs:
            nome = item['id_usuario_devedor__nome_completo']
            saldos[nome] = saldos.get(nome, 0) + float(item['total'])
            
        # Subtrai o que eu devo (-)
        for item in pagar_qs:
            nome = item['id_despesa_detalhe__id_usuario_credor__nome_completo']
            saldos[nome] = saldos.get(nome, 0) - float(item['total'])

        # 5. Separa os resultados finais já mastigados para o celular
        lista_receber = []
        lista_pagar = []
        total_receber_liquido = 0
        total_pagar_liquido = 0

        for nome, valor in saldos.items():
            if valor > 0: # Se sobrou positivo, a pessoa me deve
                lista_receber.append({"nome": nome, "valor": valor})
                total_receber_liquido += valor
            elif valor < 0: # Se ficou negativo, eu devo à pessoa
                lista_pagar.append({"nome": nome, "valor": abs(valor)})
                total_pagar_liquido += abs(valor)

        return Response({
            "total_gastos_casa": float(total_casa), # Enviando o total geral
            "total_receber": total_receber_liquido,
            "total_pagar": total_pagar_liquido,
            "saldo_liquido": total_receber_liquido - total_pagar_liquido,
            "detalhes_receber": lista_receber,
            "detalhes_pagar": lista_pagar
        })

    @action(detail=False, methods=['get'])
    def historico(self, request):
        # Traz apenas as despesas com status 'concluida'
        despesas = DespesaDetalhe.objects.filter(
            id_moradia=request.user.id_moradia,
            status='concluida'
        ).order_by('-data_vencimento')
        serializer = self.get_serializer(despesas, many=True)
        return Response(serializer.data)

class DespesaRateioViewSet(viewsets.ModelViewSet):
    queryset = DespesaRateio.objects.all()
    serializer_class = DespesaRateioSerializer

class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer

class TarefaViewSet(viewsets.ModelViewSet):
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        if usuario.id_moradia:
            # Filtra as tarefas da moradia ONDE o utilizador logado é um dos responsáveis
            return Tarefa.objects.filter(
                id_moradia=usuario.id_moradia,
                tarefaresponsavel__id_usuario=usuario
            ).order_by('data_limite').distinct() # distinct() evita que a tarefa apareça duplicada
        return Tarefa.objects.none()

    def perform_create(self, serializer):
        tarefa = serializer.save(id_moradia=self.request.user.id_moradia)
        # Agora recebemos uma lista de IDs
        responsaveis_ids = self.request.data.get('responsaveis_ids', [])
        for r_id in responsaveis_ids:
            TarefaResponsavel.objects.create(id_tarefa=tarefa, id_usuario_id=r_id)

    def perform_update(self, serializer):
        tarefa = serializer.save()
        responsaveis_ids = self.request.data.get('responsaveis_ids')
        if responsaveis_ids is not None:
            TarefaResponsavel.objects.filter(id_tarefa=tarefa).delete()
            for r_id in responsaveis_ids:
                TarefaResponsavel.objects.create(id_tarefa=tarefa, id_usuario_id=r_id)


    # Rota especial para o botão de "Check" do aplicativo
    @action(detail=True, methods=['patch'])
    def concluir(self, request, pk=None):
        tarefa = self.get_object()
        tarefa.status = not tarefa.status # Inverte (se tava False vira True e vice-versa)
        tarefa.save()
        return Response({'status': tarefa.status, 'mensagem': 'Status alterado!'})

    @action(detail=False, methods=['get'])
    def historico(self, request):
        # Traz apenas as tarefas que já foram marcadas como status=True
        tarefas = Tarefa.objects.filter(
            id_moradia=request.user.id_moradia,
            status=True
        ).order_by('-data_limite')
        serializer = self.get_serializer(tarefas, many=True)
        return Response(serializer.data)

class TarefaResponsavelViewSet(viewsets.ModelViewSet):
    queryset = TarefaResponsavel.objects.all()
    serializer_class = TarefaResponsavelSerializer