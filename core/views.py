from rest_framework import viewsets
from .models import Moradia, Usuario, DespesaGeral, DespesaDetalhe, DespesaRateio, Pagamento, Tarefa, TarefaResponsavel
from .serializers import (
    MoradiaSerializer, UsuarioSerializer, DespesaGeralSerializer, 
    DespesaDetalheSerializer, DespesaRateioSerializer, PagamentoSerializer, 
    TarefaSerializer, TarefaResponsavelSerializer
)

class MoradiaViewSet(viewsets.ModelViewSet):
    queryset = Moradia.objects.all()
    serializer_class = MoradiaSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class DespesaGeralViewSet(viewsets.ModelViewSet):
    queryset = DespesaGeral.objects.all()
    serializer_class = DespesaGeralSerializer

class DespesaDetalheViewSet(viewsets.ModelViewSet):
    queryset = DespesaDetalhe.objects.all()
    serializer_class = DespesaDetalheSerializer

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