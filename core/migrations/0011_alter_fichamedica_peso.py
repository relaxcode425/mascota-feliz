# Generated by Django 5.2 on 2025-06-17 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_fichamedica_edad_mascota_fecha_nacimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichamedica',
            name='peso',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
