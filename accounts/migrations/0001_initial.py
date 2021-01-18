# Generated by Django 3.1.4 on 2021-01-03 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountEntityType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_type', models.CharField(choices=[('BN', 'Banco nacional'), ('BE', 'Banco extranjero'), ('WE', 'Waller electronico')], max_length=8, verbose_name='Tipo de entidad')),
            ],
        ),
        migrations.CreateModel(
            name='AccountEntityFinancial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_name', models.CharField(max_length=56, verbose_name='Nombre de la entidad')),
                ('entity_name_abbr', models.CharField(max_length=8, null=True, verbose_name='Nombre corto')),
                ('entity_prefix_account', models.CharField(default=None, max_length=10, null=True, verbose_name='Prefijo de cuenta')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='type_of_entity', to='accounts.accountentitytype')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_code', models.CharField(max_length=100, verbose_name='Número/Codigo de cuenta')),
                ('account_type', models.CharField(choices=[('C', 'Corriente'), ('A', 'Ahorro'), ('D', 'Divisas')], max_length=3, verbose_name='Tipo de cuenta')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='account_entity', to='accounts.accountentityfinancial')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='account',
            index=models.Index(fields=['account_code', 'account_type'], name='accounts_ac_account_939c62_idx'),
        ),
    ]
