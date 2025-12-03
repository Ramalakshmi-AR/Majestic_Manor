from django.contrib import admin
from .models import Room, Customer, Booking
from .models import HomePage

admin.site.register(HomePage)

admin.site.register(Room)
admin.site.register(Customer)
admin.site.register(Booking)
