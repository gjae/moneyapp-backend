# Generated by Django 3.1.4 on 2021-01-18 21:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movements', '0005_remove_movement_transaction_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movement',
            name='funding',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account_fund_movement', to='movements.accountfunds'),
        ),
    ]
