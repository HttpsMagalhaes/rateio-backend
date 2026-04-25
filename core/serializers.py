from rest_framework import serializers
from .models import Moradia, Usuario, DespesaGeral, DespesaDetalhe, DespesaRateio, Pagamento, Tarefa, TarefaResponsavel
from django.contrib.auth.hashers import make_password

class MoradiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moradia
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nome_completo', 'email', 'password', 'data_nascimento', 'chave_pix', 'qr_code_pix']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)

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