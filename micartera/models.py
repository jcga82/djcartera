from django.db import models
from datetime import datetime   
from django.db.models import Avg, Sum, F, Q, FloatField, Case, CharField, Value, When
from django.contrib import messages
import decimal

ESTRATEGIA_CHOICES = [
    ('Dividendos', 'Dividendos'),
    ('Trading', 'Trading'),
    ('Grow', 'Grow'),
    ('Largo', 'Largo Plazo'),
    ('Viviendas', 'Viviendas')
]

SECTOR_CHOICES = [
    ('ConsumoDef', 'Consumo Defensivo'),
    ('salud', 'Salud'),
    ('utilities', 'Serv. Públicos'),
    ('comunicaciones', 'Comunicaciones'),
    ('elect', 'Energía'),
    ('industrial', 'Industrial'),
    ('tecno', 'Tecnología'),
    ('materiales', 'Materiales'),
    ('consumoCic', 'Consumo Cíclico'),
    ('finanzas', 'Finanzas'),
    ('inmo', 'Inmobiliario'),
    ('otros', 'Otros')
]

MERCADO_CHOICES = [
    ('NYSE', 'NYSE'),
    ('NASDAQ', 'NASDAQ'),
    ('others', 'Otros'),
]

PAISES_CHOICES = [
    ('spain', 'España'),
    ('eeuu', 'EEUU'),
    ('others', 'Otros'),
]

TIPO_OPERACION_CHOICES = [
    ('BUY', 'Compra'),
    ('SELL', 'Venta'),
    ('CASH IN', 'Ingreso'),
    ('CASH OUT', 'Retirada'),
]

TIPO_MONEDA_CHOICES = [
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('GBP', 'GBX'),
    ('JPY', 'JPY'),
    ('otra', 'Otra'),
]

TIPO_ACTIVO_CHOICES = [
    ('a', 'Acción'),
    ('etf', 'ETF'),
    ('crypto', 'Crypto'),
    ('otros', 'Otros')
]

FECHAS_DIVIDENDOS_CHOICES = [
    ('14710', '1-4-7-10'),
    ('25811', '2-5-8-11'),
    ('36912', '3-6-9-12'),
    ('612', '6-12')
]

COMUNIDAD_CHOICES = [
    ('andalucia', 'Andalucía'),
    ('madrid', 'Madrid'),
]

class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    symbol = models.CharField(max_length=10)
    logo = models.CharField(max_length=50, default='')
    isin = models.CharField(max_length=20, default='')
    description = models.TextField(max_length=500)
    estrategia = models.CharField(max_length=15, choices=ESTRATEGIA_CHOICES, default='Largo')
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default='otros')
    industria = models.CharField(max_length=80, default='')
    sic = models.CharField(max_length=10, default='')
    sicSector = models.CharField(max_length=80, default='')
    sicIndustry = models.CharField(max_length=80, default='')
    currency = models.CharField(max_length=10, default='')
    location = models.CharField(max_length=80, default='')
    mercado = models.CharField(max_length=10, choices=MERCADO_CHOICES, default='otros')
    pais = models.CharField(max_length=20, choices=PAISES_CHOICES, default='spain')
    tipo = models.CharField(max_length=10, choices=TIPO_ACTIVO_CHOICES, default='a')
    #bolsa = models.CharField(max_length=20, choices=PAISES_CHOICES, default='IBEX')
    dividendo_desde = models.CharField(max_length=4, default='0000')
    fechas_dividendo = models.CharField(max_length=10, choices=FECHAS_DIVIDENDOS_CHOICES, default='14710')
    cagr3 = models.FloatField(default=0)
    cagr5 = models.FloatField(default=0)
    pub_date = models.DateTimeField('fecha alta', default=datetime.now, blank=True)

    def __str__(self):
        return self.symbol

class Cartera(models.Model):
    # id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    capital_inicial = models.DecimalField(default=0, decimal_places=4, max_digits=20)
   # cash_balance = models.FloatField(default=0.0)
    
    @property
    def estado_cuenta(self):
        compras = Movimiento.objects.filter(tipo='c').aggregate(
            total=Sum(F('precio') * F('acciones'), output_field=FloatField()))['total']
        ventas = Movimiento.objects.filter(tipo='v').aggregate(
            total=Sum(F('precio') * F('acciones'), output_field=FloatField()))['total']
        if ventas is not None:
            return float(self.capital_inicial) - compras + ventas
        else:
            return float(self.capital_inicial) - compras

    # @property
    # def acciones_cuenta(self):
    #     return Movimiento.objects.values(
    #         'empresa', 'tipo'
    #     ).annotate(
    #         total_acciones=Sum('acciones'),
    #         precio_promedio=Avg(F('precio') * F('acciones') / F('acciones'), output_field=FloatField())
    #     )

    def __str__(self):
        return self.nombre

class Movimiento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    cartera = models.ForeignKey(Cartera, on_delete=models.CASCADE, blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_OPERACION_CHOICES, default='compra')
    acciones = models.IntegerField(default=0)
    precio = models.DecimalField(default=0, decimal_places=4, max_digits=20)
    moneda = models.CharField(max_length=10, choices=TIPO_MONEDA_CHOICES, default='usd')
    cambio_moneda = models.DecimalField(default=0, decimal_places=4, max_digits=10)
    comision = models.DecimalField(default=0, decimal_places=4, max_digits=10)
    fecha = models.DateTimeField(default=datetime.now, blank=True, null=True)
    total_acciones = models.IntegerField(default=0)

    @property
    def coste_operacion(self):
        return round(float(self.precio * self.acciones / self.cambio_moneda), 2)

    @property
    def coste_total(self):
        if self.tipo == 'compra':
            return '%.2f' % (decimal.Decimal(self.coste_operacion) + self.comision)
        elif self.tipo == 'venta':
            return '%.2f' % (decimal.Decimal(self.coste_operacion) - self.comision)
        else:
            return self.coste_operacion

    def __str__(self):
        return self.tipo + ' ' +  str(self.acciones) + ' ' + self.empresa.nombre

    def save(self, *args, **kwargs):
        p = Movimiento.objects.filter(empresa=self.empresa)
        print(len(p))
        print(p.last())
        if self.pk is not None: # The instance is being created
            print('ya existe, estoy actualizando el id', self.pk) #todo


        # Compruebo si ya tengo esa accion
        if p.last():
            print(p.last().total_acciones, self.acciones)
            if self.tipo == 'BUY':
                self.total_acciones = p.last().total_acciones + self.acciones
            else:
                # Compruebo que tenga al menos las que quiero vender
                if p.last().total_acciones >= self.acciones:
                    self.total_acciones = p.last().total_acciones - self.acciones
                else:
                    print('No hay suficientes acciones para vender1')
                    # messages.info('¡No hay suficientes acciones para vender!')
                    return
        else:
            self.total_acciones = self.acciones
        super(Movimiento, self).save(*args, **kwargs)


class ProfitCartera(models.Model):
    cartera = models.ForeignKey(Cartera, on_delete=models.CASCADE)
    fecha = models.DateField()
    valor = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    balance = models.FloatField(default=0)

    def __str__(self):
        return str(self.cartera)


class FundamentalesEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fiscalDateEnding = models.CharField(max_length=20)
    num_acciones = models.IntegerField(default=0)
    markercap = models.FloatField('MCap (mill$)', default=0)
    ebitda = models.FloatField(default=0)
    per = models.FloatField('PER', default=0)
    beta = models.FloatField(default=0)
    bpa = models.FloatField('BPA', default=0)
    dpa = models.FloatField('DPA', default=0)
    dya = models.FloatField('Div(%)', default=0)
    fechaDividendo = models.CharField('Fecha Div', max_length=50)
    fechaDividendoEx = models.CharField('Fecha ExDiv',max_length=50)
    # PRICES AVG
    WeekHighYear = models.FloatField('Max', default=0)
    WeekLowYear = models.FloatField('Min', default=0)
    DayMovingAverage50 = models.FloatField('MMA50', default=0)
    DayMovingAverage200 = models.FloatField('MMA200', default=0)

    pub_date = models.DateTimeField('Publicado el', default=datetime.now, blank=True)

    @property
    def precio(self):
        return self.markercap / self.num_acciones
    # @property
    # def rent_div(self):
    #     return round(self.dya *100, 2)
    def __str__(self):
     return str(self.empresa) + ' ' + self.fiscalDateEnding


class DividendoEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    date = models.CharField(max_length=40)
    dividendo = models.FloatField(default=0)

    def __str__(self):
     return str(self.empresa)

class HistoricoEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fiscalDateEnding = models.CharField(max_length=20)
    reportedEPS = models.FloatField(default=0)
    dividendPayout = models.FloatField(default=0)
    commonStockSharesOutstanding = models.FloatField(default=0)
    netIncome = models.IntegerField(default=0)
    #cuenta resultados
    totalRevenue = models.IntegerField(default=0)
    costOfRevenue = models.IntegerField(default=0)
    ebitda = models.IntegerField(default=0)
    dandp = models.IntegerField(default=0)
    tax = models.IntegerField(default=0)
    interests = models.IntegerField(default=0)
    #sheet
    totalCurrentAssets = models.IntegerField(default=0)
    totalNonCurrentAssets = models.IntegerField(default=0)
    totalCurrentLiabilities = models.IntegerField(default=0)
    totalNonCurrentLiabilities = models.IntegerField(default=0)
    shortTermDebt = models.IntegerField(default=0)
    longTermDebt = models.IntegerField(default=0)
    #cashlow
    operatingCashflow = models.IntegerField(default=0)
    cashflowFromInvestment = models.IntegerField(default=0)
    cashflowFromFinancing = models.IntegerField(default=0)
    capitalExpenditures = models.IntegerField(default=0)
    paymentsForRepurchaseOfCommonStock = models.IntegerField(default=0)

    @property
    def grossProfit(self):
        return self.totalRevenue - self.costOfRevenue
    @property
    def ebit(self):
        return self.ebitda - self.dandp
    @property
    def ebt(self):
        return self.ebit - self.tax
    @property
    def netIncomeCalculated(self):
        return self.ebt - self.interests

    @property
    def bpa(self):
        try:
            return round(self.netIncome / self.commonStockSharesOutstanding,2)
        except:
            return 0 
    
    @property
    def dpa(self):
        try:
            return round(self.dividendPayout / self.commonStockSharesOutstanding,2)
        except:
            return 0 
    
    @property
    def payout(self):
        try:
            return round((self.dpa / self.bpa) * 100, 0)
        except:
            return 0 


    def __str__(self):
     return str(self.empresa) + ' ' + self.fiscalDateEnding


class QHistoricoEmpresa(models.Model):
    historico = models.ForeignKey(HistoricoEmpresa, on_delete=models.CASCADE)
    confirmado = models.BooleanField(default=True)
    fiscalDateEnding = models.CharField(max_length=20)
    reportedDate = models.CharField(max_length=20)
    reportedEPS = models.FloatField(default=0)
    estimatedEPS = models.FloatField(default=0)
    estimatedTotalRevenue = models.FloatField(default=0)
    totalRevenue = models.FloatField(default=0)
    netIncome = models.FloatField(default=0)
    TextField = models.TextField(max_length=255, default="")

##########################################################################

class Vivienda(models.Model):
    id = models.AutoField(primary_key=True)
    cartera = models.ForeignKey(Cartera, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15, choices=ESTRATEGIA_CHOICES, default='Viviendas')
    direccion = models.CharField(max_length=80)
    comunidad = models.CharField(max_length=20, choices=COMUNIDAD_CHOICES, default='andalucia')
    valor_cv = models.IntegerField(default=0)
    gastos_cv = models.IntegerField(default=0)
    gastos_reforma = models.IntegerField(default=0)
    ingresos_mensuales = models.IntegerField(default=0)

    gastos_ibi = models.IntegerField(default=0)
    gastos_seguros = models.IntegerField(default=0)
    gastos_comunidad = models.IntegerField(default=0)

    financiacion = models.BooleanField(default=False)
    pct_finan = models.FloatField(default=70)
    plazo = models.IntegerField(default=20)
    interes = models.FloatField(default=1.0)


    @property
    def pct_itp(self):
        if (self.comunidad == 'andalucia'):
            return 7
        else:
            return 8

    @property
    def itp(self):
        return round(self.pct_itp /100 * self.valor_cv )

    @property
    def total_compra(self):
        return round(self.valor_cv + self.itp + self.gastos_cv + self.gastos_reforma)

    @property
    def ingresos_anuales(self):
        return self.ingresos_mensuales * 12

    @property
    def gastos_anuales(self):
        return self.gastos_ibi + self.gastos_seguros + self.gastos_comunidad

    @property
    def rent_bruta(self):
        try:
            return round((self.ingresos_anuales / self.total_compra) * 100, 2)
        except:
            return 0 
    
    @property
    def rent_neta(self):
        try:
            return round(( (self.ingresos_anuales - self.gastos_anuales) / self.total_compra) * 100, 2)
        except:
            return 0 

    @property
    def valor_hipoteca(self):
        if (self.financiacion):
            return self.valor_cv * self.pct_finan / 100
        else:
            return 0
    
    @property
    def capital_aportar(self):
        if (self.financiacion):
            return round(self.valor_cv - self.valor_hipoteca)
        else:
            return round(self.valor_cv)

    @property
    def cuota_hipoteca_mes(self):
        if (self.financiacion):
            self.plazo = self.plazo * 12
            self.interes = (self.interes / 100) / 12
            return round(self.valor_hipoteca * ( (self.interes * ((1 + self.interes)**self.plazo)) / (((1 + self.interes)**self.plazo) - 1 ) ),2)
        else:
            return 0

    @property
    def cash_flow(self):
        if (self.financiacion):
            return round(self.ingresos_mensuales - (self.gastos_anuales / 12) - self.cuota_hipoteca_mes, 2)
        else:
            return round(self.ingresos_mensuales - (self.gastos_anuales / 12), 2)

    @property
    def roce(self):
        try:
            return round( (self.cash_flow * 12) * 100 / self.capital_aportar, 2)
        except:
            return 0 

    def __str__(self):
        return str(self.direccion)



class RentaPasiva(models.Model):
    cartera = models.ForeignKey(Cartera, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15, choices=ESTRATEGIA_CHOICES, default='Dividendos')
    fecha_cobro = models.DateField()
    cantidad = models.FloatField(default=0)

    def __str__(self):
        return str(self.cartera)



class Cripto(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=80)
    symbol = models.CharField(max_length=10)
    category = models.CharField(max_length=20, default='')
    description = models.TextField(max_length=500, default='')
    logo = models.CharField(max_length=50, default='')
    technical_doc = models.CharField(max_length=50, default='')
    date_added = models.DateField(default=datetime.now, blank=True)

    def __str__(self):
     return str(self.nombre)


class FundamentalesCripto(models.Model):
    cripto = models.ForeignKey(Cripto, on_delete=models.CASCADE)
    last_updated = models.DateField(default=datetime.now, blank=True)
    cmc_rank = models.IntegerField(default=0)
    precio = models.FloatField(default=0)
    marketcap = models.FloatField(default=0)
    tags = models.CharField(max_length=100)
    max_supply = models.FloatField(default=0)
    total_supply = models.FloatField(default=0) 
    market_cap_dominance = models.FloatField(default=0) 
    percent_change_24h = models.FloatField(default=0) 
    percent_change_7d = models.FloatField(default=0) 
    percent_change_30d = models.FloatField(default=0) 
    percent_change_60d = models.FloatField(default=0) 
    percent_change_90d = models.FloatField(default=0) 

    def __str__(self):
        return str(self.cripto) + ' ' + str(self.last_updated)

class AnalisisCripto(models.Model):
    cripto = models.ForeignKey(Cripto, on_delete=models.CASCADE)
    last_updated = models.DateField(default=datetime.now, blank=True)
    porc_ballenas = models.FloatField(default=0) 
    mineria = models.TextField(max_length=500, default='')
    roadmap = models.TextField(max_length=500, default='')
    proyeccion = models.TextField(max_length=500, default='')

    def __str__(self):
        return str(self.cripto) + ' ' + str(self.last_updated)

##########################################################################

class HistoricoCasillas(models.Model):
    address = models.CharField(max_length=50)
    casilla = models.IntegerField(default=0)
    hblocks = models.IntegerField(default=0)
    date = models.DateTimeField('fecha', default=datetime.now, blank=True)