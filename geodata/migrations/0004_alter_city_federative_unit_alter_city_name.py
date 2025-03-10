# Generated by Django 5.1.3 on 2025-01-22 15:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0003_remove_city_state_city_federative_unit_and_more'),
        ('symptoms', '0004_alter_symptoms_month_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='federative_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='symptoms.symptoms'),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
