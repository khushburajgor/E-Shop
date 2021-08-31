from django.shortcuts import render , redirect

from django.contrib.auth.hashers import  check_password
from store.models.customer import Customer
from django.views import  View
from store.models.product import  Product

class Cart(View):
    def get(self , request,pk=None):
        if pk is not None:
            cart=request.session.get('cart')
            cart.pop(pk)
            request.session['cart']=cart
            print(request.session.get('cart'))
            return redirect('cart')
        request.session.get('cart')
        print(request.session.get('cart'))
        ids = list(request.session.get('cart').keys())
        products = Product.get_products_by_id(ids)
        print(products)
        return render(request , 'cart.html' , {'products' : products} )

