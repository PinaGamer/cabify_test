from django.urls import path

from . import views

urlpatterns = [
	path('',
		 views.index, name='index'),
    path('basket/',
         views.create_basket, name='create_basket'),
    path('basket/<int:basket_id>/',
         views.basket_detail, name='basket_detail'),
    path('basket/<int:basket_id>/<str:product_code>/<int:quantity>',
         views.add_item, name='add_item'),
    path('products/',
         views.products, name='products'),
    path('basket/<int:basket_id>/remove/',
         views.remove_basket, name='remove_basket')
]
