# Generated by Django 3.1.4 on 2021-01-19 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0003_bill_emit_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='bill_nulled_at',
            field=models.DateTimeField(null=True, verbose_name='Fecha de anulación'),
        ),
    ]
