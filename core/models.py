from django.db import models

class Moradia(models.Model):
    id_moradia = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    codigo_convite = models.CharField(max_length=50, unique=True) 
    data_criacao = models.DateTimeField(auto_now_add=True)
    rua = models.CharField(max_length=150)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome_completo = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True) 
    senha = models.CharField(max_length=255)               
    data_nascimento = models.DateField()
    chave_pix = models.CharField(max_length=100)
    qr_code_pix = models.CharField(max_length=255, blank=True, null=True)
    is_admin = models.BooleanField(default=False)          
    ativo = models.BooleanField(default=True)              
    id_moradia = models.ForeignKey(Moradia, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome_completo

class DespesaGeral(models.Model):
    id_despesa_geral = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=45)

    def __str__(self):
        return self.descricao

class DespesaDetalhe(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
    ]
    id_despesa_detalhe = models.AutoField(primary_key=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    id_usuario_credor = models.ForeignKey(Usuario, on_delete=models.RESTRICT)
    id_despesa_geral = models.ForeignKey(DespesaGeral, on_delete=models.RESTRICT)
    id_moradia = models.ForeignKey(Moradia, on_delete=models.CASCADE)

    def __str__(self):
        return f"Detalhe: R$ {self.valor_total} - Venc: {self.data_vencimento}"

class DespesaRateio(models.Model):
    id_rateio = models.AutoField(primary_key=True)
    valor_proporcional = models.DecimalField(max_digits=10, decimal_places=2)
    id_usuario_devedor = models.ForeignKey(Usuario, on_delete=models.RESTRICT)
    id_despesa_detalhe = models.ForeignKey(DespesaDetalhe, on_delete=models.CASCADE)

    def __str__(self):
        return f"Rateio de {self.id_usuario_devedor} - R$ {self.valor_proporcional}"

class Pagamento(models.Model):
    id_pagamento = models.AutoField(primary_key=True)
    data_pagamento = models.DateTimeField(auto_now_add=True)
    comprovante = models.CharField(max_length=255)
    status_aprovacao = models.BooleanField(default=False)
    id_rateio = models.ForeignKey(DespesaRateio, on_delete=models.CASCADE)

class Tarefa(models.Model):
    id_tarefa = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=200)
    data_limite = models.DateField()
    status = models.BooleanField(default=False)
    id_moradia = models.ForeignKey(Moradia, on_delete=models.CASCADE)

    def __str__(self):
        return self.descricao

class TarefaResponsavel(models.Model):
    id_tarefa_responsavel = models.AutoField(primary_key=True)
    id_tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)