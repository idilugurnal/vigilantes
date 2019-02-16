from django.contrib import admin

# Register your models here.
from models import Reservation, Room, Coupon, Payment, UserWrapper

admin.site.register(Reservation)
admin.site.register(Room)
admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(UserWrapper)
