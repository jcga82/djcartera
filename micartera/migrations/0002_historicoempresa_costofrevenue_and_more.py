# Generated by Django 4.0 on 2022-04-07 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('micartera', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicoempresa',
            name='costOfRevenue',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicoempresa',
            name='dandp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicoempresa',
            name='ebitda',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicoempresa',
            name='interests',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicoempresa',
            name='tax',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicoempresa',
            name='totalRevenue',
            field=models.IntegerField(default=0),
        ),
    ]
