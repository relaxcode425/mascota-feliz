# Generated by Django 5.2 on 2025-06-16 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_fichamedica_rename_creada_en_reserva_fecha_creacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mascota',
            name='sexo',
            field=models.CharField(choices=[('macho', 'Macho'), ('hembra', 'Hembra')], default='macho', max_length=10),
        ),
    ]
