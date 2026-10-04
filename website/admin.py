
from django.contrib import admin

from .models import (
    ContactMessage,
    Agent,
    Airline,
    Airport,
    Flight,
    Passenger,
    Booking,
    Hotel,
    UmrahPackage,
    UmrahBooking,
)


# =========================
# CONTACT MESSAGE
# =========================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "phone",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
    )

    ordering = (
        "-created_at",
    )


# =========================
# AGENT
# =========================

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "agency",
        "email",
        "phone",
        "created_at",
    )

    search_fields = (
        "name",
        "agency",
        "email",
        "phone",
    )

    ordering = (
        "-created_at",
    )


# =========================
# AIRLINE
# =========================

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "logo",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "is_active",
    )


# =========================
# AIRPORT
# =========================

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "city",
        "country",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "city",
        "country",
    )

    list_filter = (
        "country",
        "is_active",
    )


# =========================
# FLIGHT
# =========================

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):

    list_display = (
        "flight_number",
        "airline",
        "departure_airport",
        "arrival_airport",
        "category",
        "departure_date",
        "departure_time",
        "price",
        "available_seats",
        "is_active",
    )

    search_fields = (
        "flight_number",
        "airline__name",
        "airline__code",
        "departure_airport__code",
        "arrival_airport__code",
    )

    list_filter = (
        "airline",
        "category",
        "departure_date",
        "is_active",
    )

    ordering = (
        "departure_date",
        "departure_time",
    )


# =========================
# HOTEL
# =========================

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "location",
        "distance_from_reference",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "distance_from_reference",
        "description",
    )

    list_filter = (
        "location",
        "is_active",
    )

    ordering = (
        "location",
        "name",
    )


# =========================
# UMRAH PACKAGE
# =========================

# =========================
# UMRAH PACKAGE
# =========================

@admin.register(UmrahPackage)
class UmrahPackageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "sector",
        "airline",
        "outbound_flight_number",
        "return_flight_number",
        "makkah_hotel",
        "madinah_hotel",
        "room_type",
        "price",
        "total_seats",
        "available_seats",
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "sector",
        "airline__name",
        "airline__code",
        "outbound_flight_number",
        "return_flight_number",
        "makkah_hotel__name",
        "madinah_hotel__name",
    )

    list_filter = (
        "sector",
        "airline",
        "room_type",
        "status",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "airline",
        "outbound_departure_airport",
        "outbound_arrival_airport",
        "return_departure_airport",
        "return_arrival_airport",
        "makkah_hotel",
        "madinah_hotel",
    )


# =========================
# PASSENGER
# =========================

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "passport_number",
        "nationality",
        "phone",
        "email",
    )

    search_fields = (
        "first_name",
        "last_name",
        "passport_number",
        "phone",
        "email",
    )


# =========================
# BOOKING
# =========================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "booking_reference",
        "agent",
        "flight",
        "passenger",
        "seats_booked",
        "total_price",
        "status",
        "booked_at",
    )

    search_fields = (
        "booking_reference",
        "agent__name",
        "agent__agency",
        "passenger__first_name",
        "passenger__last_name",
        "passenger__passport_number",
    )

    list_filter = (
        "status",
        "booked_at",
    )

    ordering = (
        "-booked_at",
    )


# =========================
# UMRAH BOOKING
# =========================

@admin.register(UmrahBooking)
class UmrahBookingAdmin(admin.ModelAdmin):

    list_display = (
        "booking_reference",
        "agent",
        "package",
        "lead_passenger",
        "pilgrims_count",
        "total_price",
        "status",
        "booked_at",
    )

    search_fields = (
        "booking_reference",
        "agent__name",
        "agent__agency",
        "lead_passenger__first_name",
        "lead_passenger__last_name",
        "lead_passenger__passport_number",
        "package__name",
        "package__sector",
    )

    list_filter = (
        "status",
        "booked_at",
    )

    ordering = (
        "-booked_at",
    )

    filter_horizontal = (
        "pilgrims",
    )

    list_select_related = (
        "agent",
        "package",
        "lead_passenger",
    )
