# Generated by Django 4.0 on 2022-04-05 11:56

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cartera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('capital_inicial', models.DecimalField(decimal_places=4, default=0, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='Cripto',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=80)),
                ('symbol', models.CharField(max_length=10)),
                ('precio', models.FloatField(default=0)),
                ('marketcap', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('symbol', models.CharField(max_length=10)),
                ('logo', models.CharField(default='', max_length=50)),
                ('isin', models.CharField(default='', max_length=20)),
                ('description', models.TextField(max_length=500)),
                ('estrategia', models.CharField(choices=[('Dividendos', 'Dividendos'), ('Trading', 'Trading'), ('Grow', 'Grow'), ('Largo', 'Largo Plazo'), ('Viviendas', 'Viviendas')], default='Largo', max_length=15)),
                ('sector', models.CharField(choices=[('auto', 'Automoción'), ('salud', 'Salud'), ('elect', 'Energía'), ('tecno', 'Tecnología'), ('bienes', 'Bienes de consumo'), ('otros', 'Otros')], default='otros', max_length=10)),
                ('pais', models.CharField(choices=[('spain', 'España'), ('eeuu', 'EEUU'), ('others', 'Otros')], default='spain', max_length=20)),
                ('tipo', models.CharField(choices=[('a', 'Acción'), ('etf', 'ETF'), ('otros', 'Otros')], default='a', max_length=10)),
                ('dividendo_desde', models.CharField(default='0000', max_length=4)),
                ('fechas_dividendo', models.CharField(choices=[('14710', '1-4-7-10'), ('25811', '2-5-8-11'), ('36912', '3-6-9-12'), ('612', '6-12')], default='14710', max_length=10)),
                ('cagr3', models.FloatField(default=0)),
                ('cagr5', models.FloatField(default=0)),
                ('pub_date', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='fecha alta')),
            ],
        ),
        migrations.CreateModel(
            name='Vivienda',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(choices=[('Dividendos', 'Dividendos'), ('Trading', 'Trading'), ('Grow', 'Grow'), ('Largo', 'Largo Plazo'), ('Viviendas', 'Viviendas')], default='Viviendas', max_length=15)),
                ('direccion', models.CharField(max_length=80)),
                ('comunidad', models.CharField(choices=[('andalucia', 'Andalucía'), ('madrid', 'Madrid')], default='andalucia', max_length=20)),
                ('valor_cv', models.IntegerField(default=0)),
                ('gastos_cv', models.IntegerField(default=0)),
                ('gastos_reforma', models.IntegerField(default=0)),
                ('ingresos_mensuales', models.IntegerField(default=0)),
                ('gastos_ibi', models.IntegerField(default=0)),
                ('gastos_seguros', models.IntegerField(default=0)),
                ('gastos_comunidad', models.IntegerField(default=0)),
                ('financiacion', models.BooleanField(default=False)),
                ('pct_finan', models.FloatField(default=70)),
                ('plazo', models.IntegerField(default=20)),
                ('interes', models.FloatField(default=1.0)),
                ('cartera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='micartera.cartera')),
            ],
        ),
        migrations.CreateModel(
            name='RentaPasiva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('Dividendos', 'Dividendos'), ('Trading', 'Trading'), ('Grow', 'Grow'), ('Largo', 'Largo Plazo'), ('Viviendas', 'Viviendas')], default='Dividendos', max_length=15)),
                ('fecha_cobro', models.DateField()),
                ('cantidad', models.FloatField(default=0)),
                ('cartera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='micartera.cartera')),
            ],
        ),
        migrations.CreateModel(
            name='Movimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('c', 'Compra'), ('v', 'Venta')], default='c', max_length=1)),
                ('acciones', models.IntegerField(default=0)),
                ('precio', models.DecimalField(decimal_places=4, default=0, max_digits=20)),
                ('cambio_moneda', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('fecha', models.DateTimeField(blank=True, default=datetime.datetime.now, null=True)),
                ('cartera', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='micartera.cartera')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='micartera.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricoEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiscalDateEnding', models.CharField(max_length=20)),
                ('reportedEPS', models.FloatField(default=0)),
                ('dividendPayout', models.FloatField(default=0)),
                ('commonStockSharesOutstanding', models.FloatField(default=0)),
                ('netIncome', models.IntegerField(default=0)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='micartera.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='FundamentalesEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiscalDateEnding', models.CharField(max_length=20)),
                ('num_acciones', models.IntegerField(default=0)),
                ('markercap', models.FloatField(default=0, verbose_name='MCap (mill$)')),
                ('ebitda', models.FloatField(default=0)),
                ('per', models.FloatField(default=0, verbose_name='PER')),
                ('beta', models.FloatField(default=0)),
                ('bpa', models.FloatField(default=0, verbose_name='BPA')),
                ('dpa', models.FloatField(default=0, verbose_name='DPA')),
                ('dya', models.FloatField(default=0, verbose_name='Div(%)')),
                ('fechaDividendo', models.CharField(max_length=50, verbose_name='Fecha Div')),
                ('fechaDividendoEx', models.CharField(max_length=50, verbose_name='Fecha ExDiv')),
                ('WeekHighYear', models.FloatField(default=0, verbose_name='Max')),
                ('WeekLowYear', models.FloatField(default=0, verbose_name='Min')),
                ('DayMovingAverage50', models.FloatField(default=0, verbose_name='MMA50')),
                ('DayMovingAverage200', models.FloatField(default=0, verbose_name='MMA200')),
                ('pub_date', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='Publicado el')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='micartera.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='DividendoEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=40)),
                ('dividendo', models.FloatField(default=0)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='micartera.empresa')),
            ],
        ),
    ]
