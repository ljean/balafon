# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Brand',
                'verbose_name_plural': 'Brands',
            },
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('logo', models.ImageField(default=b'', upload_to=b'certificates', blank=True)),
            ],
            options={
                'verbose_name': 'certificate',
                'verbose_name_plural': 'certificates',
            },
        ),
        migrations.CreateModel(
            name='DeliveryPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Delivery point',
                'verbose_name_plural': 'Delivery points',
            },
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('short_name', models.CharField(default=b'', max_length=100, verbose_name='short name', blank=True)),
                ('quantity', models.DecimalField(default=0, verbose_name='quantity', max_digits=9, decimal_places=2)),
                ('rate', models.DecimalField(default=0, verbose_name='rate', max_digits=4, decimal_places=2)),
                ('active', models.BooleanField(default=False, help_text='Only active discounts are taken into account on a new purchase', verbose_name='active')),
            ],
            options={
                'ordering': ['rate', 'name'],
                'verbose_name': 'Discount',
                'verbose_name_plural': 'Discounts',
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Favorite',
                'verbose_name_plural': 'Favorites',
            },
        ),
        migrations.CreateModel(
            name='PriceClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.CharField(default=b'', max_length=100, verbose_name='Description', blank=True)),
                ('discounts', models.ManyToManyField(to='Store.Discount', verbose_name='Discount', blank=True)),
            ],
            options={
                'verbose_name': 'Price class',
                'verbose_name_plural': 'Price classes',
            },
        ),
        migrations.CreateModel(
            name='PricePolicy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('parameters', models.CharField(default=b'', max_length=100, verbose_name='parameters', blank=True)),
                ('policy', models.CharField(max_length=100, verbose_name='policy', choices=[(b'from_category', 'Inherit from category'), (b'multiply_purchase_by_ratio', 'Multiply purchase price by ratio')])),
                ('apply_to', models.IntegerField(default=0, verbose_name='apply to', choices=[(0, 'All'), (1, 'Articles'), (2, 'Categories')])),
            ],
            options={
                'verbose_name': 'Price policy',
                'verbose_name_plural': 'Price policies',
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.OneToOneField(to='Crm.Action')),
                ('delivery_point', models.ForeignKey(default=None, blank=True, to='Store.DeliveryPoint', null=True, verbose_name='delivery point')),
            ],
            options={
                'verbose_name': 'Sale',
                'verbose_name_plural': 'Sales',
            },
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.DecimalField(verbose_name='quantity', max_digits=9, decimal_places=2)),
                ('pre_tax_price', models.DecimalField(verbose_name='pre-tax price', max_digits=9, decimal_places=2)),
                ('text', models.TextField(default=b'', max_length=3000, verbose_name='Text', blank=True)),
                ('order_index', models.IntegerField(default=0)),
                ('is_blank', models.BooleanField(default=False, help_text='displayed as an empty line', verbose_name='is blank')),
                ('discount', models.ForeignKey(default=None, blank=True, to='Store.Discount', null=True)),
            ],
            options={
                'ordering': ['order_index'],
                'verbose_name': 'Sale item',
                'verbose_name_plural': 'Sales items',
            },
        ),
        migrations.CreateModel(
            name='StoreItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('pre_tax_price', models.DecimalField(verbose_name='pre-tax price', max_digits=9, decimal_places=2)),
                ('stock_count', models.DecimalField(decimal_places=2, default=None, max_digits=9, blank=True, null=True, verbose_name='stock count')),
                ('stock_threshold', models.DecimalField(decimal_places=2, default=None, max_digits=9, blank=True, null=True, verbose_name='stock threshold')),
                ('purchase_price', models.DecimalField(decimal_places=2, default=None, max_digits=9, blank=True, null=True, verbose_name='purchase price')),
                ('reference', models.CharField(default=b'', max_length=100, verbose_name='reference', blank=True)),
                ('available', models.BooleanField(default=True, verbose_name='Available')),
                ('brand', models.ForeignKey(default=None, blank=True, to='Store.Brand', null=True, verbose_name='brand')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Store item',
                'verbose_name_plural': 'Store items',
            },
        ),
        migrations.CreateModel(
            name='StoreItemCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('order_index', models.IntegerField(default=0, verbose_name='order_index')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('icon', models.CharField(default=b'', max_length=20, blank=True)),
                ('parent', models.ForeignKey(related_name='subcategories_set', default=None, blank=True, to='Store.StoreItemCategory', null=True, verbose_name='parent category')),
                ('price_policy', models.ForeignKey(default=None, blank=True, to='Store.PricePolicy', null=True, verbose_name='price policy')),
            ],
            options={
                'ordering': ['order_index', 'name'],
                'verbose_name': 'Store item category',
                'verbose_name_plural': 'Store item categories',
            },
        ),
        migrations.CreateModel(
            name='StoreItemImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.FileField(help_text='An Excel file (*.xls) with the data', upload_to=b'store_item_imports', verbose_name='Import file')),
                ('fields', models.CharField(default=b'name,brand,reference,category,purchase_price,vat_rate', help_text="Fields to import in order: if the attribute doesn't exist, create a custom property", max_length=300, verbose_name='fields')),
                ('last_import_date', models.DateTimeField(default=None, null=True, verbose_name='last import', blank=True)),
                ('import_error', models.TextField(default=b'', verbose_name='import error', blank=True)),
                ('is_successful', models.BooleanField(default=True, verbose_name='is successful')),
                ('ignore_first_line', models.BooleanField(default=True, verbose_name='ignore first line')),
                ('margin_rate', models.DecimalField(default=None, null=True, verbose_name='margin_rate', max_digits=9, decimal_places=2)),
                ('error_message', models.CharField(default=b'', max_length=100, verbose_name='error message', blank=True)),
                ('category_lines_mode', models.BooleanField(default=False, help_text='If checked, the store item category are expected as merged-cells header lines', verbose_name='category-lines mode')),
                ('default_brand', models.CharField(default=b'', help_text='If defined, it will be used if no brand is given', max_length=50, verbose_name='default Brand', blank=True)),
                ('make_available', models.BooleanField(default=False, verbose_name='articles will be available if price is set')),
            ],
            options={
                'verbose_name': 'Store item import',
                'verbose_name_plural': 'Store item imports',
            },
        ),
        migrations.CreateModel(
            name='StoreItemProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('label', models.CharField(default=b'', max_length=100, verbose_name='label', blank=True)),
                ('in_fullname', models.BooleanField(default=False, help_text='is inserted in fullname if checked', verbose_name='in fullname')),
                ('is_public', models.BooleanField(default=False, help_text='returned in public API', verbose_name='is public')),
            ],
            options={
                'verbose_name': 'Store item: property value',
                'verbose_name_plural': 'Store item: properties',
            },
        ),
        migrations.CreateModel(
            name='StoreItemPropertyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(default=b'', max_length=100, verbose_name='value', blank=True)),
                ('item', models.ForeignKey(verbose_name='item', to='Store.StoreItem')),
                ('property', models.ForeignKey(verbose_name='property', to='Store.StoreItemProperty')),
            ],
            options={
                'verbose_name': 'Store item: property value',
                'verbose_name_plural': 'Store item: property values',
            },
        ),
        migrations.CreateModel(
            name='StoreItemTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('order_index', models.IntegerField(default=0, verbose_name='order_index')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('icon', models.CharField(default=b'', max_length=20, blank=True)),
                ('show_always', models.BooleanField(default=True, verbose_name='show always')),
            ],
            options={
                'ordering': ['order_index', 'name'],
                'verbose_name': 'Store item tag',
                'verbose_name_plural': 'Store item tags',
            },
        ),
        migrations.CreateModel(
            name='StoreManagementActionType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_name', models.CharField(default=b'', help_text='Set the name of a custom template for commercial document', max_length=100, verbose_name='template name', blank=True)),
                ('show_amount_as_pre_tax', models.BooleanField(default=True, help_text='The action amount will be update with pre-tax total if checked and with tax-included total if not', verbose_name='Show amount as pre-tax')),
                ('action_type', models.OneToOneField(to='Crm.ActionType')),
                ('readonly_status', models.ManyToManyField(help_text='When action has one of these status, it is not possible to modify a commercial document', to='Crm.ActionStatus', verbose_name='readonly status', blank=True)),
            ],
            options={
                'verbose_name': 'Store management action type',
                'verbose_name_plural': 'Store management action types',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Supplier',
                'verbose_name_plural': 'Suppliers',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
            ],
            options={
                'verbose_name': 'unit',
                'verbose_name_plural': 'units',
            },
        ),
        migrations.CreateModel(
            name='VatRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.DecimalField(verbose_name='vat rate', max_digits=4, decimal_places=2)),
                ('is_default', models.BooleanField(default=False, verbose_name='is default')),
            ],
            options={
                'ordering': ['rate'],
                'verbose_name': 'VAT rate',
                'verbose_name_plural': 'VAT rates',
            },
        ),
        migrations.AddField(
            model_name='storeitemimport',
            name='supplier',
            field=models.ForeignKey(default=None, blank=True, to='Store.Supplier', null=True, verbose_name='Supplier'),
        ),
        migrations.AddField(
            model_name='storeitemimport',
            name='tags',
            field=models.ManyToManyField(help_text='Tags that can be added to the items', to='Store.StoreItemTag', verbose_name='tags', blank=True),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='category',
            field=models.ForeignKey(verbose_name='category', to='Store.StoreItemCategory'),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='certificates',
            field=models.ManyToManyField(to='Store.Certificate', verbose_name='certificate', blank=True),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='imported_by',
            field=models.ForeignKey(default=None, blank=True, to='Store.StoreItemImport', null=True, verbose_name='imported by'),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='price_class',
            field=models.ForeignKey(default=None, blank=True, to='Store.PriceClass', null=True, verbose_name='price class'),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='price_policy',
            field=models.ForeignKey(default=None, blank=True, to='Store.PricePolicy', null=True, verbose_name='price policy'),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='supplier',
            field=models.ForeignKey(default=None, blank=True, to='Store.Supplier', null=True, verbose_name='Supplier'),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='tags',
            field=models.ManyToManyField(to='Store.StoreItemTag', verbose_name='tags', blank=True),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='unit',
            field=models.ForeignKey(default=None, blank=True, to='Store.Unit', null=True),
        ),
        migrations.AddField(
            model_name='storeitem',
            name='vat_rate',
            field=models.ForeignKey(verbose_name='VAT rate', to='Store.VatRate'),
        ),
        migrations.AddField(
            model_name='saleitem',
            name='item',
            field=models.ForeignKey(default=None, blank=True, to='Store.StoreItem', null=True),
        ),
        migrations.AddField(
            model_name='saleitem',
            name='sale',
            field=models.ForeignKey(to='Store.Sale'),
        ),
        migrations.AddField(
            model_name='saleitem',
            name='vat_rate',
            field=models.ForeignKey(default=None, blank=True, to='Store.VatRate', null=True, verbose_name='VAT rate'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='item',
            field=models.ForeignKey(verbose_name='store item', to='Store.StoreItem'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='discount',
            name='tags',
            field=models.ManyToManyField(to='Store.StoreItemTag', verbose_name='tags', blank=True),
        ),
    ]
