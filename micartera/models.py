from django.db import models
from datetime import datetime   
from django.db.models import Avg, Sum, F, Q, FloatField, Case, CharField, Value, When

STATUS_CHOICES = [
    ('a', 'Activo'),
    ('n', 'No activo'),
]

SECTOR_CHOICES = [
    ('auto', 'Automoción'),
    ('salud', 'Salud'),
    ('elect', 'Energía'),
    ('tecno', 'Tecnología'),
    ('bienes', 'Bienes de consumo'),
    ('otros', 'Otros')
]

PAISES_CHOICES = [
    ('spain', 'España'),
    ('united states', 'EEUU'),
    ('others', 'Otros'),
]

TIPO_OPERACION_CHOICES = [
    ('c', 'Compra'),
    ('v', 'Venta'),
]

class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    symbol = models.CharField(max_length=10)
    isin = models.CharField(max_length=20, default='')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='a')
    sector = models.CharField(max_length=10, choices=SECTOR_CHOICES, default='otros')
    pais = models.CharField(max_length=20, choices=PAISES_CHOICES, default='spain')
    #bolsa = models.CharField(max_length=20, choices=PAISES_CHOICES, default='IBEX')
    pub_date = models.DateTimeField('fecha alta', default=datetime.now, blank=True)

    def __str__(self):
        return self.nombre

class Cartera(models.Model):
    nombre = models.CharField(max_length=200)
    capital_inicial = models.DecimalField(default=0, decimal_places=2, max_digits=10)

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
    tipo = models.CharField(max_length=1, choices=TIPO_OPERACION_CHOICES, default='c')
    acciones = models.IntegerField(default=0)
    precio = models.DecimalField(default=0, decimal_places=4, max_digits=20)
    cambio_moneda = models.DecimalField(default=0, decimal_places=4, max_digits=10)
    fecha = models.DateTimeField(default=datetime.now, blank=True, null=True)

    @property
    def coste_operacion(self):
        return float(self.precio * self.acciones * self.cambio_moneda)

    @property
    def comision(self):
        if self.empresa.pais == 'united states':
            return float(self.coste_operacion * 0.002)
        else:
            return float(self.coste_operacion * 0.00125)

    @property
    def coste_total(self):
        if self.tipo == 'c':
            return '%.2f EUR' % (float(self.coste_operacion + self.comision))
        else:
            return '%.2f EUR' % (self.coste_operacion - self.comision)

    def __str__(self):
        return self.tipo + ' ' +  str(self.acciones) + ' ' + self.empresa.nombre

    def save(self, *args, **kwargs):
        if self.tipo == 'v':
            self.acciones = self.acciones * -1
        else:
            self.acciones = self.acciones
        super(Movimiento, self).save(*args, **kwargs)

class FundamentalesEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    beneficios = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    valor_bursatil = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    per = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    beta = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    num_acciones = models.IntegerField(default=0)
    proximos_resultados = models.CharField(max_length=50)
    pub_date = models.DateTimeField('date published', default=datetime.now, blank=True)
