# Generated by Django 5.1 on 2024-10-17 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fla_loja', '0019_rename_data_car_date_alter_car_id_employee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='sales_count',
            field=models.FloatField(default=0.0),
        ),
    ]
