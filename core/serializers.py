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
    # Esses dois campos 'source' puxam o nome ao invés de só o ID
    categoria_descricao = serializers.CharField(source='id_despesa_geral.descricao', read_only=True)
    credor_nome = serializers.CharField(source='id_usuario_credor.nome_completo', read_only=True)
    moradores_ids = serializers.SerializerMethodField()

    class Meta:
        model = DespesaDetalhe
        fields = [
            'id_despesa_detalhe', 'valor_total', 'data_vencimento', 'status',
            'id_usuario_credor', 'credor_nome', 
            'id_despesa_geral', 'categoria_descricao', 
            'id_moradia', 'moradores_ids'
        ]

        read_only_fields = ['id_usuario_credor', 'id_moradia']

    def get_moradores_ids(self, obj):
        from .models import DespesaRateio
        return list(DespesaRateio.objects.filter(id_despesa_detalhe=obj).values_list('id_usuario_devedor', flat=True))

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