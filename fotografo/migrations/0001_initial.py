# Generated by Django 5.1.2 on 2024-11-01 00:59

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fotografo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('senha', models.CharField(max_length=128)),
                ('fone', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ensaio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.TextField()),
                ('val_ensaio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('qtd_fotos', models.IntegerField()),
                ('pago', models.BooleanField(default=False)),
                ('data_criacao', models.DateTimeField(default=django.utils.timezone.now)),
                ('val_foto_extra', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('data_escolha', models.DateField(blank=True, null=True)),
                ('foto_capa', models.ImageField(blank=True, null=True, upload_to='capas_ensaios/')),
                ('total_fotos_escolhidas', models.IntegerField(default=0)),
                ('fotografo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ensaios', to='fotografo.fotografo')),
            ],
        ),
    ]