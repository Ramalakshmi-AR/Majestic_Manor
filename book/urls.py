from django.urls import path
from . import views

app_name = "book"
urlpatterns = [
    path("", views.home, name="home"),
    path('rooms/', views.room_list, name='room_list'),
    path('room/<int:pk>/', views.room_detail, name='room_detail'),
    path('room/<int:pk>/book/', views.book_room, name='book_room'),
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path("search/", views.search, name="search"),
]
