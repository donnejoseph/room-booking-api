# Generated by Django 5.2 on 2025-04-22 23:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('capacity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('floor', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Meeting Room',
                'verbose_name_plural': 'Meeting Rooms',
                'ordering': ['floor', 'name'],
                'indexes': [models.Index(fields=['floor'], name='rooms_room_floor_e5a342_idx'), models.Index(fields=['capacity'], name='rooms_room_capacit_a254a2_idx')],
            },
        ),
    ]
