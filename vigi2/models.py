from __future__ import unicode_literals

import datetime
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Room(models.Model):
    price = models.IntegerField(default=0)
    type = models.CharField(max_length=10)
    empty = models.BooleanField(default=True)


class Coupon(models.Model):
    valid_from = models.DateField(default=datetime.date.today)
    valid_until = models.DateField(default=datetime.datetime(2019, 9, 12, 11, 19, 54).date())


class Payment(models.Model):
    card = models.IntegerField(default=0)
    cvc = models.IntegerField(default=0)
    valid_date = models.DateField(default=datetime.date.today)
    name = models.CharField(max_length=20)


class Reservation(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, null=True, on_delete=models.CASCADE)
    number = models.IntegerField(default=0)
    checkin = models.DateField(default=datetime.date.today)
    checkout = models.DateField(default=datetime.date.today)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, null=True, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)


class UserWrapper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    coupons = models.ManyToManyField(Coupon)
    phonenumber = models.CharField(max_length=20, null=True, blank=True, default="0")
    confirm = models.NullBooleanField(default=False)
    token = models.CharField(max_length=20, default="", null=True)