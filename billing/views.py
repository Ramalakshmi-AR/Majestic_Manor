from django.shortcuts import render
from book.models import Booking  # import your Booking model

def dashboard(request):
    bookings = Booking.objects.all().order_by('-id')

    # Calculate summary
    total_orders = bookings.count()
    total_revenue = sum(b.total_amount for b in bookings if b.status == "confirmed")
    pending_payments = bookings.filter(status="pending").count()

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_payments": pending_payments,
        "bookings": bookings,
    }
    return render(request, "billing/dashboard.html", context)
