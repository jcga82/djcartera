from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views
from micartera.views import *

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'groups', views.GroupViewSet)
router.register(r'carteras', views.CarteraViewSet, basename='carteras')
router.register(r'empresas', views.EmpresaViewSet, basename='empresas')
router.register(r'dividendos', views.DividendoEmpresaViewSet, basename='dividendos')
router.register(r'fundamentales', views.FundamentalesEmpresaViewSet, basename='fundamentales')
router.register(r'historico', views.HistoricoEmpresaViewSet, basename='historico')
router.register(r'qhistorico', views.QHistoricoEmpresaViewSet, basename='qhistorico')
router.register(r'hist_casilla', views.HistoricoCasillasViewSet, basename='hist_casilla')
router.register(r'viviendas', views.ViviendaViewSet, basename='viviendas')
router.register(r'criptos', views.CriptoViewSet, basename='criptos')
router.register(r'fund_criptos', views.FundamentalesCriptoViewSet, basename='fund_criptos')
router.register(r'analisis_criptos', views.AnalisisCriptoViewSet, basename='analisis_criptos')
router.register(r'login', views.UserViewSet, basename='login')


urlpatterns = [
    path('', include(router.urls)),
    # path('dividendos/', DividendoEmpresaViewSet.as_view({'get': 'list', 'post': 'create'}))
    #path('', views.index, name='index'),

    # path('', include(('users.urls', 'users'), namespace='users')),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('charts', views.charts, name='charts'),
    # path('dashboard/', DashboardView.as_view(), name='dashboard'),
]