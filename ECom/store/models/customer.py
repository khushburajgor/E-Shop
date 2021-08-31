from django.db import  models
from django.core.validators import MinLengthValidator

class Customer(models.Model):
    first_name = models.CharField(max_length=50,null=False)
    last_name = models.CharField(max_length=50,null=False)
    phone = models.CharField(max_length=15,null=False)
    email = models.EmailField(max_length=150,null=False)
    password = models.CharField(max_length=500,null=False)

    def register(self):
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except:
            return False


    def isExists(self):
        if Customer.objects.filter(email = self.email):
            return True

        return  False


