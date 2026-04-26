from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MoradiaViewSet, UsuarioViewSet, DespesaGeralViewSet, 
    DespesaDetalheViewSet, DespesaRateioViewSet, PagamentoViewSet, 
    TarefaViewSet, TarefaResponsavelViewSet
)

router = DefaultRouter()

router.register(r'moradias', MoradiaViewSet, basename='moradia')
router.register(r'usuarios', UsuarioViewSet)
router.register(r'categorias', DespesaGeralViewSet, basename='categoria')
router.register(r'despesas-detalhes', DespesaDetalheViewSet)
router.register(r'rateios', DespesaRateioViewSet)
router.register(r'pagamentos', PagamentoViewSet)
router.register(r'tarefas', TarefaViewSet)
router.register(r'tarefas-responsaveis', TarefaResponsavelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
]