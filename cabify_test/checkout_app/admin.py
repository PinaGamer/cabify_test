from django.contrib import admin

from .models import Product, FreePromoDiscount, BulkPurchaseDiscount, Basket

admin.site.register(Product)
admin.site.register(FreePromoDiscount)
admin.site.register(BulkPurchaseDiscount)
admin.site.register(Basket)