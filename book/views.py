import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Room, Booking, Customer, HomePage
from .forms import BookingForm, CustomerForm
from django.contrib.auth.decorators import login_required


# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# Home page
def home(request):
    homepage = HomePage.objects.first()  # Fetch the homepage content
    return render(request, "book/home.html", {"homepage": homepage})



def room_list(request):
    rooms = Room.objects.all()  # fetch all rooms
    return render(request, "book/room_list.html", {"rooms": rooms})
# List available rooms
# def room_list(request):
#     rooms = Room.objects.filter(available=True)
#     return render(request, 'book/room_list.html', {'rooms': rooms})


# Room details page
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'book/room_detail.html', {'room': room})


# Book room
def book_room(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == "POST":
        # Get customer info
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        # --- FIXED CUSTOMER HANDLING ---
        customer = Customer.objects.filter(email=email).first()

        if not customer:
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone
            )

        # Amount calculation
        total_amount = room.price_per_night
        amount_paise = int(total_amount * 100)

        # Create Razorpay order
        try:
            razorpay_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1
            })
        except razorpay.errors.BadRequestError:
            return render(request, "book/error.html", {"message": "Payment authentication failed."})
        except Exception as e:
            return render(request, "book/error.html", {"message": str(e)})

        # Save booking
        booking = Booking.objects.create(
            room=room,
            customer=customer,
            check_in=check_in,
            check_out=check_out,
            total_amount=total_amount,
            razorpay_order_id=razorpay_order['id'],
            status="pending"
        )

        return render(request, "book/payment.html", {
            "room": room,
            "booking": booking,
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "amount": amount_paise,
            "currency": "INR"
        })

    # GET request
    return render(request, "book/book_room.html", {"room": room})

# Checkout page (optional)
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'book/checkout.html', {
        "booking": booking,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount_paise": int(booking.total_amount * 100),
        "order_id": booking.razorpay_order_id,
    })


# Payment success callback
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST

        # Fetch booking by Razorpay order ID
        try:
            booking = Booking.objects.get(
                razorpay_order_id=data.get("razorpay_order_id")
            )
        except Booking.DoesNotExist:
            return HttpResponseBadRequest("Booking not found")

        params = {
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": data.get("razorpay_payment_id"),
            "razorpay_signature": data.get("razorpay_signature"),
        }

        razorpay_client = get_razorpay_client()

        try:
            # Verify payment signature
            razorpay_client.utility.verify_payment_signature(params)
            booking.status = "confirmed"
        except razorpay.errors.SignatureVerificationError:
            booking.status = "failed"

        # Save payment details
        booking.razorpay_payment_id = params.get("razorpay_payment_id")
        booking.razorpay_signature = params.get("razorpay_signature")
        booking.save()

        return render(request, "book/payment_success.html", {"booking": booking})

    return HttpResponseBadRequest("Invalid request")
