from django.contrib import admin
from .models import Empresa, FundamentalesEmpresa, Cartera, Movimiento
from django.utils.html import mark_safe

import investpy
import csv, operator
import os
from datetime import datetime   

def desactiva_empresa(modeladmin, request, queryset):
    queryset.update(status='n')

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

def descarga_registros(self, request, queryset):
    for i in queryset:
        perfil = investpy.get_stock_company_profile(stock=i.symbol, country=i.pais)
        obj = Empresa.objects.get(symbol=i.symbol)
        FundamentalesEmpresa.objects.create(
            empresa_id = obj.id, 
            num_acciones = int(perfil['num_acciones'].replace(',', '')),
            beneficios = 0 if perfil['beneficios'] == 'N/A' else float(perfil['beneficios'].replace('B', '000000')),
            valor_bursatil = float(perfil['valor_bursatil'].replace('B', '')),
            proximos_resultados = perfil['proximos_resultados']
        )
        print(perfil)

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

    # fields = ('empresa', 'tipo', 'acciones_cuenta')
    # readonly_fields = ('empresa', 'tipo', 'acciones_cuenta')


class EmpresaAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Información general',               
            {'fields': 
                [('nombre', 'symbol', 'isin'), ('pais', 'sector', 'tipo')
                ]},
        ),
        #('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    list_display = ('nombre', 'symbol', 'pub_date', 'status')
    list_filter = ['pub_date', 'sector', 'pais', 'tipo']
    actions = [desactiva_empresa, descarga_registros]
    inlines = [MovimientoInline]


class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'empresa', 'tipo', 'acciones', 'cambio_moneda', 'precio', 'coste_operacion', 'coste_total', )
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
    # actions = [desactiva_empresa, descarga_registros]
    inlines = [MovimientoInline]

    def clickable_site_domain(self, obj):
        return mark_safe(
            '<a href="%s">%s</a>' % (obj.nombre, obj.nombre)
        )



admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Cartera, CarteraAdmin)
admin.site.register(Movimiento, MovimientoAdmin)
admin.site.register(FundamentalesEmpresa)
