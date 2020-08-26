from django.shortcuts import render
from .models import Movimiento, Cartera, Empresa
from django.db.models import Avg, Sum, F, Q, FloatField, Case, CharField, Value, When
from django.views.generic import TemplateView
from datetime import datetime
from . import portfolio_utils as pu
from . import portfolio_analysis as pa
from pyrtfolio.StockPortfolio import StockPortfolio
import pandas as pd
import os
from django_pandas.io import read_frame

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
    portfolio_df = read_frame(Movimiento.objects.all()) #pd.read_csv(my_file)
    portfolio_df['fecha'] = pd.to_datetime(portfolio_df['fecha'].dt.normalize())
    print('portfolio_df:', portfolio_df)

    symbols = portfolio_df.empresa.unique()
    # empresas = Empresa.objects.filter(nombre__in=empresas_cartera)
    # symbols = empresas.values_list('symbol', flat=True)
    # print(symbols)
    
    stocks_start = datetime(2020, 8, 5)
    stocks_end = datetime(2020, 8, 24)

    daily_adj_close = pa.get_data(symbols, stocks_start, stocks_end)
    daily_adj_close = daily_adj_close[['Close']].reset_index()
    #print(daily_adj_close) #Ofrece el precio de cierre de todo el periodo seleccionado
    daily_benchmark = pa.get_benchmark(['SPY'], stocks_start, stocks_end)
    daily_benchmark = daily_benchmark[['Date', 'Close']]
    market_cal = pa.create_market_cal(stocks_start, stocks_end)
    #print('market_cal:', market_cal)
    active_portfolio = pa.portfolio_start_balance(portfolio_df, stocks_start)
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

    context = {
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