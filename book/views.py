import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Room, Booking, Customer, HomePage
from decimal import Decimal
from razorpay.errors import BadRequestError, SignatureVerificationError


# -----------------------------------------------------------
# Razorpay Client Helper
# -----------------------------------------------------------
def get_razorpay_client():
    return razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))


# -----------------------------------------------------------
# Home Page
# -----------------------------------------------------------
def home(request):
    homepage = HomePage.objects.first()
    return render(request, "book/home.html", {"homepage": homepage})


# -----------------------------------------------------------
# Room List and Details
# -----------------------------------------------------------
def room_list(request):
    rooms = Room.objects.filter(available=True)
    return render(request, "book/room_list.html", {"rooms": rooms})


def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, "book/room_detail.html", {"room": room})


# -----------------------------------------------------------
# Book Room (Creates Razorpay Order)
# -----------------------------------------------------------
def book_room(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == "POST":
        # Customer Details
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        # Create/Get Customer
        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone
            },
        )

        # Convert price to paise
        total_amount = float(room.price_per_night)
        amount_paise = int(total_amount * 100)

        # Create Razorpay Order
        client = get_razorpay_client()
        try:
            razorpay_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1
            })
        except BadRequestError:
            return render(request, "book/error.html", {
                "message": "Payment authentication failed. Check Razorpay keys."
            })
        except Exception as e:
            return render(request, "book/error.html", {
                "message": f"Error creating Razorpay order: {e}"
            })

        # Save Booking
        booking = Booking.objects.create(
            room=room,
            customer=customer,
            check_in=check_in,
            check_out=check_out,
            total_amount=Decimal(total_amount),
            razorpay_order_id=razorpay_order["id"],
            status="pending",
        )

        # Render Payment Page
        return render(request, "book/payment.html", {
            "booking": booking,
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "amount": amount_paise,
            "currency": "INR",
            "room": room,
        })

    return render(request, "book/book_room.html", {"room": room})


# -----------------------------------------------------------
# Checkout Page (Optional Step)
# -----------------------------------------------------------
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, "book/checkout.html", {
        "booking": booking,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount_paise": int(booking.total_amount * 100),
        "order_id": booking.razorpay_order_id,
    })


# -----------------------------------------------------------
# Payment Success Callback (Razorpay POST)
# -----------------------------------------------------------
@csrf_exempt
def payment_success(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method.")

    data = request.POST
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")

    # Fetch related Booking
    try:
        booking = Booking.objects.get(razorpay_order_id=razorpay_order_id)
    except Booking.DoesNotExist:
        return HttpResponseBadRequest("Booking not found.")

    client = get_razorpay_client()

    params = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    # Verify Razorpay Signature
    try:
        client.utility.verify_payment_signature(params)
        booking.status = "confirmed"
    except SignatureVerificationError:
        booking.status = "failed"
        booking.save()
        return render(request, "book/error.html", {
            "message": "Payment verification failed. Please contact support."
        })
    except Exception as e:
        booking.status = "failed"
        booking.save()
        return render(request, "book/error.html", {
            "message": f"Payment verification error: {e}"
        })

    # Save payment info
    booking.razorpay_payment_id = razorpay_payment_id
    booking.razorpay_signature = razorpay_signature
    booking.save()

    return render(request, "book/payment_success.html", {"booking": booking})
