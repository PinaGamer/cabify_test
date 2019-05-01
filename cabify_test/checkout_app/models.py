from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import math

NEGATIVE_PRODUCT_PRICE_VLD = "A product's price can't be negative"
STUPID_OFFER_VLD = "It makes no sense this offer! `items_to_buy` > `items_to_pay` "
NON_ZERO_MSG_VLD = "At least the client needs to buy 1 item to apply the discount"
BULKPURCHASE_MSG_VLD = "The discount needs to be higher than 0"
MIN_VALUE_BASKET_VLD = "At least it needs to be placed one item of a product into the basket"
BULKPURCHASE_MAX_PRICE_VLD = "The discount to apply can't be higher than the product's price ('{}' item cost {}$)"


class BaseModel(models.Model):
    """
        This class will be the base for another models into the database.
        It includes audit fields that every table must have
    """
    created_audit_date = models.DateTimeField(auto_now_add=True)
    updated_audit_date = models.DateTimeField(auto_now=True)
    user_audit_id = models.CharField(max_length=32, default="ADMIN")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
            Due to SQLite overtolerance, before save the model into database
            `full_clean` method will check that data is valid (i.e. field's length)
        """
        self.full_clean()
        super(BaseModel, self).save(*args, **kwargs)


class Product(BaseModel):
    product_code = models.CharField(primary_key=True, max_length=20)
    product_name = models.CharField(unique=True, max_length=100)
    price = models.FloatField(validators=[
        MinValueValidator(0.00, NEGATIVE_PRODUCT_PRICE_VLD)
    ])

    class Meta():
        db_table = "t_product"

    def __str__(self):
        return self.product_code


class Basket(BaseModel):
    basket_id = models.AutoField(primary_key=True)
    products = models.ManyToManyField(Product, through="BasketProduct")

    def get_grouped_items(self):
        return BasketProduct.objects.filter(basket=self.basket_id).values(
            'basket_id', 'product_id', price=F('product__price')
        ).annotate(total_items=Sum('quantity'))

    def get_total_amount_without_discount(self):
        total = 0
        for p in BasketProduct.objects.filter(basket=self.basket_id):
            total += p.quantity * p.product.price
        return total

    def get_total_amount_with_discount(self):
        total = 0
        items = self.get_grouped_items()

        for it in items:
            prd = it['product_id']
            free_promo_disc = FreePromoDiscount.objects.filter(
                product=prd, items_to_buy__lte=it['total_items']).first()
            bulk_purch_disc = BulkPurchaseDiscount.objects.filter(
                product=prd, min_items__lte=it['total_items']).first()

            if free_promo_disc is not None:
                apply_promo_to = math.floor(
                    it['total_items'] / free_promo_disc.items_to_buy)
                not_promo = math.floor(
                    it['total_items'] % free_promo_disc.items_to_buy)
                total += apply_promo_to * free_promo_disc.items_to_pay * \
                    it['price'] + not_promo * it['price']
            elif bulk_purch_disc is not None:
                final_price = it['price'] - bulk_purch_disc.discount
                total += it['total_items'] * final_price
            else:
                total += it['total_items'] * it['price']
        return total

    def get_total(self):
        without_disc = self.get_total_amount_without_discount()
        with_disc = self.get_total_amount_with_discount()

        if with_disc != without_disc:
            diff = without_disc - with_disc
        else:
            return (without_disc, None, None)
        return (without_disc, with_disc, diff)

    def get_elems(self):
        """
            Returns a string representation of the elements added to the cart
        """
        p_dict = {}

        for bp in BasketProduct.objects.filter(basket=self.basket_id):
            prd = bp.product
            if prd.product_code not in p_dict:
                p_dict[prd.product_code] = bp.quantity
            else:
                p_dict[prd.product_code] += bp.quantity
        return p_dict

    class Meta():
        db_table = "t_basket"

    def __str__(self):
        diff_products = self.products.count()
        num_items = '{} items'.format(
            diff_products) if diff_products != 0 else 'EMPTY'
        return '{} ({})'.format(self.basket_id, num_items)


class BasketProduct(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        validators=[MinValueValidator(1, MIN_VALUE_BASKET_VLD)]
    )

    def __str__(self):
        return '{} - {}({})'.format(self.basket.basket_id, self.product.product_code, self.quantity)

    class Meta():
        db_table = "t_basket_products"


class Discount(BaseModel):
    product = models.OneToOneField(
        Product, primary_key=True, on_delete=models.CASCADE)

    class Meta():
        db_table = "t_discount"


class FreePromoDiscount(Discount):
    """
        This table holds every promo based on "buy y for the price of x" method
        (y needs to be strictly higher than x)
    """
    items_to_buy = models.PositiveIntegerField(validators=[
        MinValueValidator(1, NON_ZERO_MSG_VLD)])
    items_to_pay = models.PositiveIntegerField(validators=[
        MinValueValidator(1, NON_ZERO_MSG_VLD)])

    def clean(self):
        if self.items_to_pay > self.items_to_buy - 1:
            raise ValidationError({
                'items_to_pay': STUPID_OFFER_VLD.format(self.items_to_pay, self.items_to_buy),
                'items_to_buy': STUPID_OFFER_VLD.format(self.items_to_pay, self.items_to_buy)
            })

    def __str__(self):
        return '{} ({}x{})'.format(self.product.product_code, self.items_to_buy, self.items_to_pay)

    class Meta():
        db_table = "t_free_promo_discount"


class BulkPurchaseDiscount(Discount):
    """
        This table holds every discount based on buy a minimum quantity
        of a product in order to apply a discount
    """
    min_items = models.PositiveIntegerField(validators=[
        MinValueValidator(1, NON_ZERO_MSG_VLD)])
    discount = models.FloatField(validators=[
        MinValueValidator(0.01, BULKPURCHASE_MSG_VLD)
    ])

    def clean(self):
        if self.discount > self.product.price:
            raise ValidationError({
                'discount': BULKPURCHASE_MAX_PRICE_VLD.format(
                    self.product.product_code, self.product.price)
            })

    def __str__(self):
        return '{} ({} items - {}$)'.format(self.product.product_code, self.min_items, self.discount)

    class Meta():
        db_table = "t_bulk_purchase_discount"
