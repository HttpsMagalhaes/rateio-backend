from rest_framework import serializers
from .models import Moradia, Usuario, DespesaGeral, DespesaDetalhe, DespesaRateio, Pagamento, Tarefa, TarefaResponsavel

class MoradiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moradia
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class DespesaGeralSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespesaGeral
        fields = '__all__'

class DespesaDetalheSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespesaDetalhe
        fields = '__all__'

class DespesaRateioSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespesaRateio
        fields = '__all__'

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'

class TarefaResponsavelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarefaResponsavel
        fields = '__all__'