# Generated by Django 5.1.3 on 2025-01-20 21:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('geodata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Burned',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('register_at', models.DateTimeField()),
                ('no_rain_days', models.IntegerField()),
                ('precipitation', models.FloatField()),
                ('fire_risk', models.FloatField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('frp', models.FloatField()),
                ('biome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geodata.biome')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geodata.city')),
                ('satellite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geodata.satellite')),
            ],
        ),
    ]
