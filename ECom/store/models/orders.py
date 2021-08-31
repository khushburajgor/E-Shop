from django.db import models
from .product import Product
from .customer import Customer
from .payment import Payment
import datetime


class Order(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,
                                 on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(null=False)
    address = models.CharField(max_length=50, default='', blank=False,null=False)
    phone = models.CharField(max_length=50, default='', blank=False,null=False)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)
    payment = models.CharField(max_length= 255)

    def placeOrder(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')

