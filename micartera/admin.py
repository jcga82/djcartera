from django.contrib import admin
from .models import Cripto, DividendoEmpresa, Empresa, FundamentalesCripto, FundamentalesEmpresa, Cartera, Movimiento, HistoricoEmpresa, QHistoricoEmpresa, RentaPasiva, Vivienda, HistoricoCasillas, AnalisisCripto, ProfitCartera
from .forms import CategoryFieldForm
from django.utils.html import mark_safe
import requests
#import investpy
import csv, operator
import os
from datetime import datetime   
from decimal import *
from django.db import models
from django.forms import TextInput, Textarea
from requests import Session
from import_export import resources
from import_export.admin import ImportExportModelAdmin
import json
import pandas as pd
# from investpy.portfolio_value import Portfolio
from .portfolio_value import Portfolio 
from sec_api import MappingApi
myApi = "4287ef1a74898bbb0f8b2cb809fcda4be555686b49a0d2f09594ded6f1f86e29"

def download_datos_sec(self, request, queryset):
    mappingApi = MappingApi(myApi)
    result1 = mappingApi.resolve("ticker", queryset[0].symbol)
    print(result1)

def get_movimientos(self, request, queryset):
    movimientos = Movimiento.objects.filter(cartera=queryset[0].id).values('fecha', 'empresa__nombre', 'empresa__symbol', 'tipo', 'acciones', 'total_acciones', 'precio', 'moneda', 'cambio_moneda', 'comision')
    # print(movimientos)
    df = pd.DataFrame.from_records(movimientos) #, columns=['empresa']
    # print(df['empresa_id'].describe())
    df['total_usd'] = df['precio'].astype(float) #df['acciones'] * 
    df['comision'] = df['comision'].astype(float)
    df['precio'] = df['precio'].astype(float)
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date #, format='%Y%m%d'
    df['date'] = df['fecha'].astype('datetime64[ns]')

    #Calculo las acciones que tengo de cada una
    df['total_shares_held'] = df['total_acciones'].astype(float)
    #df.loc[df['empresa__symbol'] == 'TSLA', 'acciones'].sum()
    operaciones = df.groupby(['empresa__symbol', 'tipo'])['acciones'].agg('sum')
    print(operaciones)
    print(operaciones.reset_index(name='count'))
    # print('group:', operaciones.loc[operaciones['tipo']=='BUY']).size


    # df = df.rename(columns={
    #     'tipo':'action',
    #     'empresa__nombre':'company',
    #     'empresa__symbol':'yahoo_ticker',
    #     'moneda':'currency',
    #     'acciones':'num_shares', 
    #     'precio':'stock_price_usd',
    #     'comision':'trading_costs_usd', 
    #     # 'total_acciones':'total_shares_held'
    #     })
    # print(df)
    # pf = Portfolio(df)
    # value = pf.portfolio_value_usd
    # profit = pf.profit
    # balance = pf.cash.daily_cash_balance
    # print(pf.portfolio_value_usd)
    # print(profit)
    # merge = pd.concat([value, profit, balance], axis=1)
    # print(merge)
    # print("Se está guardando un registro de profit diario en cartera...")
    # for (index,row) in merge.iterrows():
    #     ProfitCartera.objects.get_or_create(
    #                 cartera = queryset[0],
    #                 fecha = index.date(),
    #                 valor = round(row[0],2), 
    #                 profit = round(row[1],2),
    #                 balance = round(row['pf_cash_balance'],2)
    #                 )

def cambia_dividendos(modeladmin, request, queryset):
    queryset.update(estrategia='Dividendos')

def calcula_cagr(modeladmin, request, queryset):
    for i in queryset:
        empresa = Empresa.objects.filter(symbol=i.symbol).first()
        dividendos = DividendoEmpresa.objects.filter(empresa=empresa.id)
        # Calcular el cagr de los 5 ultimos años
        v20 = 0
        v17 = 0
        v15 = 0
        cagr = 0
        for dividendo in dividendos:
            if dividendo.date == '2020':
                v20 = dividendo.dividendo
                print('2020: ', dividendo.dividendo)
            if dividendo.date == '2017':
                v17 = dividendo.dividendo
            if dividendo.date == '2015':
                v15 = dividendo.dividendo
                print('2016: ', dividendo.dividendo)
            cagr3 = ((v20 / v17)**(1/3))-1 if v15 != 0 else 0
            cagr5 = ((v20 / v15)**(1/5))-1 if v15 != 0 else 0
        # print(cagr5,empresa.cagr5)
        Empresa.objects.filter(symbol=i.symbol).update(cagr5=round(cagr5*100, 2))
        Empresa.objects.filter(symbol=i.symbol).update(cagr3=round(cagr3*100, 2))

def carga_csv_degiro(self, request, queryset):
    print(queryset)
    cartera = Cartera.objects.all()
    tipo = ''
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, 'Transactions.csv')
    with open(my_file) as csvarchivo:
        entrada = csv.DictReader(csvarchivo, delimiter=',')
        line_count = 0
        for row in entrada:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            #print(f'\t{row["ISIN"]} works in the {row["Bolsa"]} department, and was born in {row["Precio"]}.')
            if Empresa.objects.filter(isin=row["ISIN"]).exists(): #US6541101050
                empresa = Empresa.objects.get(isin=row["ISIN"])
                if float(row["Número"]) > 0:
                    tipo = 'c'
                else:
                    tipo = 'v'
                print(row["Fecha"])
                fecha = row["Fecha"]+ ' ' + row["Hora"]
                fecha = datetime.strptime(fecha, '%d-%m-%Y %H:%M')
                print(fecha)
                try:
                    tipo_cambio = float(row["Tipo de cambio"])
                except:
                    tipo_cambio = 1.0
                mov = Movimiento(empresa=empresa, cartera=cartera[0], tipo=tipo, acciones=abs(float(row["Número"])), precio=float(row["Precio"]), cambio_moneda=tipo_cambio, fecha=fecha) #comision=float(row["Comisión"]))
                print(mov)
                mov.save()
            else:
                print("OJO, No hay empresa en Empresas con el ISIN: %s" % (row["ISIN"]))
            #mov = Movimiento(1, 1)
            line_count += 1
        print(f'Processed {line_count} lines.')
        # for reg in entrada:
        #     print(reg) #['Fecha', 'Hora', 'Producto', 'ISIN', 'Bolsa', 'Número', '', 'Precio', '', 'Valor local', '', 'Valor', 'Tipo de cambio', '', 'Comisión', '', 'Total', 'ID Orden']

def addFiscal(array1, array2, array3, array4, listaFinal, year):
    dicc = []
    for i in array1['annualReports']:
        if (i['fiscalDateEnding'][0:4] == year):
            dicc.append(i)
    for i in array2['annualReports']:
        if (i['fiscalDateEnding'][0:4] == year):
            dicc.append(i)
    for i in array3['annualEarnings']:
        if (i['fiscalDateEnding'][0:4] == year):
            dicc.append(i) 
    for i in array4['annualReports']:
        if (i['fiscalDateEnding'][0:4] == year):
            dicc.append(i) 
    listaFinal.append(dicc)


def addFiscalQ(array1, array3, listaFinal, year):
    t1 = []
    t2 = []
    t3 = []
    t4 = []
    for i in array1['quarterlyReports']:
        if (i['fiscalDateEnding'][0:4] == year):
            if (i['fiscalDateEnding'][5:7] == '01' or i['fiscalDateEnding'][5:7] == '02' or i['fiscalDateEnding'][5:7] == '03'):
                i['trimestre']='Q1'
                t1.append(i)
            if (i['fiscalDateEnding'][5:7] == '04' or i['fiscalDateEnding'][5:7] == '05' or i['fiscalDateEnding'][5:7] == '06'):
                i['trimestre']='Q2'
                t2.append(i)
            if (i['fiscalDateEnding'][5:7] == '07' or i['fiscalDateEnding'][5:7] == '08' or i['fiscalDateEnding'][5:7] == '09'):
                i['trimestre']='Q3'
                t3.append(i)
            if (i['fiscalDateEnding'][5:7] == '10' or i['fiscalDateEnding'][5:7] == '11' or i['fiscalDateEnding'][5:7] == '12'):
                i['trimestre']='Q4'
                t4.append(i)
    for i in array3['quarterlyEarnings']:
        if (i['fiscalDateEnding'][0:4] == year):
            if (i['fiscalDateEnding'][5:7] == '01' or i['fiscalDateEnding'][5:7] == '02' or i['fiscalDateEnding'][5:7] == '03'):
                i['trimestre']='Q1'
                t1.append(i)
            if (i['fiscalDateEnding'][5:7] == '04' or i['fiscalDateEnding'][5:7] == '05' or i['fiscalDateEnding'][5:7] == '06'):
                i['trimestre']='Q2'
                t2.append(i)
            if (i['fiscalDateEnding'][5:7] == '07' or i['fiscalDateEnding'][5:7] == '08' or i['fiscalDateEnding'][5:7] == '09'):
                i['trimestre']='Q3'
                t3.append(i)
            if (i['fiscalDateEnding'][5:7] == '10' or i['fiscalDateEnding'][5:7] == '11' or i['fiscalDateEnding'][5:7] == '12'):
                i['trimestre']='Q4'
                t4.append(i)
    listaFinal.append(t1)
    listaFinal.append(t2)
    listaFinal.append(t3)
    listaFinal.append(t4)

def descarga_trimestres(self, request, queryset):
    lista = []
    obj = HistoricoEmpresa.objects.filter(empresa=queryset[0].empresa)
    print(obj, queryset[0].fiscalDateEnding)
    earn = requests.get('https://www.alphavantage.co/query?function=EARNINGS&symbol=' + queryset[0].empresa.symbol + '&apikey=RW3ZTFLNEG0J1XWE')
    earnings = earn.json()
    income = requests.get('https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=' + queryset[0].empresa.symbol + '&apikey=RW3ZTFLNEG0J1XWE')
    incomes = income.json()

    addFiscalQ(incomes, earnings, lista, queryset[0].fiscalDateEnding)

    print(lista)
    for i in lista:
        if (i[0]['fiscalDateEnding'][0:4] == queryset[0].fiscalDateEnding):
            QHistoricoEmpresa.objects.create(
                    historico = obj[0], 
                    fiscalDateEnding = i[1]['fiscalDateEnding'],
                    reportedDate = i[1]['reportedDate'],
                    reportedEPS = i[1]['reportedEPS'],
                    estimatedEPS = i[1]['estimatedEPS'],
                    totalRevenue = i[0]['totalRevenue'],
                    netIncome = i[0]['netIncome']
                )

def descarga_registros(self, request, queryset):

    lista = []
    obj = Empresa.objects.get(symbol=queryset[0].symbol)

    for i in queryset:
        # perfil = investpy.get_stock_company_profile(stock=i.symbol, country=i.pais)
        perfil = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=' + i.symbol + '&apikey=RW3ZTFLNEG0J1XWE')
        respuesta = perfil.json()
        # print(respuesta)
        income = requests.get('https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=' + i.symbol + '&apikey=RW3ZTFLNEG0J1XWE')
        incomes = income.json()
        earn = requests.get('https://www.alphavantage.co/query?function=EARNINGS&symbol=' + i.symbol + '&apikey=RW3ZTFLNEG0J1XWE')
        earnings = earn.json()
        cash = requests.get('https://www.alphavantage.co/query?function=CASH_FLOW&symbol=' + i.symbol + '&apikey=RW3ZTFLNEG0J1XWE')
        cashflow = cash.json()
        balance = requests.get('https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol=' + i.symbol + '&apikey=RW3ZTFLNEG0J1XWE')
        balancesheet = balance.json()


        addFiscal(incomes, cashflow, earnings, balancesheet, lista, '2021')
        addFiscal(incomes, cashflow, earnings, balancesheet, lista, '2020')
        addFiscal(incomes, cashflow, earnings, balancesheet, lista, '2019')
        addFiscal(incomes, cashflow, earnings, balancesheet, lista, '2018')


    print(lista)

    if (HistoricoEmpresa.objects.filter(empresa=obj.id).count() != 0):
        print('Ya tiene historico...')
        pass

    else:
        for i in lista:
            divPayout = 0
            repurchaseOfCommonStock = 0
            if obj.estrategia == 'Dividendos':
                try:
                    divPayout = i[1]['dividendPayout']
                    repurchaseOfCommonStock = 0 if i[1]['paymentsForRepurchaseOfCommonStock'] is None else 1
                except:
                    print('error al obtener dividendo o recompra acciones')
                
            HistoricoEmpresa.objects.create(
                empresa_id = obj.id, 
                fiscalDateEnding = i[0]['fiscalDateEnding'][0:4],
                dividendPayout = divPayout,
                operatingCashflow = i[1]['operatingCashflow'],
                cashflowFromInvestment = i[1]['cashflowFromInvestment'],
                cashflowFromFinancing = i[1]['cashflowFromFinancing'],
                #para FCF
                capitalExpenditures = i[1]['capitalExpenditures'],
                paymentsForRepurchaseOfCommonStock = repurchaseOfCommonStock,

                reportedEPS = i[2]['reportedEPS'],

                commonStockSharesOutstanding= i[3]['commonStockSharesOutstanding'],
                totalCurrentAssets = i[3]['totalCurrentAssets'],
                totalNonCurrentAssets = i[3]['totalNonCurrentAssets'],
                totalCurrentLiabilities = i[3]['totalCurrentLiabilities'],
                totalNonCurrentLiabilities = i[3]['totalNonCurrentLiabilities'],
                shortTermDebt = 0 if i[3]['shortTermDebt'] is None else 1,
                longTermDebt = 0 if i[3]['longTermDebt'] is None else 1,
                
                totalRevenue = i[0]['totalRevenue'],
                costOfRevenue = i[0]['costOfRevenue'],
                ebitda = i[0]['ebitda'],
                dandp = i[0]['depreciationAndAmortization'],
                tax = i[0]['incomeTaxExpense'],
                interests = i[0]['interestExpense'],
                netIncome = i[0]['netIncome']
                )

    if (FundamentalesEmpresa.objects.filter(empresa=obj.id).count() != 0):
        print('Ya tiene fundamentales...')
        pass
    else:
        FundamentalesEmpresa.objects.create(
                empresa_id = obj.id, 
                fiscalDateEnding = lista[0][0]['fiscalDateEnding'][0:4],
                # num_acciones = int(lista[0][0]['commonStockSharesOutstanding']),
                markercap = float(respuesta['MarketCapitalization'])/1000000,
                ebitda = round(float(respuesta['EBITDA'])/1000000,0),
                per = respuesta['PERatio'],
                bpa = float(respuesta['EPS']),
                # DIVIDENDOS
                dpa = float(respuesta['DividendPerShare']),
                dya = round(float(respuesta['DividendYield'])*100,2),
                fechaDividendo = respuesta['DividendDate'],
                fechaDividendoEx= respuesta['ExDividendDate'],
                # PRICES AVG
                WeekHighYear = respuesta['52WeekHigh'],
                WeekLowYear = respuesta['52WeekLow'],
                DayMovingAverage50 = respuesta['50DayMovingAverage'],
                DayMovingAverage200 = respuesta['200DayMovingAverage'],
                
                # beneficios = 0 if perfil['beneficios'] == 'N/A' else float(perfil['beneficios'].replace('B', '000000')),
                # valor_bursatil = float(perfil['valor_bursatil'].replace('B', '')),
                # proximos_resultados = perfil['proximos_resultados']
            )         


descarga_registros.short_description = "Descarga Registros"

def duplicate_event(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()
duplicate_event.short_description = "Duplicar registro seleccionado"

def format_date(self, obj):
    return obj.date.strftime('%b, %Y')

format_date.admin_order_field = 'date'
format_date.short_description = 'Fecha'


class MovimientoInline(admin.TabularInline):
    model = Movimiento
    extra = 0
    ordering = ('-fecha',)

    # fields = ('empresa', 'tipo', 'acciones_cuenta')
    # readonly_fields = ('empresa', 'tipo', 'acciones_cuenta')

class DividendoInline(admin.TabularInline):
    model = DividendoEmpresa
    extra = 0

class HistoricoInline(admin.TabularInline):
    model = HistoricoEmpresa
    extra = 0
    fields = ('fiscalDateEnding', 'bpa', 'dpa', 'payout', 'reportedEPS', 'totalRevenue')
    readonly_fields = ('fiscalDateEnding', 'bpa', 'payout', 'dpa')

class FundamentalesInline(admin.StackedInline):
    model = FundamentalesEmpresa
    extra = 0
    readonly_fields = ('fiscalDateEnding','ebitda', 'per', 'bpa', 'dpa', 'dya')
    fieldsets = [
        (None, 
        {'fields': 
            [   ('per', 'dya','bpa', 'dpa'), 
                ('fiscalDateEnding','num_acciones', 'markercap'),
                ('fechaDividendo', 'fechaDividendoEx'),
            ]
        }),
    ]
    verbose_name = 'Fundamentales'
    verbose_name_plural = 'Fundamentales'

class DividendoResource(resources.ModelResource):
    class Meta:
        model = DividendoEmpresa

class DividendoEmpresaAdmin(ImportExportModelAdmin):
    resource_class = DividendoResource
    list_display = ('empresa', 'date', 'dividendo')

class EmpresaResource(resources.ModelResource):
    class Meta:
        model = Empresa

class QHistoricoInline(admin.TabularInline):
    model = QHistoricoEmpresa
    extra = 0
    fields = ('fiscalDateEnding', 'confirmado', 'reportedDate', 'reportedEPS', 'estimatedEPS', 'totalRevenue', 'netIncome')

class HistoricoEmpresaAdmin(ImportExportModelAdmin):
    fieldsets = [
        ('Información general',               
            {'fields': 
                [('empresa', 'fiscalDateEnding'), ('reportedEPS', 'dividendPayout', 'commonStockSharesOutstanding'), 
                ]},
        ),
        ('Cuenta Resultados',               
            {'fields': 
                [('totalRevenue', 'costOfRevenue', 'ebitda'), ('dandp', 'interests', 'tax'),
                ('netIncome'),
                ]
            },
        ),
        ('Balance',               
            {'fields': 
                [('totalCurrentAssets', 'totalNonCurrentAssets'), 
                ('totalCurrentLiabilities', 'totalNonCurrentLiabilities', 'shortTermDebt', 'longTermDebt')]
            },
        ),
        ('CashFlow',               
            {'fields': 
                [('operatingCashflow', 'cashflowFromInvestment', 'cashflowFromFinancing'), 
                ('capitalExpenditures', 'paymentsForRepurchaseOfCommonStock')]
            },
        ),
        # ('Otros', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    list_display = ('fiscalDateEnding', 'empresa', 'reportedEPS', 'dividendPayout', 'commonStockSharesOutstanding', 'netIncome', 'totalRevenue', 'ebitda', )
    actions = [descarga_trimestres]
    inlines = [QHistoricoInline]
    list_filter = ['fiscalDateEnding', 'empresa']

class QHistoricoEmpresaAdmin(ImportExportModelAdmin):
    list_display = ('fiscalDateEnding', 'confirmado', 'historico', 'reportedDate', 'reportedEPS', 'estimatedEPS', 'totalRevenue', 'netIncome')
    list_filter = ['confirmado', 'fiscalDateEnding', 'historico']

class EmpresaAdmin(ImportExportModelAdmin):
    resource_class = EmpresaResource
    form = CategoryFieldForm
    fieldsets = [
        ('Información general',               
            {'fields': 
                [('nombre', 'symbol'), ('pais', 'mercado', 'currency', 'location'), ('sector', 'industria', 'sicSector', 'sicIndustry'), ('logo', 'isin', 'tipo'), ('description'), 
                ('estrategia', 'dividendo_desde', 'fechas_dividendo'), ('cagr3', 'cagr5'), ('pub_date')
                ]},
        ),
        #('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    readonly_fields = ["pub_date"]
    list_display = ('nombre', 'symbol', 'estrategia', 'sector', 'cagr5', 'fund_count', 'hist_count', 'dividentos_count', 'perc_div')
    list_filter = ['estrategia', 'pub_date', 'sector', 'pais']
    exclude = []
    actions = [cambia_dividendos, descarga_registros, calcula_cagr, download_datos_sec]
    inlines = [FundamentalesInline, HistoricoInline, DividendoInline, MovimientoInline]

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        # models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    # def change_view(self, request, object_id, extra_context=None):
    #     print(request)       
    #     self.exclude = ['fechas_dividendo', ]
        
    #     return super(EmpresaAdmin, self).change_view(request, object_id, extra_context)

    # def get_form(self, request, obj=None, **kwargs):
    #     if obj.estrategia == "Dividendos":
    #         print('eeee', self.exclude)
    #         self.exclude = ['dividendo_desde',]
    #         print('eeee', self.exclude)
    #         kwargs.update({
    #             'exclude': getattr(kwargs, 'exclude', tuple()) + ('',),
    #         })
    #     form = super(EmpresaAdmin, self).get_form(request, obj, **kwargs)
    #     return form
    def dividentos_count(self, obj):
        return obj.dividendoempresa_set.count()
    
    def fund_count(self, obj):
        return obj.fundamentalesempresa_set.count()
    
    def hist_count(self, obj):
        return obj.historicoempresa_set.count()
    
    def perc_div(self, obj):
        if (obj.fundamentalesempresa_set.all().first()):
            return obj.fundamentalesempresa_set.all().first()
        else:
            0

    class Media:
        js = ('admin/js/category-field-admin.js',)


class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'empresa', 'total_acciones', 'tipo', 'acciones', 'cambio_moneda', 'precio', 'coste_operacion', 'coste_total', )
    actions = [carga_csv_degiro, duplicate_event]
    list_filter = ['fecha', 'empresa', 'tipo']


class CarteraAdmin(admin.ModelAdmin):
    #readonly_fields = ('acciones_cuenta',)
    fieldsets = [
        ('Información general',               
            {'fields': 
                [('nombre', 'capital_inicial'),
                ]},
        ),
    ]
    list_display = ('nombre', 'capital_inicial')
    inlines = [MovimientoInline]
    actions = [get_movimientos]

    def clickable_site_domain(self, obj):
        return mark_safe(
            '<a href="%s">%s</a>' % (obj.nombre, obj.nombre)
        )

class ViviendaAdmin(admin.ModelAdmin):
    #readonly_fields = ('acciones_cuenta',)
    # fieldsets = [
    #     ('Información general',               
    #         {'fields': 
    #             [('cartera', 'capital_inicial'),
    #             ]},
    #     ),
    # ]
    list_display = ('direccion', 'itp', 'total_compra', 'gastos_anuales' ,'rent_bruta', 'rent_neta', 'valor_hipoteca', 'capital_aportar', 'cuota_hipoteca_mes', 'cash_flow', 'roce')

class RentaPasivaAdmin(admin.ModelAdmin):
    #readonly_fields = ('acciones_cuenta',)
    # fieldsets = [
    #     ('Información general',               
    #         {'fields': 
    #             [('cartera', 'capital_inicial'),
    #             ]},
    #     ),
    # ]
    list_display = ('cartera', 'fecha_cobro', 'tipo', 'cantidad')


def descarga_criptos(self, request, queryset):
    print(queryset[0])
    obj = Cripto.objects.filter(nombre=queryset[0].nombre)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    # url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '2cea63b7-7ec6-418a-b316-eab169aee75c',
    }
    parameters = {
        'symbol': queryset[0].symbol
        # 'start':'1',
        # 'limit':'10',
        # 'convert':'USD'
    }
    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        datos = data['data'][queryset[0].symbol]
        print(datos['quote']['USD']['last_updated'][0:10])
        FundamentalesCripto.objects.create(
                cripto = obj[0], 
                last_updated = datos['quote']['USD']['last_updated'][0:10],
                cmc_rank = datos['cmc_rank'],
                precio = round(datos['quote']['USD']['price']),
                marketcap= round(datos['quote']['USD']['market_cap']/1000000),
                max_supply = round(datos['max_supply']),
                total_supply = round(datos['total_supply']),
                market_cap_dominance = round(datos['quote']['USD']['market_cap_dominance']),
                percent_change_24h = round(datos['quote']['USD']['percent_change_24h'], 2),
                percent_change_7d = round(datos['quote']['USD']['percent_change_7d'], 2), 
                percent_change_30d = round(datos['quote']['USD']['percent_change_30d'], 2), 
                percent_change_60d = round(datos['quote']['USD']['percent_change_60d'], 2), 
                percent_change_90d = round(datos['quote']['USD']['percent_change_90d'], 2), 
            )
            
    except (ConnectionError) as e:
        print(e)


class CriptoAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'nombre', 'category', 'date_added', )
    actions = [descarga_criptos]
    list_filter = ['category', 'date_added']

class ProfitCarteraAdmin(admin.ModelAdmin):
    list_display = ('cartera', 'fecha', 'valor', 'profit', 'balance')
    list_filter = ['cartera', 'fecha']


admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Cartera, CarteraAdmin)
admin.site.register(Movimiento, MovimientoAdmin)
admin.site.register(FundamentalesEmpresa)
admin.site.register(DividendoEmpresa, DividendoEmpresaAdmin)
admin.site.register(Vivienda, ViviendaAdmin)
admin.site.register(HistoricoEmpresa, HistoricoEmpresaAdmin)
admin.site.register(QHistoricoEmpresa, QHistoricoEmpresaAdmin)
admin.site.register(RentaPasiva, RentaPasivaAdmin)
admin.site.register(Cripto, CriptoAdmin)
admin.site.register(FundamentalesCripto)
admin.site.register(AnalisisCripto)
admin.site.register(HistoricoCasillas)
admin.site.register(ProfitCartera, ProfitCarteraAdmin)
