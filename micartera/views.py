from django.shortcuts import render
from .models import Movimiento
from django.db.models import Avg, Sum, F, Q, FloatField, Case, CharField, Value, When


def index(request):
    latest_movimientos_list = Movimiento.objects.order_by('-fecha')[:5]
    cartera_actual_list = Movimiento.objects.values(
            'empresa__nombre'
        ).annotate(
            total_acciones=Sum('acciones'),
            #rentabilidad=Sum('coste_total'),
            coste_operacion=Sum(F('precio') * F('acciones') * F('cambio_moneda'), output_field=FloatField()),
            precio_promedio=Avg(F('precio') * F('acciones') / F('acciones'), output_field=FloatField())
        )
        # sales_price=Case(
        #     When(discount__isnull=True, then=F('price')),
        #     When(discount__isnull=False, then=(F('price') - (F('discount') * F('price')) / 100)),
        #     output_field=IntegerField(),
        # )

    print(cartera_actual_list)
    context = {
        'latest_movimientos_list': latest_movimientos_list,
        'cartera_actual_list': cartera_actual_list,
    }

    return render(request, 'micartera/index.html', context)