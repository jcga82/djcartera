# Generated by Django 3.2.10 on 2022-04-21 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('micartera', '0012_qhistoricoempresa_estimatedtotalrevenue'),
    ]

    operations = [
        migrations.AddField(
            model_name='qhistoricoempresa',
            name='TextField',
            field=models.TextField(default='', max_length=255),
        ),
    ]
