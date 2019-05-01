from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from .models import Basket, Product, BasketProduct
from .forms import AddItemForm


def index(req):
    if 'basket_id' in req.session:
        basket_id = req.session['basket_id']
    else:
        basket_id = None
    context = {
        'basket_id' : basket_id
    }
    return render(req, 'checkout_app/index.html', context)


def create_basket(req):
    if 'basket_id' not in req.session:
        b = Basket.objects.create(user_audit_id=req.session.session_key)
        req.session['basket_id'] = b.basket_id
    basket_id = req.session['basket_id']    
    return redirect('basket_detail', basket_id=basket_id)


def basket_detail(req, basket_id):
    if 'basket_id' not in req.session:
        b = Basket.objects.create(user_audit_id=req.session.session_key)
        req.session['basket_id'] = b.basket_id
    basket_id = req.session['basket_id']
    b = get_object_or_404(Basket, pk=basket_id)
    price_no_disc, price_with_disc, diff = b.get_total()
    items = b.get_elems()
    context = {
        'basket': b,
        'items': items,
        'price_no_disc': price_no_disc,
        'price_with_disc': price_with_disc,
        'diff': diff
    }
    return render(req, 'checkout_app/basket_detail.html', context)


def products(req):
    if 'basket_id' not in req.session:
        b = Basket.objects.create(user_audit_id=req.session.session_key)
        req.session['basket_id'] = b.basket_id
    basket_id = req.session['basket_id']
    if req.method == "POST":
        form = AddItemForm(req.POST)
        if form.is_valid():
            product_code = form.data['product_code']
            quantity = form.data['quantity']
            return redirect('add_item', basket_id=basket_id,
                product_code=product_code, quantity=quantity)
    else:
        form = AddItemForm()
    context = {
        'form' : form,
        'basket_id' : basket_id
    }
    return render(req, 'checkout_app/products.html', context)


def add_item(req, basket_id, product_code, quantity):
    if 'basket_id' not in req.session:
        return render(req, 'checkout_app/basket_not_found.html', status=403)
    if quantity < 1:
        context = {'basket_id' : basket_id}
        return render(req, 'checkout_app/basket_bad_request.html', context, status=400)
    b = get_object_or_404(Basket, pk=basket_id)
    p = get_object_or_404(Product, pk=product_code)

    bp = BasketProduct.objects.create(product=p, basket=b, quantity=quantity, user_audit_id=req.session.session_key)

    return redirect('basket_detail', basket_id)


def remove_basket(req, basket_id):
    if 'basket_id' not in req.session:
        return render(req, 'checkout_app/basket_not_found.html', status=403)
    get_object_or_404(Basket, pk=basket_id).delete()
    del req.session['basket_id']
    return HttpResponse('Your basket has been successfully removed'.format(basket_id))
