# Generated by Django 4.0.3 on 2022-05-26 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('micartera', '0017_auto_20220506_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='comision',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='movimiento',
            name='moneda',
            field=models.CharField(choices=[('usd', 'USD'), ('eur', 'EUR'), ('gbx', 'GBX'), ('otra', 'Otra')], default='usd', max_length=10),
        ),
        migrations.AddField(
            model_name='movimiento',
            name='total_acciones',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='movimiento',
            name='tipo',
            field=models.CharField(choices=[('compra', 'Compra'), ('venta', 'Venta'), ('ingreso', 'Ingreso'), ('retirada', 'Retirada')], default='compra', max_length=10),
        ),
    ]
