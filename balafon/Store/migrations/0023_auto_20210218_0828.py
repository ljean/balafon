# Generated by Django 2.2.18 on 2021-02-18 08:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0022_auto_20201201_1525'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('code', models.CharField(max_length=100, verbose_name='code')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'Payment mode',
                'verbose_name_plural': 'Payment modes',
            },
        ),
        migrations.AddField(
            model_name='sale',
            name='payment_mode',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Store.PaymentMode', verbose_name='payment mode'),
        ),
    ]