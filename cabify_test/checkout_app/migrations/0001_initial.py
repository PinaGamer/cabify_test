# Generated by Django 2.2 on 2019-05-01 22:02

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('created_audit_date', models.DateTimeField(auto_now_add=True)),
                ('updated_audit_date', models.DateTimeField(auto_now=True)),
                ('user_audit_id', models.CharField(default='ADMIN', max_length=32)),
                ('basket_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 't_basket',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('created_audit_date', models.DateTimeField(auto_now_add=True)),
                ('updated_audit_date', models.DateTimeField(auto_now=True)),
                ('user_audit_id', models.CharField(default='ADMIN', max_length=32)),
                ('product_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=100, unique=True)),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0, "A product's price can't be negative")])),
            ],
            options={
                'db_table': 't_product',
            },
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('created_audit_date', models.DateTimeField(auto_now_add=True)),
                ('updated_audit_date', models.DateTimeField(auto_now=True)),
                ('user_audit_id', models.CharField(default='ADMIN', max_length=32)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='checkout_app.Product')),
            ],
            options={
                'db_table': 't_discount',
            },
        ),
        migrations.CreateModel(
            name='BasketProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_audit_date', models.DateTimeField(auto_now_add=True)),
                ('updated_audit_date', models.DateTimeField(auto_now=True)),
                ('user_audit_id', models.CharField(default='ADMIN', max_length=32)),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'At least it needs to be placed one item of a product into the basket')])),
                ('basket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkout_app.Basket')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkout_app.Product')),
            ],
            options={
                'db_table': 't_basket_products',
            },
        ),
        migrations.AddField(
            model_name='basket',
            name='products',
            field=models.ManyToManyField(through='checkout_app.BasketProduct', to='checkout_app.Product'),
        ),
        migrations.CreateModel(
            name='BulkPurchaseDiscount',
            fields=[
                ('discount_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='checkout_app.Discount')),
                ('min_items', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'At least the client needs to buy 1 item to apply the discount')])),
                ('discount', models.FloatField(validators=[django.core.validators.MinValueValidator(0.01, 'The discount needs to be higher than 0')])),
            ],
            options={
                'db_table': 't_bulk_purchase_discount',
            },
            bases=('checkout_app.discount',),
        ),
        migrations.CreateModel(
            name='FreePromoDiscount',
            fields=[
                ('discount_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='checkout_app.Discount')),
                ('items_to_buy', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'At least the client needs to buy 1 item to apply the discount')])),
                ('items_to_pay', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'At least the client needs to buy 1 item to apply the discount')])),
            ],
            options={
                'db_table': 't_free_promo_discount',
            },
            bases=('checkout_app.discount',),
        ),
    ]
