# Generated by Django 4.0 on 2022-04-19 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('micartera', '0007_historicoempresa_capitalexpenditures_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QHistoricoEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiscalDateEnding', models.CharField(max_length=20)),
                ('reportedEPS', models.FloatField(default=0)),
                ('estimatedEPS', models.FloatField(default=0)),
                ('historico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='micartera.historicoempresa')),
            ],
        ),
    ]
