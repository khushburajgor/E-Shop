from django.db import models
import datetime


class Payment(models.Model):
    card_number = models.CharField(max_length=12, null=False,blank=False)
    balance = models.FloatField()
    name = models.CharField(max_length=30,null=False,blank=False)
    cvv = models.IntegerField(null=False)
    month = models.IntegerField()
    year = models.IntegerField()