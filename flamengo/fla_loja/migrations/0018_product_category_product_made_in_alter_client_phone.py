# Generated by Django 5.1 on 2024-10-17 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fla_loja', '0017_rename_sale_purchasescompleted_purchasesnotcompleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='product',
            name='made_in',
            field=models.CharField(default='', max_length=90),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=models.CharField(default='', max_length=16),
        ),
    ]
