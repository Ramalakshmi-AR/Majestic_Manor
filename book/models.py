from django.db import models
from django.utils import timezone


class Room(models.Model):
    ROOM_TYPES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    )
    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    available = models.BooleanField(default=True)

    main_image = models.ImageField(upload_to='rooms/', null=True, blank=True)
   
    def __str__(self):
        return f"Room {self.number} ({self.get_room_type_display()})"


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Payment Failed'),
    )

    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Booking {self.pk} - {self.customer}"


class HomePage(models.Model):
    hero_title = models.CharField(max_length=200, default="Welcome to Majestic Manor")
    hero_subtitle = models.CharField(max_length=300, blank=True, null=True)
    hero_image = models.ImageField(upload_to="homepage/", blank=True, null=True)

    room1_title = models.CharField(max_length=100, blank=True, null=True)
    room1_image = models.ImageField(upload_to="homepage/", blank=True, null=True)

    room2_title = models.CharField(max_length=100, blank=True, null=True)
    room2_image = models.ImageField(upload_to="homepage/", blank=True, null=True)

    room3_title = models.CharField(max_length=100, blank=True, null=True)
    room3_image = models.ImageField(upload_to="homepage/", blank=True, null=True)

    def __str__(self):
        return "Home Page Content"
