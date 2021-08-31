import razorpay as razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect

from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from store.models.customer import Customer
from django.views import View

from store.models.product import Product
from store.models.orders import Order

from store.models.payment import Payment
import datetime


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))
        print(address, phone, customer, cart, products)

        amount = 0
        for product in products:
            quantity = int(cart.get(str(product.id)))
            amount += product.price * quantity *100
        if(Customer.objects.filter(id=customer).exists() == False):
            return redirect('/login')
        else:
            customer_obj = Customer.objects.get(id=customer)
        currency = 'INR'

        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           ))

        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = '/purchased/' + str(address) + '/' + str(phone)

        # we need to pass these details to frontend.
        context = {}
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url
        context['prefill'] = {'contact' : phone, 'email': customer_obj.email}
        context['products'] = products
        return render(request, 'cart.html', context)


class product_purchase(View):

    def post(self,request,pk):
        product=Product.objects.get(pk=pk)
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        quantity= int(request.POST.get('Quantity'))
        # cardnumber = request.POST.get('card')
        # cardnumber = Payment.objects.filter(card_number=cardnumber).first()
        # print(request.POST.get('Date'))
        # month=int(request.POST.get('Date').split('-')[1])
        # year = int(request.POST.get('Date').split('-')[0])
        # print(month)
        # print(year)
        # print(type(request.POST.get('Date')))
        if(Customer.objects.filter(id=customer).exists() == False):
            return redirect('/login')
        else:
            customer_obj = Customer.objects.get(id=customer)
        currency = 'INR'
        amount = product.price * quantity * 100

        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           ))

        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = '/purchased/' + str(address) + '/' + str(phone) +'/'+ str(product.id) + '/' + str(quantity)

        # we need to pass these details to frontend.
        context = {}
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url
        context['prefill'] = {'contact': phone, 'email': customer_obj.email}
        context['prop'] = product
        return render(request, 'index.html', context)

@csrf_exempt
def purchased(request, address, phone, pid=None, q=None):
    if request.method == 'POST':
        if 'razorpay_payment_id' in request.POST:
            # get the required parameters from post request.
            payment_id = request.POST['razorpay_payment_id']
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            amount = razorpay_client.order.fetch(razorpay_order_id)['amount']
            # print(amount)# Rs. 200
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is None:
                try:

                    # capture the payemt
                    # capturing is not needed as we have turned on auto capture
                    # razorpay_client.payment.capture(payment_id, amount)
                    if pid is None:
                        customer = Customer.objects.get(id=request.session.get('customer'))
                        cart = request.session.get('cart')
                        products = Product.get_products_by_id(list(cart.keys()))
                        for product in products:
                            quantity = int(cart.get(str(product.id)))
                            order = Order(customer=customer,
                                          product=product,
                                          price=product.price,
                                          address=address,
                                          phone=phone,
                                          quantity=quantity, payment=razorpay_order_id)
                            order.save()

                        return redirect(f'/payment_success/'+str(razorpay_order_id)+'/1')
                    else:
                        product = Product.objects.get(id=pid)
                        order = Order(customer=Customer.objects.get(id = request.session.get('customer')),
                                      product=product,
                                      price=product.price,
                                      address=address,
                                      phone=phone,
                                      quantity=q, payment=razorpay_order_id)
                        order.save()

                        # render success page on successful capture of payment
                        return redirect(f'/payment_success/'+str(order.id))
                except Exception as e:
                    print(e)
                    # if there is an error while capturing payment.
                    return redirect(f'/')
            else:
                print('here2')
                # if signature verification fails.
                return redirect(f'/')
        else:
            # There is an error
            error = request.POST.get('error')
            print(error)
        return redirect(f'/')
    else:
        return HttpResponseBadRequest()


def payment_success(request, pk=None, flag = None):

    if flag is not None:
        cart = request.session['cart']

        products = Product.get_products_by_id(list(cart.keys()))
        p = []
        for product in products:
            quantity = int(cart.get(str(product.id)))
            p.append( {'product': product, 'quantity': quantity} )

        request.session['cart'] = {}
        return render(request, 'payment_success.html', {'item_list': p, 'order_id':  pk })

    order = Order.objects.get(id=pk)
    if order.customer.id != request.session.get('customer'):
        return redirect('/login')
    return render(request, 'payment_success.html', {'order': order})
