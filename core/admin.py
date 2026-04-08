from django.contrib import admin
from .models import Moradia, Usuario, DespesaGeral, DespesaDetalhe, DespesaRateio, Pagamento, Tarefa, TarefaResponsavel

admin.site.register(Moradia)
admin.site.register(Usuario)
admin.site.register(DespesaGeral)
admin.site.register(DespesaDetalhe)
admin.site.register(DespesaRateio)
admin.site.register(Pagamento)
admin.site.register(Tarefa)
admin.site.register(TarefaResponsavel)