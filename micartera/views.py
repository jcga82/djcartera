from django.shortcuts import render

from micartera.filtros import DividendosFilter
from .models import Movimiento, Cartera, Empresa
from django.db.models import Avg, Sum, F, Q, FloatField, Case, CharField, Value, When
from django.contrib.auth.models import User, Group
from django.views.generic import TemplateView
from datetime import datetime
import pandas as pd
# from django_pandas.io import read_frame
from rest_framework import generics, status, mixins, viewsets
from rest_framework import permissions
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import *


# Permissions
from rest_framework.permissions import IsAuthenticated
# from users.permissions import IsStandardUser

#CARTERAS
class CarteraViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = CarteraModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Cartera.objects.all()#filter(user=self.request.user)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = CarteraSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        emp = serializer.save()
        data = CarteraModelSerializer(emp).data
        return Response(data, status=status.HTTP_201_CREATED)


#DIVIDENDOS
class DividendoEmpresaViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = DividendoEmpresaModelSerializer
    paginator = None
    # filter_class = DividendosFilter
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['id', 'name']
    # search_fields = ['=name', 'intro']
    # ordering_fields = ['name', 'id']
    # ordering = ['id']

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        symbol = self.request.query_params.get('symbol', None)
        empresa = Empresa.objects.filter(symbol=symbol)
        queryset = DividendoEmpresa.objects.filter(empresa=empresa[0].id)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = DividendoEmpresaSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        div = serializer.save()
        data = EmpresaModelSerializer(div).data
        return Response(data, status=status.HTTP_201_CREATED)

#EMPRESAS
class EmpresaViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = EmpresaModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Restrict list to only user experience."""
        queryset = Empresa.objects.all()#filter(user=self.request.user)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = EmpresaSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        emp = serializer.save()
        data = EmpresaModelSerializer(emp).data
        return Response(data, status=status.HTTP_201_CREATED)


#FUNDAMENTALES EMPRESAS
class FundamentalesEmpresaViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = FundamentalesEmpresaModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        symbol = self.request.query_params.get('symbol', None)
        empresa = Empresa.objects.filter(symbol=symbol)
        queryset = FundamentalesEmpresa.objects.filter(empresa=empresa[0].id)
        print(empresa[0].id)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = FundamentalesEmpresaSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        div = serializer.save()
        data = FundamentalesEmpresaModelSerializer(div).data
        return Response(data, status=status.HTTP_201_CREATED)

#HISTORICO EMPRESAS
class HistoricoEmpresaViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = HistoricoEmpresaModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        queryset = HistoricoEmpresa.objects.filter(empresa=id)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = HistoricoEmpresaSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        emp = serializer.save()
        data = HistoricoEmpresaModelSerializer(emp).data
        return Response(data, status=status.HTTP_201_CREATED)

#QHISTORICO EMPRESAS
class QHistoricoEmpresaViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = QHistoricoEmpresaModelSerializer
    paginator = None

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        queryset = QHistoricoEmpresa.objects.all()
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = QHistoricoEmpresaSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        emp = serializer.save()
        data = QHistoricoEmpresaModelSerializer(emp).data
        return Response(data, status=status.HTTP_201_CREATED)

#HISTORICO CASILLAS
class HistoricoCasillasViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = HistoricoCasillasModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        address = self.request.query_params.get('address', None)
        queryset = HistoricoCasillas.objects.filter(address=address)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = HistoricoCasillasModelSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        hist = serializer.save()
        data = HistoricoCasillasModelSerializer(hist).data
        return Response(data, status=status.HTTP_201_CREATED)

#VIVIENDAS
class ViviendaViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = ViviendaModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        queryset = Vivienda.objects.all()#filter(user=self.request.user)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = ViviendaSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        emp = serializer.save()
        data = ViviendaModelSerializer(emp).data
        return Response(data, status=status.HTTP_201_CREATED)
    
    # def put(self, request, *args, **kwargs):
    #     return self.update(request, *args, **kwargs)
    
    def put(self, request, pk):
        viv = Vivienda.objects.filter(pk=pk).first()
        print(viv)
        if viv:
            serializer = ViviendaSerializer(viv)
            viv.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        viv = Vivienda.objects.filter(pk=pk).first()
        if viv:
            serializer = ViviendaSerializer(viv)
            viv.delete()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


#CRIPTOS
class CriptoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = CriptoModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Cripto.objects.all()
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = CriptoSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        emp = serializer.save()
        data = CriptoModelSerializer(emp).data
        return Response(data, status=status.HTTP_201_CREATED)
    
    def put(self, request, pk):
        viv = Cripto.objects.filter(pk=pk).first()
        print(viv)
        if viv:
            serializer = CriptoSerializer(viv)
            viv.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        viv = Cripto.objects.filter(pk=pk).first()
        if viv:
            serializer = CriptoSerializer(viv)
            viv.delete()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


#CRIPTO FUNDAMENTALES
class FundamentalesCriptoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = FundamentalesCriptoModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        queryset = FundamentalesCripto.objects.filter(cripto=id)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = FundamentalesCriptoSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        emp = serializer.save()
        data = FundamentalesCriptoModelSerializer(emp).data
        return Response(data, status=status.HTTP_201_CREATED)

#CRIPTO ANALISIS
class AnalisisCriptoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = AnalisisCriptoModelSerializer

    # def get_permissions(self):
    #     permission_classes = [IsAuthenticated, ]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        queryset = AnalisisCripto.objects.filter(cripto=id)
        return queryset
        
    def create(self, request, *args, **kwargs):
        serializer = AnalisisCriptoSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        emp = serializer.save()
        data = AnalisisCriptoModelSerializer(emp).data
        return Response(data, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User sign in."""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserSerializer(user).data,
            'access_token': token
        }
        return Response(data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def signup(self, request):
        """User sign up."""
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

from . import portfolio_utils as pu
from . import portfolio_analysis as pa
# from pyrtfolio.StockPortfolio import StockPortfolio
import investpy
#VOY A SACAR LAS ESPAÑOLAS Y LOS ETF JE00B1VS3770 italy ETFS Physical Gold

class DashboardView(TemplateView):
    template_name = 'micartera/dashboard.html'

    latest_movimientos_list = Movimiento.objects.order_by('-fecha')[:5]
    #print(latest_movimientos_list)

    def get_graph_sales_year_month(self):
        data = []
        try:
            year = datetime.now().year
            for m in range(1, 13):
                total = Movimiento.objects.filter(date_joined__year=year, date_joined__month=m).aggregate(r=Coalesce(Sum('total'), 0)).get('r')
                data.append(float(total))
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['panel'] = 'Panel de administrador'
        context['graph_sales_year_month'] = self.get_graph_sales_year_month()
        return context


def index(request):

    # portfolio = StockPortfolio()
    # portfolio.add_stock(stock_symbol='BBVA',
    #                 stock_country='spain',
    #                 purchase_date='04/01/2018',
    #                 num_of_shares=2,
    #                 cost_per_share=7.2)
    # print(portfolio.__dict__)                
    movimientos_list = Movimiento.objects.values(
            'empresa__symbol'
        ).annotate(
            total_acciones=Sum('acciones'),
        )


    cartera_actual_list = Movimiento.objects.values(
            'empresa__symbol'
        ).annotate(
            total_acciones=Sum('acciones'),
            #rentabilidad=Sum('coste_total'),
            coste_operacion=Sum(F('precio') * F('acciones') * F('cambio_moneda'), output_field=FloatField()),
            precio_promedio=Avg(F('precio') * F('acciones') / F('acciones'), output_field=FloatField())
        )#.filter(total_acciones>0)
        # sales_price=Case(
        #     When(discount__isnull=True, then=F('price')),
        #     When(discount__isnull=False, then=(F('price') - (F('discount') * F('price')) / 100)),
        #     output_field=IntegerField(),
        # )

    # THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    # my_file = os.path.join(THIS_FOLDER, 'test_stock_transactions.csv')

    empresas_eeuu = Empresa.objects.all()#filter(pais='united states') # , tipo='a'
    empresas_es = Empresa.objects.filter(pais='spain')
    portfolio_df = []#read_frame(Movimiento.objects.filter(empresa__in=empresas_eeuu)) #pd.read_csv(my_file) filter(tipo='a')
    print('aqui;', portfolio_df)
    symbols = portfolio_df.empresa.unique()#empresas_validas.unique()
    print(symbols)

    portfolio_df['fecha'] = pd.to_datetime(portfolio_df['fecha'].dt.normalize())
    portfolio_df.sort_values("fecha", inplace=True, ascending=True)
    print('portfolio_df:', portfolio_df)

    
    # empresas = Empresa.objects.filter(nombre__in=empresas_cartera)
    # symbols = empresas.values_list('symbol', flat=True)
    
    stocks_start = datetime(2020, 1, 26)
    stocks_end = datetime(2020, 2, 7)

    dfETF = investpy.get_etf_historical_data(etf='ETFS Physical Gold', country='italy', from_date=stocks_start.strftime('%d/%m/%Y'), to_date=stocks_end.strftime('%d/%m/%Y'))
    dfETF.drop(['Open', 'High', 'Low', 'Currency', 'Exchange'], axis = 'columns', inplace=True)
    dfETF["Ticker"] = "PHAU"
    dfETF['Date'] = pd.date_range(start=stocks_start.strftime('%d/%m/%Y'), periods=len(dfETF), freq='D')
    #dfETF['Date'] = [d.strftime('%Y-%m-%d') if not pd.isnull(d) else '' for d in dfETF['Date']]
    print('dataETF:', dfETF)


    # GETDATA EEUU EN YFINANCE
    daily_adj_close = pa.get_data(symbols, stocks_start, stocks_end)
    daily_adj_close = daily_adj_close[['Close']].reset_index()
    daily_adj_close=daily_adj_close.append(dfETF,ignore_index=True)
    print('el precio de cierre de todo el periodo seleccionado es:', daily_adj_close) #Ofrece el precio de cierre de todo el periodo seleccionado
    daily_benchmark = pa.get_benchmark(['SPY'], stocks_start, stocks_end)
    daily_benchmark = daily_benchmark[['Date', 'Close']]
    market_cal = pa.create_market_cal(stocks_start, stocks_end)
    #print('market_cal:', market_cal)
    active_portfolio = pa.portfolio_start_balance(portfolio_df, stocks_start)
    cartera_activa = pa.cartera_start_balance(portfolio_df, stocks_start) #para poner lo de la fecha luego 
    print('active_portfolio:')
    print(active_portfolio)
    positions_per_day = pa.time_fill(active_portfolio, market_cal)
    print('positions_per_day:', positions_per_day)
    # modified_cost_per_share = pa.modified_cost_per_share(portfolio_df, daily_adj_close, stocks_start)
    # print('modified_cost_per_share:', modified_cost_per_share)
    combined_df = pa.per_day_portfolio_calcs(positions_per_day, daily_benchmark, daily_adj_close, stocks_start)
    print('combined_df:', combined_df)



    positions_summary = pu.get_position_summary(combined_df)#Movimiento.objects.all())
    valor_cartera_total_diaria = pu.get_valor_cartera_total_diaria(combined_df)
    
    #print(positions_summary)
    # print(positions_summary["Total Gain/Loss ($)"].iloc[-1])

    accounts = Cartera.objects.all()
    total_cash = sum((acct.capital_inicial for acct in accounts))

    estado_cuenta_cartera = pu.get_estado_cuenta_cartera(portfolio_df, total_cash)

    context = {
        "estado_cuenta_cartera": estado_cuenta_cartera.to_html(index=False, float_format=lambda x: '%.2f' % x),
        "valor_cartera_total_diaria": valor_cartera_total_diaria.to_html(index=False, float_format=lambda x: '%.2f' % x),
        "positions": positions_summary.to_html(index=False, float_format=lambda x: '%.2f' % x),
        "accounts": [acct.nombre for acct in accounts],
        "cash_balances": {acct: acct.capital_inicial for acct in accounts},
        "total_cash": "{:,.2f}".format(total_cash),
        #"total_value": "{:,.2f}".format(total_cash + positions_summary["Market Value ($)"].iloc[0]),# + positions_summary["Total Gain/Loss ($)"].iloc[0]),
        "num_positions": positions_summary.shape[0] - 1,

        'latest_movimientos_list': movimientos_list,
        'cartera_actual_list': cartera_actual_list,
    }

    return render(request, 'micartera/index.html', context)


def charts(request):

    def get_graph_sales_year_month(self):
        
        data = []
        try:
            year = datetime.now().year
            for m in range(1, 13):
                total = Movimiento.objects.filter(date_joined__year=year, date_joined__month=m).aggregate(r=Coalesce(Sum('total'), 0)).get('r')
                data.append(float(total))
        except:
            pass
        return data

    graph_sales_year_month = self.get_graph_sales_year_month()#[49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4]
    
    context = {
        'graph_sales_year_month': graph_sales_year_month
    }

    return render(request, 'micartera/charts.html', context)