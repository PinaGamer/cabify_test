from django.test import TestCase
from django.urls import reverse
from .models import Product, Discount, FreePromoDiscount, BulkPurchaseDiscount, Basket
from django.core.exceptions import ValidationError


class ProductModelTests(TestCase):

    def test_create_two_products_with_same_product_code(self):
        """
            It's not possible to create two products with the same product_code
        """
        p1 = Product(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        p1.save()

        p2 = Product(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        self.assertRaises(ValidationError, p2.save)


class DiscountModelTests(TestCase):

    def test_create_two_discounts_of_the_same_product(self):
        """
            It's not possible to create two discounts related to the same 
            product
        """
        p1 = Product(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        p1.save()

        d1 = Discount(product=p1)
        d1.save()

        d2 = Discount(product=p1)
        self.assertRaises(ValidationError, d2.save)

    def test_create_two_fp_discounts_of_the_same_product(self):
        """
            Same like `test_create_two_discounts_of_the_same_product` test but using 
            the FreePromoDiscount class. The result must be the same due to 
            FreePromoDiscount class inherits Discount class
        """
        p1 = Product(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        p1.save()

        d1 = FreePromoDiscount(product=p1, items_to_buy=3, items_to_pay=2)
        d1.save()

        d2 = FreePromoDiscount(product=p1, items_to_buy=3, items_to_pay=2)
        self.assertRaises(ValidationError, d2.save)

    def test_create_two_blk_prch_discounts_of_the_same_product(self):
        """
            Same like `test_create_two_discounts_of_the_same_product` test but using 
            the BulkPurchaseDiscount class. The result must be the same due to 
            BulkPurchaseDiscount class inherits Discount class
        """
        p1 = Product(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        p1.save()

        d1 = BulkPurchaseDiscount(product=p1, min_items=3, discount=2.00)
        d1.save()

        d2 = BulkPurchaseDiscount(product=p1, min_items=3, discount=2.00)
        self.assertRaises(ValidationError, d2.save)

    def test_create_two_different_discounts_of_the_same_product(self):
        """
            Same like `test_create_two_discounts_of_the_same_product` test but using 
            the BulkPurchaseDiscount and FreePromoDiscount classes. The result 
            must be the same due to both classes inherit Discount class
        """
        p1 = Product(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        p1.save()

        d1 = BulkPurchaseDiscount(product=p1, min_items=3, discount=2.00)
        d1.save()

        d2 = FreePromoDiscount(product=p1, items_to_buy=3, items_to_pay=2)
        self.assertRaises(ValidationError, d2.save)


class FreePromoDiscountModelTests(TestCase):

    def test_create_fpd_itb_gt_itp(self):
        """
            It's not possible to create a FreePromoDiscount
            when `items_to_pay` attribute is higher than `items_to_buy`
        """
        p1 = Product.objects.create(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        fpd1 = FreePromoDiscount(product=p1, items_to_buy=2, items_to_pay=3)
        self.assertRaises(ValidationError, fpd1.save)

    def test_create_fpd_itb_et_itp(self):
        """
            It's not possible to create a FreePromoDiscount
            when `items_to_pay` attribute is equal than `items_to_buy`
        """
        p1 = Product.objects.create(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        fpd1 = FreePromoDiscount(product=p1, items_to_buy=2, items_to_pay=2)
        self.assertRaises(ValidationError, fpd1.save)

    def test_create_fpd_items_less_than_one(self):
        """
            It's not possible to create a FreePromoDiscount
            when `items_to_pay` or `items_to_buy` are less than 1
        """
        p1 = Product.objects.create(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        fpd1 = FreePromoDiscount(product=p1, items_to_buy=0, items_to_pay=1)
        self.assertRaises(ValidationError, fpd1.save)

        fpd2 = FreePromoDiscount(product=p1, items_to_buy=1, items_to_pay=0)
        self.assertRaises(ValidationError, fpd2.save)


class BulkPurchaseDiscountModelTests(TestCase):

    def test_create_bp_discount_gt_price(self):
        """
            It's no makes sense to create a BulkDiscoun when `discount` 
            attribute is higher than the product's price
        """
        p1 = Product.objects.create(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        d1 = BulkPurchaseDiscount(product=p1, min_items=1, discount=12.00)
        self.assertRaises(ValidationError, d1.save)

    def test_create_bp_items_lt_one(self):
        """
            It's not possible to create a BulkPurchaseDiscount
            when `min_items` is less than 1
        """
        p1 = Product.objects.create(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        d1 = BulkPurchaseDiscount(product=p1, min_items=0, discount=12.00)
        self.assertRaises(ValidationError, d1.save)


class IndexViewTests(TestCase):

    def test_no_basket_created(self):
        """
            When a new client enters into the shop, `Go to your basket!` link
            does not appear
        """
        MSG = "Go to your basket"

        url = reverse('index')
        rsp = self.client.get(url)
        self.assertNotContains(rsp, MSG)


class AddItemViewTests(TestCase):

    def test_add_item_to_basket_forbidden(self):
        """
            When a new client enters into the shop, and tries to add 
            any item to any basket it receives a 403 response
        """
        b1 = Basket.objects.create()
        p1 = Product.objects.create(product_code='PRODUCT_TEST', product_name='Test product', price=10)
        quantity = 1

        url = reverse('add_item', args=(b1.pk, p1.product_code, quantity))
        rsp = self.client.get(url)
        self.assertEqual(rsp.status_code, 403)


class RemoveBasketViewTests(TestCase):

    def test_remove_basket_forbidden(self):
        """
            When a new client enters into the shop, and tries to add 
            any item to any basket it receives a 403 response
        """
        b1 = Basket.objects.create()
        url = reverse('remove_basket', args=(b1.pk,))
        rsp = self.client.get(url)
        self.assertEqual(rsp.status_code, 403)