# Generated by Django 4.0 on 2022-04-11 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('micartera', '0002_historicoempresa_costofrevenue_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='sector',
            field=models.CharField(choices=[('ConsumoDef', 'Consumo Defensivo'), ('salud', 'Salud'), ('utilities', 'Serv. Públicos'), ('comunicaciones', 'Comunicaciones'), ('elect', 'Energía'), ('industrial', 'Industrial'), ('tecno', 'Tecnología'), ('materiales', 'Materiales'), ('consumoCic', 'Consumo Cíclico'), ('finanzas', 'Finanzas'), ('inmo', 'Inmobiliario'), ('otros', 'Otros')], default='otros', max_length=20),
        ),
    ]