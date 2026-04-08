import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from core.models import Moradia, Usuario, DespesaGeral, DespesaDetalhe, DespesaRateio

def popular_banco():
    print("Iniciando o plantio de dados (Seed)...")

    Moradia.objects.all().delete()
    DespesaGeral.objects.all().delete()

    moradia = Moradia.objects.create(
        nome="República Hackers do Bem",
        codigo_convite="HACK2026",
        rua="Avenida da Computação",
        numero="1010",
        bairro="Centro",
        cidade="Muzambinho"
    )
    print(f"Moradia '{moradia.nome}' criada!")

    user1 = Usuario.objects.create(
        nome_completo="Admin da República",
        email="admin@rateio.com",
        senha="senha_criptografada_fake",
        data_nascimento=date(2000, 5, 20),
        chave_pix="11122233344",
        qr_code_pix="link_qr_code_1",
        is_admin=True,
        id_moradia=moradia
    )
    user2 = Usuario.objects.create(
        nome_completo="Morador Dev",
        email="dev@rateio.com",
        senha="senha_criptografada_fake",
        data_nascimento=date(2001, 8, 15),
        chave_pix="55566677788",
        qr_code_pix="link_qr_code_2",
        is_admin=False,
        id_moradia=moradia
    )
    print("Usuários criados!")

    cat_luz = DespesaGeral.objects.create(descricao="Conta de Energia")
    cat_internet = DespesaGeral.objects.create(descricao="Internet Fibra")
    print("Categorias de despesas criadas!")

    despesa1 = DespesaDetalhe.objects.create(
        valor_total=200.00,
        data_vencimento=date(2026, 4, 10),
        status="pendente",
        id_usuario_credor=user1,
        id_despesa_geral=cat_luz,
        id_moradia=moradia
    )
    print(f"Despesa '{cat_luz.descricao}' lançada com sucesso!")

    DespesaRateio.objects.create(
        valor_proporcional=100.00,
        id_usuario_devedor=user1,
        id_despesa_detalhe=despesa1
    )
    DespesaRateio.objects.create(
        valor_proporcional=100.00,
        id_usuario_devedor=user2,
        id_despesa_detalhe=despesa1
    )
    print("Rateio dividido entre os moradores!")
    print("Banco de dados populado com sucesso! Tudo pronto para o Frontend.")

if __name__ == '__main__':
    popular_banco()