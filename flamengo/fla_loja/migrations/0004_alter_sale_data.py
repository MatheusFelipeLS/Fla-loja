# Generated by Django 5.1 on 2024-08-25 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fla_loja', '0003_sale_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='data',
            field=models.DateField(verbose_name='Date purchased'),
        ),
    ]