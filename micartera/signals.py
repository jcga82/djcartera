from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .models import Movimiento, Vivienda, RentaPasiva, Cartera
            

@receiver(post_save, sender=Cartera)
def make_auto_renta_pasiva(sender, instance, **kwargs):
    if kwargs['created']:
        print("Se está guardando Renta Pasiva...", instance)
        #Comprobar antes que la accion comprada tenga dividendo
        for i in range(0,3):
            RentaPasiva.objects.create(
                cartera = instance,
                tipo = 'Dividendos',
                fecha_cobro = datetime.today() + relativedelta(months=+i), #fecha_dividendo
                cantidad = 20.1
                )

@receiver(post_save, sender=Vivienda)
def make_auto_renta_pasiva(sender, instance, **kwargs):
    if kwargs['created']:
        # se crean 12 pagos mensuales con la renta mensual. todo para el dia 5 de cada mes
        for i in range(1,12):
            RentaPasiva.objects.create(
                cartera = instance,
                tipo = 'Viviendas',
                fecha_cobro = datetime.today() + relativedelta(months=+i),
                cantidad = instance.ingresos_mensuales
                )