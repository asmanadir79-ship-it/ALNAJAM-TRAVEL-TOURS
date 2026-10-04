from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction, models
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
import uuid
import random
import string
import json
from .models import (
    ContactMessage,
    Agent,
    Airline,
    Airport,
    Flight,
    Passenger,
    Booking,
    GroupTicket,
    GroupBooking,
    AgentWallet,
    TopUpRequest,
    WalletTransaction,
    Hotel,
    UmrahPackage,
    UmrahBooking,
)
from .forms import PassengerForm, GroupTicketForm
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib.units import mm
from io import BytesIO


# =====================================================
# HOME
# =====================================================

def home(request):
    return render(request, "home.html")


# =====================================================
# CONTACT
# =====================================================

def contact(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        messages.success(
            request,
            "Thank you! Your message has been sent successfully."
        )

        return redirect("contact")

    return render(request, "contact.html")


# =====================================================
# FLIGHTS
# =====================================================

def flights(request):
    return render(request, "flights.html")


# =====================================================
# HOTELS
# =====================================================

def hotels(request):
    return render(request, "hotels.html")


# =====================================================
# VISA
# =====================================================

def visa(request):
    return render(request, "visa.html")


# =====================================================
# UMRAH
# =====================================================

def umrah(request):
    return render(request, "umrah.html")


# =====================================================
# TOURS
# =====================================================

def tours(request):
    return render(request, "tours.html")


# =====================================================
# ABOUT
# =====================================================

def about(request):
    return render(request, "about.html")


# =====================================================
# LOGIN
# =====================================================

def login_view(request):

    if request.method == "POST":

        email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # -------------------------------------------------
        # FIND DJANGO USER USING EMAIL
        # -------------------------------------------------

        try:

            user_obj = User.objects.get(
                email__iexact=email
            )

        except User.DoesNotExist:

            user_obj = None

        # -------------------------------------------------
        # AUTHENTICATE USER
        # -------------------------------------------------

        if user_obj is not None:

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

        else:

            user = None

        # -------------------------------------------------
        # LOGIN SUCCESS
        # -------------------------------------------------

        if user is not None:

            # =================================================
            # ADMIN / SUPERUSER
            # =================================================

            if user.is_superuser:

                login(request, user)

                messages.success(
                    request,
                    "Welcome to AL NAJAM Admin Dashboard."
                )

                return redirect("admin_dashboard")

            # =================================================
            # AGENT
            # =================================================

            if hasattr(user, "agent_profile"):

                agent = user.agent_profile

                # -------------------------------------------------
                # APPROVED
                # -------------------------------------------------

                if agent.status == "APPROVED":

                    login(request, user)

                    messages.success(
                        request,
                        "Login successful! Welcome to AL NAJAM."
                    )

                    return redirect("agent_dashboard")

                # -------------------------------------------------
                # PENDING
                # -------------------------------------------------

                elif agent.status == "PENDING":

                    messages.warning(
                        request,
                        "Your agent account is waiting for admin approval."
                    )

                    return redirect("login")

                # -------------------------------------------------
                # REJECTED
                # -------------------------------------------------

                elif agent.status == "REJECTED":

                    messages.error(
                        request,
                        "Your agent application has been rejected."
                    )

                    return redirect("login")

                # -------------------------------------------------
                # SUSPENDED
                # -------------------------------------------------

                elif agent.status == "SUSPENDED":

                    messages.error(
                        request,
                        "Your agent account has been suspended."
                    )

                    return redirect("login")

            # -------------------------------------------------
            # NO PERMISSION
            # -------------------------------------------------

            messages.error(
                request,
                "This account does not have permission to access AL NAJAM."
            )

            return redirect("login")

        # =================================================
        # LOGIN FAILED
        # =================================================

        messages.error(
            request,
            "Invalid email address or password."
        )

    return render(
        request,
        "login.html"
    )


# =====================================================
# BECOME AN AGENT
# =====================================================

def become_agent(request):

    if request.method == "POST":

        name = request.POST.get("name")
        agency = request.POST.get("agency")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # -------------------------------------------------
        # CHECK PASSWORDS
        # -------------------------------------------------

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("become_agent")

        # -------------------------------------------------
        # CHECK USERNAME / EMAIL
        # -------------------------------------------------

        if User.objects.filter(
            username=email
        ).exists():

            messages.error(
                request,
                "An account with this email already exists."
            )

            return redirect("become_agent")

        # -------------------------------------------------
        # CHECK AGENT EMAIL
        # -------------------------------------------------

        if Agent.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "An agent account with this email already exists."
            )

            return redirect("become_agent")

        # -------------------------------------------------
        # CREATE DJANGO USER
        # -------------------------------------------------

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # -------------------------------------------------
        # CREATE AGENT PROFILE
        # -------------------------------------------------

        Agent.objects.create(
            user=user,
            name=name,
            agency=agency,
            email=email,
            phone=phone
        )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        messages.success(
            request,
            "Agent account created successfully! You can now login."
        )

        return redirect("login")

    return render(
        request,
        "become-agent.html"
    )


# =====================================================
# AGENT DASHBOARD
# =====================================================

# =====================================================
# AGENT DASHBOARD - DYNAMIC
# =====================================================

@login_required(login_url="login")
def agent_dashboard(request):

    # =================================================
    # GET LOGGED-IN AGENT
    # =================================================

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # CURRENT DATE
    # =================================================

    today = timezone.localdate()

    # =================================================
    # AGENT WALLET
    # =================================================

    wallet, created = AgentWallet.objects.get_or_create(
        agent=agent
    )

    wallet_balance = wallet.balance or 0

    # =================================================
    # NORMAL FLIGHT BOOKINGS
    # =================================================

    flight_bookings = Booking.objects.filter(
        agent=agent
    ).select_related(
        "flight",
        "flight__airline",
        "flight__departure_airport",
        "flight__arrival_airport",
        "passenger"
    )

    # =================================================
    # GROUP BOOKINGS
    # =================================================

    group_bookings = GroupBooking.objects.filter(
        agent=agent
    ).select_related(
        "group_ticket",
        "group_ticket__airline",
        "group_ticket__departure_airport",
        "group_ticket__arrival_airport",
        "passenger"
    )

    # =================================================
    # UMRAH BOOKINGS
    # =================================================

    umrah_bookings = UmrahBooking.objects.filter(
        agent=agent
    ).select_related(
        "package",
        "package__airline",
        "package__outbound_departure_airport",
        "package__outbound_arrival_airport",
        "package__return_departure_airport",
        "package__return_arrival_airport",
        "package__makkah_hotel",
        "package__madinah_hotel",
        "lead_passenger"
    )

    # =================================================
    # BASIC COUNTS
    # =================================================

    flight_total = flight_bookings.count()
    group_total = group_bookings.count()
    umrah_total = umrah_bookings.count()

    total_bookings = (
        flight_total
        + group_total
        + umrah_total
    )

    # =================================================
    # PENDING BOOKINGS
    # =================================================

    pending_flights = flight_bookings.filter(
        status="PENDING"
    ).count()

    pending_groups = group_bookings.filter(
        status="PENDING"
    ).count()

    pending_umrah = umrah_bookings.filter(
        status="PENDING"
    ).count()

    pending_requests = (
        pending_flights
        + pending_groups
        + pending_umrah
    )

    # =================================================
    # CONFIRMED BOOKINGS
    # =================================================

    confirmed_flights = flight_bookings.filter(
        status="CONFIRMED"
    ).count()

    confirmed_groups = group_bookings.filter(
        status="CONFIRMED"
    ).count()

    confirmed_umrah = umrah_bookings.filter(
        status="CONFIRMED"
    ).count()

    confirmed_bookings = (
        confirmed_flights
        + confirmed_groups
        + confirmed_umrah
    )

    # =================================================
    # CANCELLED / REJECTED
    # =================================================

    cancelled_flights = flight_bookings.filter(
        status="CANCELLED"
    ).count()

    rejected_groups = group_bookings.filter(
        status="REJECTED"
    ).count()

    rejected_umrah = umrah_bookings.filter(
        status="REJECTED"
    ).count()

    cancelled_bookings = (
        cancelled_flights
        + rejected_groups
        + rejected_umrah
    )

    # =================================================
    # TOTAL SALES
    # =================================================

    flight_sales = (
        flight_bookings
        .filter(status="CONFIRMED")
        .aggregate(
            total=models.Sum("total_price")
        )["total"] or 0
    )

    group_sales = (
        group_bookings
        .filter(status="CONFIRMED")
        .aggregate(
            total=models.Sum("total_price")
        )["total"] or 0
    )

    umrah_sales = (
        umrah_bookings
        .filter(status="CONFIRMED")
        .aggregate(
            total=models.Sum("total_price")
        )["total"] or 0
    )

    total_sales = (
        flight_sales
        + group_sales
        + umrah_sales
    )

    # =================================================
    # TODAY'S BOOKINGS
    # =================================================

    today_flights = flight_bookings.filter(
        booked_at__date=today
    )

    today_groups = group_bookings.filter(
        booked_at__date=today
    )

    today_umrah = umrah_bookings.filter(
        booked_at__date=today
    )

    bookings_today = (
        today_flights.count()
        + today_groups.count()
        + today_umrah.count()
    )

    # =================================================
    # TODAY'S CONFIRMED BOOKINGS
    # =================================================

    confirmed_today = (
        today_flights.filter(
            status="CONFIRMED"
        ).count()
        +
        today_groups.filter(
            status="CONFIRMED"
        ).count()
        +
        today_umrah.filter(
            status="CONFIRMED"
        ).count()
    )

    # =================================================
    # TODAY'S CANCELLED / REJECTED
    # =================================================

    cancelled_today = (
        today_flights.filter(
            status="CANCELLED"
        ).count()
        +
        today_groups.filter(
            status="REJECTED"
        ).count()
        +
        today_umrah.filter(
            status="REJECTED"
        ).count()
    )

    # =================================================
    # TODAY'S REVENUE
    # =================================================

    today_flight_revenue = (
        today_flights
        .filter(status="CONFIRMED")
        .aggregate(
            total=models.Sum("total_price")
        )["total"] or 0
    )

    today_group_revenue = (
        today_groups
        .filter(status="CONFIRMED")
        .aggregate(
            total=models.Sum("total_price")
        )["total"] or 0
    )

    today_umrah_revenue = (
        today_umrah
        .filter(status="CONFIRMED")
        .aggregate(
            total=models.Sum("total_price")
        )["total"] or 0
    )

    revenue_today = (
        today_flight_revenue
        + today_group_revenue
        + today_umrah_revenue
    )

    # =================================================
    # RECENT BOOKINGS
    # =================================================

    recent_flights = list(
        flight_bookings
        .order_by("-booked_at")[:5]
    )

    recent_groups = list(
        group_bookings
        .order_by("-booked_at")[:5]
    )

    recent_umrah = list(
        umrah_bookings
        .order_by("-booked_at")[:5]
    )

    recent_bookings = (
        recent_flights
        + recent_groups
        + recent_umrah
    )

    # =================================================
    # MARK BOOKING TYPE
    # =================================================

    for booking in recent_flights:
        booking.booking_type = "FLIGHT"

    for booking in recent_groups:
        booking.booking_type = "GROUP"

    for booking in recent_umrah:
        booking.booking_type = "UMRAH"

    # =================================================
    # SORT RECENT BOOKINGS
    # =================================================

    recent_bookings.sort(
        key=lambda booking: booking.booked_at,
        reverse=True
    )

    recent_bookings = recent_bookings[:5]

    # =================================================
    # UPCOMING DEPARTURES
    # =================================================

    upcoming_departures = []

    # -------------------------------------------------
    # FLIGHTS
    # -------------------------------------------------

    for booking in flight_bookings.filter(
        status="CONFIRMED"
    ).order_by(
        "flight__departure_date",
        "flight__departure_time"
    )[:10]:

        if booking.flight.departure_date >= today:

            booking.departure_date_dynamic = (
                booking.flight.departure_date
            )

            booking.departure_route_dynamic = (
                f"{booking.flight.departure_airport.code}"
                f" → "
                f"{booking.flight.arrival_airport.code}"
            )

            booking.departure_type_dynamic = "FLIGHT"

            upcoming_departures.append(
                booking
            )

    # -------------------------------------------------
    # GROUP
    # -------------------------------------------------

    for booking in group_bookings.filter(
        status="CONFIRMED"
    ).order_by(
        "group_ticket__departure_date",
        "group_ticket__departure_time"
    )[:10]:

        if booking.group_ticket.departure_date >= today:

            booking.departure_date_dynamic = (
                booking.group_ticket.departure_date
            )

            booking.departure_route_dynamic = (
                f"{booking.group_ticket.departure_airport.code}"
                f" → "
                f"{booking.group_ticket.arrival_airport.code}"
            )

            booking.departure_type_dynamic = "GROUP"

            upcoming_departures.append(
                booking
            )

    # -------------------------------------------------
    # UMRAH
    # -------------------------------------------------

    for booking in umrah_bookings.filter(
        status="CONFIRMED"
    ).order_by(
        "package__outbound_departure_date"
    )[:10]:

        if booking.package.outbound_departure_date >= today:

            booking.departure_date_dynamic = (
                booking.package.outbound_departure_date
            )

            booking.departure_route_dynamic = (
                f"{booking.package.outbound_departure_airport.code}"
                f" → "
                f"{booking.package.outbound_arrival_airport.code}"
            )

            booking.departure_type_dynamic = "UMRAH"

            upcoming_departures.append(
                booking
            )

    # =================================================
    # SORT UPCOMING
    # =================================================

    upcoming_departures.sort(
        key=lambda booking: booking.departure_date_dynamic
    )

    upcoming_departures = upcoming_departures[:5]

    # =================================================
    # EXPIRING UMRAH BOOKINGS
    # =================================================

    expiring_soon = umrah_bookings.filter(
        status="CONFIRMED",
        expires_at__isnull=False,
        expires_at__date__lte=today + timedelta(days=1)
    ).count()

    # =================================================
    # TEAM / STAFF
    # =================================================

    # Your current system does not yet show a separate
    # staff-member model, so keep this at zero for now.
    team_members = 0

    # =================================================
    # PAYMENT PENDING
    # =================================================

    payment_pending = TopUpRequest.objects.filter(
        agent=agent,
        status="PENDING"
    ).count()

    # =================================================
    # TOP ROUTES
    # =================================================

    route_counts = {}

    # Flights
    for booking in flight_bookings:

        route = (
            f"{booking.flight.departure_airport.code}"
            f" → "
            f"{booking.flight.arrival_airport.code}"
        )

        route_counts[route] = (
            route_counts.get(route, 0) + 1
        )

    # Group tickets
    for booking in group_bookings:

        route = (
            f"{booking.group_ticket.departure_airport.code}"
            f" → "
            f"{booking.group_ticket.arrival_airport.code}"
        )

        route_counts[route] = (
            route_counts.get(route, 0) + 1
        )

    # Umrah
    for booking in umrah_bookings:

        route = (
            f"{booking.package.outbound_departure_airport.code}"
            f" → "
            f"{booking.package.outbound_arrival_airport.code}"
        )

        route_counts[route] = (
            route_counts.get(route, 0) + 1
        )

    top_routes = sorted(
        route_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )[:5]

    # =================================================
    # WALLET NOTICE
    # =================================================

    wallet_low = wallet_balance < 10000

    # =================================================
    # TOTAL ACTIVE BOOKINGS
    # =================================================

    active_bookings = (
        confirmed_bookings
        + pending_requests
    )

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        "agent": agent,

        # -----------------------------
        # WALLET
        # -----------------------------

        "wallet": wallet,

        "wallet_balance": wallet_balance,

        "wallet_low": wallet_low,

        # -----------------------------
        # MAIN STATS
        # -----------------------------

        "total_sales": total_sales,

        "active_bookings": active_bookings,

        "confirmed_bookings": confirmed_bookings,

        "pending_requests": pending_requests,

        "team_members": team_members,

        # -----------------------------
        # TODAY
        # -----------------------------

        "bookings_today": bookings_today,

        "confirmed_today": confirmed_today,

        "cancelled_today": cancelled_today,

        "revenue_today": revenue_today,

        # -----------------------------
        # ACTION REQUIRED
        # -----------------------------

        "payment_pending": payment_pending,

        "expiring_soon": expiring_soon,

        # -----------------------------
        # BOOKINGS
        # -----------------------------

        "recent_bookings": recent_bookings,

        "upcoming_departures": upcoming_departures,

        # -----------------------------
        # ROUTES
        # -----------------------------

        "top_routes": top_routes,

        # -----------------------------
        # PROFIT
        # -----------------------------
        # Profit/commission is not currently
        # stored in the booking models.

        "total_profit": 0,
    }

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "agent-dashboard.html",
        context
    )

# =====================================================
# LOGOUT
# =====================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# =====================================================
# BOOK FLIGHT
# =====================================================

@login_required(login_url="login")
def book_flight(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    flights = Flight.objects.filter(
        is_active=True,
        available_seats__gt=0
    ).select_related(
        "airline",
        "departure_airport",
        "arrival_airport"
    ).order_by(
        "departure_date",
        "departure_time"
    )

    # =================================================
    # SEARCH FILTERS
    # =================================================

    from_code = request.GET.get(
        "from",
        ""
    ).strip().upper()

    to_code = request.GET.get(
        "to",
        ""
    ).strip().upper()

    travel_date = request.GET.get(
        "date",
        ""
    ).strip()

    airline_code = request.GET.get(
        "airline",
        ""
    ).strip().upper()

    category = request.GET.get(
        "category",
        ""
    ).strip().upper()

    # =================================================
    # FROM AIRPORT
    # =================================================

    if from_code:

        flights = flights.filter(
            departure_airport__code=from_code
        )

    # =================================================
    # TO AIRPORT
    # =================================================

    if to_code:

        flights = flights.filter(
            arrival_airport__code=to_code
        )

    # =================================================
    # DATE
    # =================================================

    if travel_date:

        flights = flights.filter(
            departure_date=travel_date
        )

    # =================================================
    # AIRLINE
    # =================================================

    if airline_code:

        flights = flights.filter(
            airline__code=airline_code
        )

    # =================================================
    # CATEGORY
    # =================================================

    if category:

        flights = flights.filter(
            category=category
        )

    # =================================================
    # DROPDOWN DATA
    # =================================================

    airlines = Airline.objects.filter(
        is_active=True
    ).order_by(
        "name"
    )

    airports = Airport.objects.filter(
        is_active=True
    ).order_by(
        "city"
    )

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        "agent": agent,

        "flights": flights,

        "airlines": airlines,

        "airports": airports,

        "search_from": from_code,

        "search_to": to_code,

        "search_date": travel_date,

        "search_airline": airline_code,

        "search_category": category,

    }

    return render(
        request,
        "book-flight.html",
        context
    )


# =====================================================
# CREATE BOOKING
# =====================================================

@login_required(login_url="login")
def create_booking(request, flight_id):

    flight = get_object_or_404(
        Flight,
        id=flight_id,
        is_active=True
    )

    # =================================================
    # CHECK SEATS
    # =================================================

    if flight.available_seats <= 0:

        messages.error(
            request,
            "Sorry, this flight is fully booked."
        )

        return redirect("book_flight")

    # =================================================
    # GET LOGGED-IN AGENT
    # =================================================

    try:

        agent = Agent.objects.get(
            user=request.user
        )

    except Agent.DoesNotExist:

        messages.error(
            request,
            "Agent profile not found."
        )

        return redirect("agent_dashboard")

    # =================================================
    # POST
    # =================================================

    if request.method == "POST":

        passenger_form = PassengerForm(
            request.POST
        )

        seats_booked = request.POST.get(
            "seats_booked",
            "1"
        )

        # -------------------------------------------------
        # CONVERT SEATS TO INTEGER
        # -------------------------------------------------

        try:

            seats_booked = int(
                seats_booked
            )

        except (ValueError, TypeError):

            seats_booked = 0

        # -------------------------------------------------
        # VALIDATE SEATS
        # -------------------------------------------------

        if seats_booked < 1:

            messages.error(
                request,
                "Please select at least 1 seat."
            )

        elif seats_booked > flight.available_seats:

            messages.error(
                request,
                f"Only {flight.available_seats} seat(s) are available."
            )

        elif passenger_form.is_valid():

            # =================================================
            # DATABASE TRANSACTION
            # =================================================

            with transaction.atomic():

                # Refresh and lock flight row

                flight = Flight.objects.select_for_update().get(
                    id=flight_id
                )

                # -------------------------------------------------
                # CHECK SEATS AGAIN
                # -------------------------------------------------

                if seats_booked > flight.available_seats:

                    messages.error(
                        request,
                        "Sorry, the requested seats are no longer available."
                    )

                    return redirect(
                        "create_booking",
                        flight_id=flight.id
                    )

                # -------------------------------------------------
                # SAVE PASSENGER
                # -------------------------------------------------

                passenger = passenger_form.save()

                # -------------------------------------------------
                # CALCULATE TOTAL PRICE
                # -------------------------------------------------

                total_price = (
                    flight.price * seats_booked
                )

                # -------------------------------------------------
                # GENERATE BOOKING REFERENCE
                # -------------------------------------------------

                while True:

                    booking_reference = (
                        "ALN-"
                        + get_random_string(
                            8
                        ).upper()
                    )

                    if not Booking.objects.filter(
                        booking_reference=booking_reference
                    ).exists():

                        break

                # -------------------------------------------------
                # CREATE BOOKING
                # -------------------------------------------------

                booking = Booking.objects.create(

                    booking_reference=booking_reference,

                    agent=agent,

                    flight=flight,

                    passenger=passenger,

                    seats_booked=seats_booked,

                    total_price=total_price,

                    status="PENDING"
                )

                # -------------------------------------------------
                # REDUCE AVAILABLE SEATS
                # -------------------------------------------------

                flight.available_seats -= seats_booked

                flight.save(
                    update_fields=[
                        "available_seats"
                    ]
                )

            # =================================================
            # SUCCESS
            # =================================================

            messages.success(
                request,
                f"Booking {booking.booking_reference} created successfully."
            )

            return redirect(
                "booking_success",
                booking_id=booking.id
            )

    else:

        passenger_form = PassengerForm()

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "create_booking.html",
        {
            "flight": flight,
            "passenger_form": passenger_form,
        }
    )


# =====================================================
# BOOKING SUCCESS
# =====================================================

@login_required(login_url="login")
def booking_success(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    return render(
        request,
        "booking_success.html",
        {
            "booking": booking
        }
    )


# =====================================================
# AGENT BOOKINGS
# =====================================================

@login_required(login_url="login")
def bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    bookings = Booking.objects.filter(
        agent=agent
    ).select_related(
        "flight",
        "flight__airline",
        "flight__departure_airport",
        "flight__arrival_airport",
        "passenger"
    ).order_by(
        "-booked_at"
    )

    # =================================================
    # BOOKING COUNTS
    # =================================================

    pending_count = bookings.filter(
        status="PENDING"
    ).count()

    confirmed_count = bookings.filter(
        status="CONFIRMED"
    ).count()

    cancelled_count = bookings.filter(
        status="CANCELLED"
    ).count()

    completed_count = bookings.filter(
        status="COMPLETED"
    ).count()

    return render(
        request,
        "bookings.html",
        {
            "agent": agent,
            "bookings": bookings,

            "pending_count": pending_count,

            "confirmed_count": confirmed_count,

            "cancelled_count": cancelled_count,

            "completed_count": completed_count,
        }
    )




# =====================================================
# ADMIN DASHBOARD
# =====================================================

# =====================================================
# ADMIN DASHBOARD
# =====================================================

@login_required(login_url="login")
def admin_dashboard(request):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You are not authorized to access the Admin Dashboard."
        )

        return redirect("home")

    # =================================================
    # AGENTS
    # =================================================

    pending_agents = Agent.objects.filter(
        status="PENDING"
    ).order_by(
        "-created_at"
    )

    approved_agents = Agent.objects.filter(
        status="APPROVED"
    ).order_by(
        "-created_at"
    )

    rejected_agents = Agent.objects.filter(
        status="REJECTED"
    ).order_by(
        "-created_at"
    )

    suspended_agents = Agent.objects.filter(
        status="SUSPENDED"
    ).order_by(
        "-created_at"
    )

    # =================================================
    # NORMAL FLIGHT BOOKINGS
    # =================================================

    recent_bookings = Booking.objects.select_related(
        "agent",
        "flight",
        "flight__airline",
        "flight__departure_airport",
        "flight__arrival_airport",
        "passenger"
    ).order_by(
        "-booked_at"
    )[:10]

    pending_bookings_count = Booking.objects.filter(
        status="PENDING"
    ).count()

    confirmed_bookings_count = Booking.objects.filter(
        status="CONFIRMED"
    ).count()

    cancelled_bookings_count = Booking.objects.filter(
        status="CANCELLED"
    ).count()

    total_bookings_count = Booking.objects.count()

    # =================================================
    # GROUP BOOKINGS
    # =================================================

    recent_group_bookings = GroupBooking.objects.select_related(
        "agent",
        "group_ticket",
        "group_ticket__airline",
        "group_ticket__departure_airport",
        "group_ticket__arrival_airport",
        "passenger"
    ).order_by(
        "-booked_at"
    )[:10]

    pending_group_bookings_count = GroupBooking.objects.filter(
        status="PENDING"
    ).count()

    confirmed_group_bookings_count = GroupBooking.objects.filter(
        status="CONFIRMED"
    ).count()

    rejected_group_bookings_count = GroupBooking.objects.filter(
        status="REJECTED"
    ).count()

    total_group_bookings_count = GroupBooking.objects.count()

    # =================================================
    # UMRAH BOOKINGS
    # =================================================

    recent_umrah_bookings = (
        UmrahBooking.objects
        .select_related(
            "agent",
            "package",
            "package__airline",
            "lead_passenger"
        )
        .order_by(
            "-booked_at"
        )[:10]
    )

    pending_umrah_bookings_count = (
        UmrahBooking.objects.filter(
            status="PENDING"
        ).count()
    )

    confirmed_umrah_bookings_count = (
        UmrahBooking.objects.filter(
            status="CONFIRMED"
        ).count()
    )

    rejected_umrah_bookings_count = (
        UmrahBooking.objects.filter(
            status="REJECTED"
        ).count()
    )

    total_umrah_bookings_count = (
        UmrahBooking.objects.count()
    )

    # =================================================
    # WALLET TOP-UP REQUESTS
    # =================================================

    pending_topup_requests = TopUpRequest.objects.filter(
        status="PENDING"
    ).select_related(
        "agent"
    ).order_by(
        "-created_at"
    )

    pending_topup_requests_count = pending_topup_requests.count()

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        # -----------------------------
        # AGENTS
        # -----------------------------

        "pending_agents": pending_agents,

        "approved_agents": approved_agents,

        "rejected_agents": rejected_agents,

        "suspended_agents": suspended_agents,

        "pending_count": pending_agents.count(),

        "approved_count": approved_agents.count(),

        "rejected_count": rejected_agents.count(),

        "suspended_count": suspended_agents.count(),

        # -----------------------------
        # NORMAL BOOKINGS
        # -----------------------------

        "recent_bookings": recent_bookings,

        "pending_bookings_count": pending_bookings_count,

        "confirmed_bookings_count": confirmed_bookings_count,

        "cancelled_bookings_count": cancelled_bookings_count,

        "total_bookings_count": total_bookings_count,

        # -----------------------------
        # GROUP BOOKINGS
        # -----------------------------

        "recent_group_bookings": recent_group_bookings,

        "pending_group_bookings_count":
            pending_group_bookings_count,

        "confirmed_group_bookings_count":
            confirmed_group_bookings_count,

        "rejected_group_bookings_count":
            rejected_group_bookings_count,

        "total_group_bookings_count":
            total_group_bookings_count,

        # -----------------------------
        # UMRAH BOOKINGS
        # -----------------------------

        "recent_umrah_bookings":
            recent_umrah_bookings,

        "pending_umrah_bookings_count":
            pending_umrah_bookings_count,

        "confirmed_umrah_bookings_count":
            confirmed_umrah_bookings_count,

        "rejected_umrah_bookings_count":
            rejected_umrah_bookings_count,

        "total_umrah_bookings_count":
            total_umrah_bookings_count,

        # -----------------------------
        # WALLET
        # -----------------------------

        "pending_topup_requests":
            pending_topup_requests,

        "pending_topup_requests_count":
            pending_topup_requests_count,

    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )
# =====================================================
# ADMIN - PENDING AGENTS
# =====================================================

@login_required(login_url="login")
def pending_agents(request):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access the Admin Dashboard."
        )

        return redirect("login")

    agents = Agent.objects.filter(
        status="PENDING"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "pending_agents.html",
        {
            "agents": agents
        }
    )


# =====================================================
# ADMIN - AGENT DETAIL
# =====================================================

@login_required(login_url="login")
def admin_agent_detail(request, agent_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access this page."
        )

        return redirect("login")

    agent = get_object_or_404(
        Agent,
        id=agent_id
    )

    return render(
        request,
        "admin_agent_detail.html",
        {
            "agent": agent
        }
    )


# =====================================================
# ADMIN - APPROVE AGENT
# =====================================================

@login_required(login_url="login")
def approve_agent(request, agent_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to perform this action."
        )

        return redirect("login")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_agent_detail",
            agent_id=agent_id
        )

    agent = get_object_or_404(
        Agent,
        id=agent_id
    )

    agent.status = "APPROVED"
    agent.rejection_reason = ""

    agent.save()

    messages.success(
        request,
        f"{agent.name} has been approved successfully."
    )

    return redirect(
        "admin_agent_detail",
        agent_id=agent.id
    )


# =====================================================
# ADMIN - REJECT AGENT
# =====================================================

@login_required(login_url="login")
def reject_agent(request, agent_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to perform this action."
        )

        return redirect("login")

    agent = get_object_or_404(
        Agent,
        id=agent_id
    )

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_agent_detail",
            agent_id=agent.id
        )

    reason = request.POST.get(
        "rejection_reason",
        ""
    ).strip()

    if not reason:

        messages.error(
            request,
            "Please provide a rejection reason."
        )

        return redirect(
            "admin_agent_detail",
            agent_id=agent.id
        )

    agent.status = "REJECTED"
    agent.rejection_reason = reason

    agent.save()

    messages.success(
        request,
        f"{agent.name} has been rejected."
    )

    return redirect(
        "admin_agent_detail",
        agent_id=agent.id
    )


# =====================================================
# ADMIN - SUSPEND AGENT
# =====================================================

@login_required(login_url="login")
def suspend_agent(request, agent_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to perform this action."
        )

        return redirect("login")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_agent_detail",
            agent_id=agent_id
        )

    agent = get_object_or_404(
        Agent,
        id=agent_id
    )

    agent.status = "SUSPENDED"

    agent.save()

    messages.warning(
        request,
        f"{agent.name} has been suspended."
    )

    return redirect(
        "admin_agent_detail",
        agent_id=agent.id
    )


# =====================================================
# ADMIN - BOOKING DETAIL
# =====================================================

@login_required(login_url="login")
def admin_booking_detail(request, booking_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access this booking."
        )

        return redirect("login")

    booking = get_object_or_404(

        Booking.objects.select_related(
            "agent",
            "flight",
            "flight__airline",
            "flight__departure_airport",
            "flight__arrival_airport",
            "passenger"
        ),

        id=booking_id
    )

    return render(
        request,
        "admin_booking_detail.html",
        {
            "booking": booking
        }
    )


# =====================================================
# ADMIN - CONFIRM BOOKING
# =====================================================

@login_required(login_url="login")
def confirm_booking(request, booking_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to confirm bookings."
        )

        return redirect("login")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_booking_detail",
            booking_id=booking_id
        )

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    # =================================================
    # CHECK CURRENT STATUS
    # =================================================

    if booking.status != "PENDING":

        messages.warning(
            request,
            "This booking cannot be confirmed."
        )

        return redirect(
            "admin_booking_detail",
            booking_id=booking.id
        )

    # =================================================
    # GENERATE PNR
    # =================================================

    while True:

        pnr = (
            "ALN"
            + get_random_string(
                6
            ).upper()
        )

        if not Booking.objects.filter(
            pnr=pnr
        ).exists():

            break

    # =================================================
    # GENERATE TICKET NUMBER
    # =================================================

    while True:

        ticket_number = (
            "220"
            + get_random_string(
                10,
                allowed_chars="0123456789"
            )
        )

        if not Booking.objects.filter(
            ticket_number=ticket_number
        ).exists():

            break

    # =================================================
    # CONFIRM BOOKING
    # =================================================

    booking.status = "CONFIRMED"

    booking.pnr = pnr

    booking.ticket_number = ticket_number

    booking.save(
        update_fields=[
            "status",
            "pnr",
            "ticket_number",
            "updated_at"
        ]
    )

    # =================================================
    # SUCCESS MESSAGE
    # =================================================

    messages.success(
        request,
        f"Booking {booking.booking_reference} has been confirmed successfully."
    )

    return redirect(
        "admin_booking_detail",
        booking_id=booking.id
    )


# =====================================================
# ADMIN - CANCEL BOOKING
# =====================================================

@login_required(login_url="login")
def cancel_booking(request, booking_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to cancel bookings."
        )

        return redirect("login")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_booking_detail",
            booking_id=booking_id
        )

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    if booking.status != "PENDING":

        messages.warning(
            request,
            "This booking cannot be cancelled."
        )

        return redirect(
            "admin_booking_detail",
            booking_id=booking.id
        )

    booking.status = "CANCELLED"

    booking.save(
        update_fields=[
            "status"
        ]
    )

    messages.success(
        request,
        f"Booking {booking.booking_reference} has been cancelled."
    )

    return redirect(
        "admin_booking_detail",
        booking_id=booking.id
    )


# =====================================================
# ADMIN - GROUP TICKETS
# =====================================================

@login_required(login_url="login")
def admin_group_tickets(request):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access Group Tickets."
        )

        return redirect("login")

    # =================================================
    # BASE GROUP TICKET QUERYSET
    # =================================================

    group_tickets = GroupTicket.objects.select_related(
        "airline",
        "departure_airport",
        "arrival_airport"
    ).order_by(
        "-created_at"
    )

    # =================================================
    # SEARCH
    # =================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        group_tickets = group_tickets.filter(

            Q(
                airline__name__icontains=search
            )
            |
            Q(
                airline__code__icontains=search
            )
            |
            Q(
                flight_number__icontains=search
            )
            |
            Q(
                departure_airport__code__icontains=search
            )
            |
            Q(
                arrival_airport__code__icontains=search
            )

        )

    # =================================================
    # STATUS FILTER
    # =================================================

    status = request.GET.get(
        "status",
        ""
    ).strip().lower()

    if status == "active":

        group_tickets = group_tickets.filter(
            is_active=True
        )

    elif status == "inactive":

        group_tickets = group_tickets.filter(
            is_active=False
        )

    # =================================================
    # AVAILABILITY FILTER
    # =================================================

    availability = request.GET.get(
        "availability",
        ""
    ).strip().lower()

    if availability == "available":

        group_tickets = group_tickets.filter(
            available_seats__gt=0
        )

    elif availability == "soldout":

        group_tickets = group_tickets.filter(
            available_seats=0
        )

    # =================================================
    # SUMMARY STATISTICS
    # =================================================

    total_group_tickets = group_tickets.count()

    active_count = group_tickets.filter(
        is_active=True
    ).count()

    total_available = sum(
        ticket.available_seats
        for ticket in group_tickets
    )

    total_seats = sum(
        ticket.total_seats
        for ticket in group_tickets
    )

    total_sold = total_seats - total_available

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        "group_tickets": group_tickets,

        "total_group_tickets": total_group_tickets,

        "active_count": active_count,

        "total_available": total_available,

        "total_sold": total_sold,

    }

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "admin/group-tickets.html",
        context
    )


# =====================================================
# ADMIN - ADD GROUP TICKET
# =====================================================

@login_required(login_url="login")
def admin_add_group_ticket(request):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to add Group Tickets."
        )

        return redirect("login")

    if request.method == "POST":

        form = GroupTicketForm(
            request.POST
        )

        if form.is_valid():

            group_ticket = form.save()

            messages.success(
                request,
                f"Group Ticket {group_ticket.flight_number} added successfully."
            )

            return redirect(
                "admin_group_tickets"
            )

    else:

        form = GroupTicketForm()

    return render(
        request,
        "admin/add-group-ticket.html",
        {
            "form": form
        }
    )


# =====================================================
# ADMIN - EDIT GROUP TICKET
# =====================================================

@login_required(login_url="login")
def admin_edit_group_ticket(request, ticket_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to edit Group Tickets."
        )

        return redirect("login")

    group_ticket = get_object_or_404(
        GroupTicket,
        id=ticket_id
    )

    if request.method == "POST":

        form = GroupTicketForm(
            request.POST,
            instance=group_ticket
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Group Ticket updated successfully."
            )

            return redirect(
                "admin_group_tickets"
            )

    else:

        form = GroupTicketForm(
            instance=group_ticket
        )

    return render(
        request,
        "admin/add-group-ticket.html",
        {
            "form": form,
            "group_ticket": group_ticket
        }
    )


# =====================================================
# ADMIN - DELETE GROUP TICKET
# =====================================================

@login_required(login_url="login")
def admin_delete_group_ticket(request, ticket_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to delete Group Tickets."
        )

        return redirect("login")

    group_ticket = get_object_or_404(
        GroupTicket,
        id=ticket_id
    )

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_group_tickets"
        )

    flight_number = group_ticket.flight_number

    group_ticket.delete()

    messages.success(
        request,
        f"Group Ticket {flight_number} deleted successfully."
    )

    return redirect(
        "admin_group_tickets"
    )


# =====================================================
# AGENT - ALL BOOKINGS
# =====================================================

# =====================================================
# AGENT - ALL BOOKINGS
# =====================================================
from .models import (
    Agent,
    Booking,
    GroupBooking,
    UmrahBooking,
)
@login_required(login_url="login")
def agent_all_bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # NORMAL FLIGHT BOOKINGS
    # =================================================

    flight_bookings = list(
        Booking.objects.filter(
            agent=agent
        ).select_related(
            "flight",
            "flight__airline",
            "flight__departure_airport",
            "flight__arrival_airport",
            "passenger"
        )
    )

    # Mark booking type
    for booking in flight_bookings:
        booking.booking_type = "FLIGHT"

    # =================================================
    # GROUP TICKET BOOKINGS
    # =================================================

    group_bookings = list(
        GroupBooking.objects.filter(
            agent=agent
        ).select_related(
            "group_ticket",
            "group_ticket__airline",
            "group_ticket__departure_airport",
            "group_ticket__arrival_airport",
            "passenger"
        )
    )

    # Mark booking type
    for booking in group_bookings:
        booking.booking_type = "GROUP"

    # =================================================
    # UMRAH BOOKINGS
    # =================================================

    umrah_bookings = list(
        UmrahBooking.objects.filter(
            agent=agent
        ).select_related(
            "package",
            "package__airline",
            "package__outbound_departure_airport",
            "package__outbound_arrival_airport",
            "package__return_departure_airport",
            "package__return_arrival_airport",
            "package__makkah_hotel",
            "package__madinah_hotel",
            "lead_passenger"
        )
    )

    # Mark booking type
    for booking in umrah_bookings:
        booking.booking_type = "UMRAH"

    # =================================================
    # COMBINE ALL BOOKING TYPES
    # =================================================

    combined_bookings = (
        flight_bookings +
        group_bookings +
        umrah_bookings
    )

    # =================================================
    # SORT BY NEWEST BOOKING
    # =================================================

    combined_bookings.sort(
        key=lambda booking: booking.booked_at,
        reverse=True
    )

    # =================================================
    # CONTEXT
    # =================================================

    return render(
        request,
        "agent/all-bookings.html",
        {
            "agent": agent,
            "bookings": combined_bookings,
        }
    )

# =====================================================
# AGENT - PENDING BOOKINGS
# =====================================================

@login_required(login_url="login")
def agent_pending_bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # NORMAL FLIGHT BOOKINGS
    # =================================================

    flight_bookings = list(
        Booking.objects.filter(
            agent=agent,
            status="PENDING"
        ).select_related(
            "flight",
            "flight__airline",
            "flight__departure_airport",
            "flight__arrival_airport",
            "passenger"
        )
    )

    for booking in flight_bookings:
        booking.booking_type = "FLIGHT"

    # =================================================
    # GROUP TICKET BOOKINGS
    # =================================================

    group_bookings = list(
        GroupBooking.objects.filter(
            agent=agent,
            status="PENDING"
        ).select_related(
            "group_ticket",
            "group_ticket__airline",
            "group_ticket__departure_airport",
            "group_ticket__arrival_airport",
            "passenger"
        )
    )

    for booking in group_bookings:
        booking.booking_type = "GROUP"

    # =================================================
    # UMRAH BOOKINGS
    # =================================================

    umrah_bookings = list(
        UmrahBooking.objects.filter(
            agent=agent,
            status="PENDING"
        ).select_related(
            "package",
            "package__airline",
            "package__outbound_departure_airport",
            "package__outbound_arrival_airport",
            "package__return_departure_airport",
            "package__return_arrival_airport",
            "package__makkah_hotel",
            "package__madinah_hotel",
            "lead_passenger"
        )
    )

    for booking in umrah_bookings:
        booking.booking_type = "UMRAH"

    bookings = (
        flight_bookings +
        group_bookings +
        umrah_bookings
    )

    bookings.sort(
        key=lambda booking: booking.booked_at,
        reverse=True
    )

    return render(
        request,
        "agent/pending-bookings.html",
        {
            "agent": agent,
            "bookings": bookings,
        }
    )


# =====================================================
# AGENT - CONFIRMED BOOKINGS
# =====================================================

@login_required(login_url="login")
def agent_confirmed_bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # EXPIRE UMRAH BOOKINGS AFTER 24 HOURS
    # =================================================

    now = timezone.now()

    UmrahBooking.objects.filter(
        agent=agent,
        status="CONFIRMED",
        expires_at__isnull=False,
        expires_at__lte=now
    ).update(
        status="EXPIRED"
    )

    # =================================================
    # NORMAL FLIGHT BOOKINGS
    # =================================================

    flight_bookings = list(
        Booking.objects.filter(
            agent=agent,
            status="CONFIRMED"
        ).select_related(
            "flight",
            "flight__airline",
            "flight__departure_airport",
            "flight__arrival_airport",
            "passenger"
        )
    )

    for booking in flight_bookings:
        booking.booking_type = "FLIGHT"

    # =================================================
    # GROUP TICKET BOOKINGS
    # =================================================

    group_bookings = list(
        GroupBooking.objects.filter(
            agent=agent,
            status="CONFIRMED"
        ).select_related(
            "group_ticket",
            "group_ticket__airline",
            "group_ticket__departure_airport",
            "group_ticket__arrival_airport",
            "passenger"
        )
    )

    for booking in group_bookings:
        booking.booking_type = "GROUP"

    # =================================================
    # UMRAH BOOKINGS
    # CONFIRMED + EXPIRED
    # =================================================

    umrah_bookings = list(
        UmrahBooking.objects.filter(
            agent=agent,
            status__in=[
                "CONFIRMED",
                "EXPIRED"
            ]
        ).select_related(
            "package",
            "package__airline",
            "package__outbound_departure_airport",
            "package__outbound_arrival_airport",
            "package__return_departure_airport",
            "package__return_arrival_airport",
            "package__makkah_hotel",
            "package__madinah_hotel",
            "lead_passenger"
        )
    )

    for booking in umrah_bookings:
        booking.booking_type = "UMRAH"

    # =================================================
    # COMBINE ALL CONFIRMED/EXPIRED BOOKINGS
    # =================================================

    bookings = (
        flight_bookings +
        group_bookings +
        umrah_bookings
    )

    # =================================================
    # SORT BY NEWEST BOOKING
    # =================================================

    bookings.sort(
        key=lambda booking: booking.booked_at,
        reverse=True
    )

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "agent/confirmed-bookings.html",
        {
            "agent": agent,
            "bookings": bookings,
        }
    )


# =====================================================
# AGENT - REJECTED BOOKINGS
# =====================================================

@login_required(login_url="login")
def agent_rejected_bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # NORMAL FLIGHT BOOKINGS
    # =================================================

    flight_bookings = list(
        Booking.objects.filter(
            agent=agent,
            status="REJECTED"
        ).select_related(
            "flight",
            "flight__airline",
            "flight__departure_airport",
            "flight__arrival_airport",
            "passenger"
        )
    )

    for booking in flight_bookings:
        booking.booking_type = "FLIGHT"

    # =================================================
    # GROUP TICKET BOOKINGS
    # =================================================

    group_bookings = list(
        GroupBooking.objects.filter(
            agent=agent,
            status="REJECTED"
        ).select_related(
            "group_ticket",
            "group_ticket__airline",
            "group_ticket__departure_airport",
            "group_ticket__arrival_airport",
            "passenger"
        )
    )

    for booking in group_bookings:
        booking.booking_type = "GROUP"

    # =================================================
    # UMRAH BOOKINGS
    # =================================================

    umrah_bookings = list(
        UmrahBooking.objects.filter(
            agent=agent,
            status="REJECTED"
        ).select_related(
            "package",
            "package__airline",
            "package__outbound_departure_airport",
            "package__outbound_arrival_airport",
            "package__return_departure_airport",
            "package__return_arrival_airport",
            "package__makkah_hotel",
            "package__madinah_hotel",
            "lead_passenger"
        )
    )

    for booking in umrah_bookings:
        booking.booking_type = "UMRAH"

    bookings = (
        flight_bookings +
        group_bookings +
        umrah_bookings
    )

    bookings.sort(
        key=lambda booking: booking.booked_at,
        reverse=True
    )

    return render(
        request,
        "agent/rejected-bookings.html",
        {
            "agent": agent,
            "bookings": bookings,
        }
    )
# =====================================================
# AGENT - VIEW TICKET
# =====================================================

@login_required(login_url="login")
def agent_view_ticket(request, booking_id):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    booking = get_object_or_404(
        Booking.objects.select_related(
            "flight",
            "flight__airline",
            "flight__departure_airport",
            "flight__arrival_airport",
            "passenger"
        ),
        id=booking_id,
        agent=agent,
        status="CONFIRMED"
    )

    return render(
        request,
        "agent/view-ticket.html",
        {
            "agent": agent,
            "booking": booking,
        }
    )


# =====================================================
# AGENT - GROUP BOOKINGS
# =====================================================

@login_required(login_url="login")
def agent_group_bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    return render(
        request,
        "agent/group-bookings.html",
        {
            "agent": agent,
        }
    )


# =====================================================
# AGENT - GROUP TICKETS
# =====================================================

@login_required(login_url="login")
def agent_group_tickets(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    group_tickets = GroupTicket.objects.filter(
        is_active=True,
        available_seats__gt=0
    ).select_related(
        "airline",
        "departure_airport",
        "arrival_airport"
    ).order_by(
        "departure_date",
        "departure_time"
    )

    # =================================================
    # SEARCH VALUES
    # =================================================

    from_code = request.GET.get(
        "from",
        ""
    ).strip().upper()

    to_code = request.GET.get(
        "to",
        ""
    ).strip().upper()

    travel_date = request.GET.get(
        "date",
        ""
    ).strip()

    airline_search = request.GET.get(
        "airline",
        ""
    ).strip()

    # =================================================
    # FROM
    # =================================================

    if from_code:

        group_tickets = group_tickets.filter(
            departure_airport__code=from_code
        )

    # =================================================
    # TO
    # =================================================

    if to_code:

        group_tickets = group_tickets.filter(
            arrival_airport__code=to_code
        )

    # =================================================
    # DATE
    # =================================================

    if travel_date:

        group_tickets = group_tickets.filter(
            departure_date=travel_date
        )

    # =================================================
    # AIRLINE
    # =================================================

    if airline_search:

        group_tickets = group_tickets.filter(
            Q(airline__code__icontains=airline_search)
            |
            Q(airline__name__icontains=airline_search)
        )

    # =================================================
    # AVAILABLE ROUTES FOR QUICK CATEGORIES
    # =================================================
    #
    # Only routes having:
    #   - active Group Ticket
    #   - available seats > 0
    #
    # will be considered AVAILABLE INVENTORY.
    # =================================================

    available_routes = list(
        GroupTicket.objects.filter(
            is_active=True,
            available_seats__gt=0
        ).values_list(
            "departure_airport__code",
            "arrival_airport__code"
        ).distinct()
    )

    available_routes = [
        f"{departure_code}-{arrival_code}"
        for departure_code, arrival_code in available_routes
    ]

    # =================================================
    # CONVERT ROUTES TO JSON
    # =================================================
    #
    # JavaScript will use this to highlight only the
    # routes for which inventory currently exists.
    # =================================================

    available_routes_json = json.dumps(
        available_routes
    )

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "agent/group-tickets.html",
        {
            "agent": agent,

            "group_tickets": group_tickets,

            "search_from": from_code,
            "search_to": to_code,
            "search_date": travel_date,
            "search_airline": airline_search,

            # QUICK CATEGORY ROUTES
            "available_routes": available_routes,

            # AVAILABLE ROUTES FOR JAVASCRIPT
            "available_routes_json": available_routes_json,
        }
    )
# =====================================================
# AGENT - CREATE GROUP BOOKING
# =====================================================

@login_required(login_url="login")
def create_group_booking(request, group_ticket_id):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    group_ticket = get_object_or_404(
        GroupTicket.objects.select_related(
            "airline",
            "departure_airport",
            "arrival_airport"
        ),
        id=group_ticket_id,
        is_active=True
    )

    # =================================================
    # CHECK AVAILABLE SEATS
    # =================================================

    if group_ticket.available_seats <= 0:

        messages.error(
            request,
            "Sorry, this group ticket is sold out."
        )

        return redirect(
            "agent_group_tickets"
        )

    # =================================================
    # POST
    # =================================================

    if request.method == "POST":

        passenger_form = PassengerForm(
            request.POST
        )

        seats_booked = request.POST.get(
            "seats_booked",
            "1"
        )

        # =================================================
        # CONVERT SEATS
        # =================================================

        try:

            seats_booked = int(
                seats_booked
            )

        except (ValueError, TypeError):

            seats_booked = 0

        # =================================================
        # VALIDATE SEATS
        # =================================================

        if seats_booked < 1:

            messages.error(
                request,
                "Please select at least 1 seat."
            )

        elif seats_booked > group_ticket.available_seats:

            messages.error(
                request,
                f"Only {group_ticket.available_seats} seat(s) are available."
            )

        elif passenger_form.is_valid():

            # =================================================
            # DATABASE TRANSACTION
            # =================================================

            with transaction.atomic():

                group_ticket = GroupTicket.objects.select_for_update().get(
                    id=group_ticket_id,
                    is_active=True
                )

                # -------------------------------------------------
                # CHECK AGAIN
                # -------------------------------------------------

                if seats_booked > group_ticket.available_seats:

                    messages.error(
                        request,
                        "Sorry, the requested seats are no longer available."
                    )

                    return redirect(
                        "create_group_booking",
                        group_ticket_id=group_ticket.id
                    )

                # -------------------------------------------------
                # SAVE PASSENGER
                # -------------------------------------------------

                passenger = passenger_form.save()

                # -------------------------------------------------
                # TOTAL PRICE
                # -------------------------------------------------

                total_price = (
                    group_ticket.price * seats_booked
                )

                # -------------------------------------------------
                # BOOKING REFERENCE
                # -------------------------------------------------

                while True:

                    booking_reference = (
                        "ALN-G"
                        + get_random_string(
                            8
                        ).upper()
                    )

                    if not GroupBooking.objects.filter(
                        booking_reference=booking_reference
                    ).exists():

                        break

                # -------------------------------------------------
                # CREATE GROUP BOOKING
                # -------------------------------------------------

                group_booking = GroupBooking.objects.create(

                    booking_reference=booking_reference,

                    agent=agent,

                    group_ticket=group_ticket,

                    passenger=passenger,

                    seats_booked=seats_booked,

                    total_price=total_price,

                    status="PENDING"
                )

                # -------------------------------------------------
                # REDUCE GROUP TICKET SEATS
                # -------------------------------------------------

                group_ticket.available_seats -= seats_booked

                group_ticket.save(
                    update_fields=[
                        "available_seats"
                    ]
                )

            # =================================================
            # SUCCESS
            # =================================================

            messages.success(
                request,
                f"Group booking {group_booking.booking_reference} created successfully."
            )

            return redirect(
                "group_booking_success",
                booking_id=group_booking.id
            )

    else:

        passenger_form = PassengerForm()

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "create_group_booking.html",
        {
            "agent": agent,
            "group_ticket": group_ticket,
            "passenger_form": passenger_form,
        }
    )


# =====================================================
# GROUP BOOKING SUCCESS
# =====================================================

@login_required(login_url="login")
def group_booking_success(request, booking_id):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    group_booking = get_object_or_404(
        GroupBooking.objects.select_related(
            "agent",
            "group_ticket",
            "group_ticket__airline",
            "group_ticket__departure_airport",
            "group_ticket__arrival_airport",
            "passenger"
        ),
        id=booking_id,
        agent=agent
    )

    return render(
        request,
        "group_booking_success.html",
        {
            "agent": agent,
            "booking": group_booking,
        }
    )


# =====================================================
# AGENT - UMRAH BOOKINGS
# =====================================================

# =====================================================
# AGENT - UMRAH PACKAGES
# =====================================================

@login_required(login_url="login")
def agent_umrah_bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # BASE PACKAGE QUERY
    # =================================================

    packages = (
        UmrahPackage.objects
        .filter(
            status="ACTIVE",
            available_seats__gt=0
        )
        .select_related(
            "airline",
            "outbound_departure_airport",
            "outbound_arrival_airport",
            "return_departure_airport",
            "return_arrival_airport",
            "makkah_hotel",
            "madinah_hotel",
        )
        .order_by(
            "outbound_departure_date",
            "price"
        )
    )

    # =================================================
    # SEARCH
    # =================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        packages = packages.filter(

            Q(name__icontains=search)
            |
            Q(sector__icontains=search)
            |
            Q(airline__name__icontains=search)
            |
            Q(airline__code__icontains=search)
            |
            Q(outbound_flight_number__icontains=search)
            |
            Q(return_flight_number__icontains=search)
            |
            Q(outbound_departure_airport__code__icontains=search)
            |
            Q(outbound_arrival_airport__code__icontains=search)
            |
            Q(return_departure_airport__code__icontains=search)
            |
            Q(return_arrival_airport__code__icontains=search)
            |
            Q(makkah_hotel__name__icontains=search)
            |
            Q(madinah_hotel__name__icontains=search)

        ).distinct()

    # =================================================
    # SECTOR FILTER
    # =================================================

    selected_sector = request.GET.get(
        "sector",
        ""
    ).strip()

    if selected_sector:

        packages = packages.filter(
            sector=selected_sector
        )

    # =================================================
    # AIRLINE FILTER
    # =================================================

    selected_airline = request.GET.get(
        "airline",
        ""
    ).strip()

    if selected_airline:

        packages = packages.filter(
            airline_id=selected_airline
        )

    # =================================================
    # MAKKAH HOTEL FILTER
    # =================================================

    selected_makkah_hotel = request.GET.get(
        "makkah_hotel",
        ""
    ).strip()

    if selected_makkah_hotel:

        packages = packages.filter(
            makkah_hotel_id=selected_makkah_hotel
        )

    # =================================================
    # MADINAH HOTEL FILTER
    # =================================================

    selected_madinah_hotel = request.GET.get(
        "madinah_hotel",
        ""
    ).strip()

    if selected_madinah_hotel:

        packages = packages.filter(
            madinah_hotel_id=selected_madinah_hotel
        )

    # =================================================
    # FILTER DATA
    # =================================================

    airlines = (
        Airline.objects
        .filter(
            is_active=True,
            umrah_packages__status="ACTIVE",
            umrah_packages__available_seats__gt=0
        )
        .distinct()
        .order_by("name")
    )

    makkah_hotels = (
        Hotel.objects
        .filter(
            location="MAKKAH",
            is_active=True,
            makkah_umrah_packages__status="ACTIVE",
            makkah_umrah_packages__available_seats__gt=0
        )
        .distinct()
        .order_by("name")
    )

    madinah_hotels = (
        Hotel.objects
        .filter(
            location="MADINAH",
            is_active=True,
            madinah_umrah_packages__status="ACTIVE",
            madinah_umrah_packages__available_seats__gt=0
        )
        .distinct()
        .order_by("name")
    )

    sectors = (
        UmrahPackage.objects
        .filter(
            status="ACTIVE",
            available_seats__gt=0
        )
        .values_list(
            "sector",
            flat=True
        )
        .distinct()
        .order_by("sector")
    )

    total_packages = packages.count()

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "agent/umrah-bookings.html",
        {
            "agent": agent,

            "packages": packages,

            "total_packages": total_packages,

            "airlines": airlines,

            "makkah_hotels": makkah_hotels,

            "madinah_hotels": madinah_hotels,

            "sectors": sectors,

            "search": search,

            "selected_sector": selected_sector,

            "selected_airline": selected_airline,

            "selected_makkah_hotel": selected_makkah_hotel,

            "selected_madinah_hotel": selected_madinah_hotel,
        }
    )
# =====================================================
# AGENT - TOUR BOOKINGS
# =====================================================

@login_required(login_url="login")
def agent_tour_bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    return render(
        request,
        "agent/tour-bookings.html",
        {
            "agent": agent,
        }
    )


# =====================================================
# AGENT - VISA BOOKINGS
# =====================================================

@login_required(login_url="login")
def agent_visa_bookings(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    return render(
        request,
        "agent/visa-bookings.html",
        {
            "agent": agent,
        }
    )


# =====================================================
# AGENT - WALLET
# =====================================================

# =====================================================
# AGENT - WALLET
# =====================================================

@login_required(login_url="login")
def agent_wallet(request):

    # =================================================
    # GET LOGGED-IN AGENT
    # =================================================

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # GET OR CREATE AGENT WALLET
    # =================================================

    wallet, created = AgentWallet.objects.get_or_create(
        agent=agent
    )

    # =================================================
    # SUBMIT TOP-UP REQUEST
    # =================================================

    if request.method == "POST":

        amount = request.POST.get(
            "amount",
            ""
        ).strip()

        transaction_date = request.POST.get(
            "transaction_date",
            ""
        ).strip()

        receipt = request.FILES.get(
            "receipt"
        )

        # -------------------------------------------------
        # VALIDATE AMOUNT
        # -------------------------------------------------

        try:

            amount = float(amount)

        except (ValueError, TypeError):

            amount = 0

        if amount <= 0:

            messages.error(
                request,
                "Please enter a valid top-up amount."
            )

            return redirect(
                "agent_wallet"
            )

        # -------------------------------------------------
        # VALIDATE DATE
        # -------------------------------------------------

        if not transaction_date:

            messages.error(
                request,
                "Please select the transaction date."
            )

            return redirect(
                "agent_wallet"
            )

        # -------------------------------------------------
        # VALIDATE RECEIPT
        # -------------------------------------------------

        if not receipt:

            messages.error(
                request,
                "Please upload your deposit receipt."
            )

            return redirect(
                "agent_wallet"
            )

        # -------------------------------------------------
        # CREATE TOP-UP REQUEST
        # -------------------------------------------------

        TopUpRequest.objects.create(

            agent=agent,

            amount=amount,

            transaction_date=transaction_date,

            receipt=receipt,

            status="PENDING"
        )

        messages.success(
            request,
            "Your top-up request has been submitted successfully. "
            "It is now waiting for admin approval."
        )

        return redirect(
            "agent_wallet"
        )

    # =================================================
    # RECENT TOP-UP REQUESTS
    # =================================================

    topup_requests = TopUpRequest.objects.filter(
        agent=agent
    ).order_by(
        "-created_at"
    )[:10]

    # =================================================
    # ALL WALLET TRANSACTIONS
    # =================================================

    all_transactions = WalletTransaction.objects.filter(
        agent=agent
    ).order_by(
        "created_at"
    )

    # =================================================
    # DATE FILTER VALUES
    # =================================================

    date_from = request.GET.get(
        "date_from",
        ""
    ).strip()

    date_to = request.GET.get(
        "date_to",
        ""
    ).strip()

    # =================================================
    # STATEMENT TRANSACTIONS
    # =================================================

    statement_transactions = all_transactions

    # =================================================
    # OPENING BALANCE
    # =================================================

    opening_balance = 0

    # -------------------------------------------------
    # APPLY FROM DATE
    # -------------------------------------------------

    if date_from:

        try:

            from_date = timezone.datetime.fromisoformat(
                date_from
            ).date()

            # Latest transaction before selected
            # From Date
            previous_transaction = (
                all_transactions
                .filter(
                    created_at__date__lt=from_date
                )
                .order_by(
                    "-created_at"
                )
                .first()
            )

            if previous_transaction:

                opening_balance = (
                    previous_transaction.balance_after
                )

            statement_transactions = (
                statement_transactions.filter(
                    created_at__date__gte=from_date
                )
            )

        except ValueError:

            date_from = ""

    # =================================================
    # APPLY TO DATE
    # =================================================

    if date_to:

        try:

            to_date = timezone.datetime.fromisoformat(
                date_to
            ).date()

            statement_transactions = (
                statement_transactions.filter(
                    created_at__date__lte=to_date
                )
            )

        except ValueError:

            date_to = ""

    # =================================================
    # CALCULATE STATEMENT TOTALS
    # =================================================

    total_credits = (
        statement_transactions.aggregate(
            total=models.Sum("credit")
        )["total"] or 0
    )

    total_debits = (
        statement_transactions.aggregate(
            total=models.Sum("debit")
        )["total"] or 0
    )

    # =================================================
    # CALCULATE CLOSING BALANCE
    # =================================================

    closing_balance = (
        opening_balance
        + total_credits
        - total_debits
    )

    # =================================================
    # TOTAL BUSINESS VOLUME
    # =================================================

    total_business_volume = Booking.objects.filter(
        agent=agent,
        status="CONFIRMED"
    ).aggregate(
        total=models.Sum("total_price")
    )["total"] or 0

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        "agent": agent,

        "wallet": wallet,

        "topup_requests": topup_requests,

        # Used by Recent Ledger Activity
        "transactions": all_transactions,

        # Used by filtered Account Statement
        "statement_transactions": statement_transactions,

        "date_from": date_from,

        "date_to": date_to,

        "opening_balance": opening_balance,

        "total_credits": total_credits,

        "total_debits": total_debits,

        "closing_balance": closing_balance,

        "total_business_volume": total_business_volume,

    }

    return render(
        request,
        "wallet.html",
        context
    )
# =====================================================
# ADMIN - GROUP BOOKING DETAIL
# =====================================================

@login_required(login_url="login")
def admin_group_booking_detail(request, booking_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access this group booking."
        )

        return redirect("login")

    group_booking = get_object_or_404(

        GroupBooking.objects.select_related(
            "agent",
            "group_ticket",
            "group_ticket__airline",
            "group_ticket__departure_airport",
            "group_ticket__arrival_airport",
            "passenger"
        ),

        id=booking_id
    )

    # =================================================
    # CHECK 2-HOUR EXPIRY
    # =================================================

    if (
        group_booking.status == "CONFIRMED"
        and group_booking.expires_at
        and timezone.now() >= group_booking.expires_at
    ):

        group_booking.status = "EXPIRED"

        group_booking.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )

    return render(
        request,
        "admin_group_booking_detail.html",
        {
            "booking": group_booking
        }
    )



# =====================================================
# ADMIN - CONFIRM GROUP BOOKING
# =====================================================

@login_required(login_url="login")
def confirm_group_booking(request, booking_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to confirm group bookings."
        )

        return redirect("login")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_group_booking_detail",
            booking_id=booking_id
        )

    # =================================================
    # DATABASE TRANSACTION
    # =================================================

    with transaction.atomic():

        group_booking = get_object_or_404(
            GroupBooking,
            id=booking_id
        )

        # =================================================
        # CHECK CURRENT STATUS
        # =================================================

        if group_booking.status != "PENDING":

            messages.warning(
                request,
                "This group booking cannot be confirmed."
            )

            return redirect(
                "admin_group_booking_detail",
                booking_id=group_booking.id
            )

        # =================================================
        # GENERATE UNIQUE 6-CHARACTER PNR
        # 2 uppercase letters + 4 numbers
        # Example: AK2715
        # =================================================

        while True:

            letters = get_random_string(
                2,
                allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )

            numbers = get_random_string(
                4,
                allowed_chars="0123456789"
            )

            pnr = letters + numbers

            normal_pnr_exists = Booking.objects.filter(
                pnr=pnr
            ).exists()

            group_pnr_exists = GroupBooking.objects.filter(
                pnr=pnr
            ).exists()

            if not normal_pnr_exists and not group_pnr_exists:

                break

        # =================================================
        # GENERATE UNIQUE TICKET NUMBER
        # =================================================

        while True:

            ticket_number = (
                "220"
                + get_random_string(
                    10,
                    allowed_chars="0123456789"
                )
            )

            normal_ticket_exists = Booking.objects.filter(
                ticket_number=ticket_number
            ).exists()

            group_ticket_exists = GroupBooking.objects.filter(
                ticket_number=ticket_number
            ).exists()

            if not normal_ticket_exists and not group_ticket_exists:

                break

        # =================================================
        # CONFIRMATION TIME
        # =================================================

        confirmed_at = timezone.now()

        # =================================================
        # EXPIRY TIME
        # EXPIRES 2 HOURS AFTER ADMIN CONFIRMATION
        # =================================================

        expires_at = confirmed_at + timedelta(
            hours=2
        )

        # =================================================
        # CONFIRM GROUP BOOKING
        # =================================================

        group_booking.status = "CONFIRMED"

        group_booking.pnr = pnr

        group_booking.ticket_number = ticket_number

        group_booking.confirmed_at = confirmed_at

        group_booking.expires_at = expires_at

        group_booking.save(
            update_fields=[
                "status",
                "pnr",
                "ticket_number",
                "confirmed_at",
                "expires_at",
                "updated_at"
            ]
        )

    # =================================================
    # SUCCESS MESSAGE
    # =================================================

    messages.success(
        request,
        (
            f"Group booking {group_booking.booking_reference} "
            f"has been confirmed successfully. "
            f"PNR: {pnr} | "
            f"Ticket No: {ticket_number}"
        )
    )

    return redirect(
        "admin_group_booking_detail",
        booking_id=group_booking.id
    )

# =====================================================
# ADMIN - REJECT GROUP BOOKING
# =====================================================

@login_required(login_url="login")
def reject_group_booking(request, booking_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to reject group bookings."
        )

        return redirect("login")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_group_booking_detail",
            booking_id=booking_id
        )

    group_booking = get_object_or_404(
        GroupBooking.objects.select_related(
            "group_ticket"
        ),
        id=booking_id
    )

    # =================================================
    # CHECK CURRENT STATUS
    # =================================================

    if group_booking.status != "PENDING":

        messages.warning(
            request,
            "This group booking cannot be rejected."
        )

        return redirect(
            "admin_group_booking_detail",
            booking_id=group_booking.id
        )

    # =================================================
    # REJECTION REASON
    # =================================================

    reason = request.POST.get(
        "rejection_reason",
        ""
    ).strip()

    if not reason:

        messages.error(
            request,
            "Please provide a rejection reason."
        )

        return redirect(
            "admin_group_booking_detail",
            booking_id=group_booking.id
        )

    # =================================================
    # DATABASE TRANSACTION
    # =================================================

    with transaction.atomic():

        group_booking = GroupBooking.objects.select_for_update().select_related(
            "group_ticket"
        ).get(
            id=booking_id
        )

        if group_booking.status != "PENDING":

            messages.warning(
                request,
                "This group booking has already been processed."
            )

            return redirect(
                "admin_group_booking_detail",
                booking_id=group_booking.id
            )

        # -------------------------------------------------
        # RETURN SEATS TO GROUP TICKET
        # -------------------------------------------------

        group_ticket = GroupTicket.objects.select_for_update().get(
            id=group_booking.group_ticket_id
        )

        group_ticket.available_seats += group_booking.seats_booked

        # Safety: never allow available seats to exceed total seats

        if group_ticket.available_seats > group_ticket.total_seats:

            group_ticket.available_seats = group_ticket.total_seats

        group_ticket.save(
            update_fields=[
                "available_seats"
            ]
        )

        # -------------------------------------------------
        # REJECT BOOKING
        # -------------------------------------------------

        group_booking.status = "REJECTED"

        group_booking.rejection_reason = reason

        group_booking.save(
            update_fields=[
                "status",
                "rejection_reason",
                "updated_at"
            ]
        )

    messages.success(
        request,
        f"Group booking {group_booking.booking_reference} has been rejected."
    )

    return redirect(
        "admin_group_booking_detail",
        booking_id=group_booking.id
    )
# =====================================================
# AGENT - VIEW GROUP TICKET
# =====================================================

# =====================================================
# AGENT - GROUP VIEW TICKET
# =====================================================

@login_required(login_url="login")
def agent_group_view_ticket(request, booking_id):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    group_booking = get_object_or_404(
        GroupBooking.objects.select_related(
            "agent",
            "group_ticket",
            "group_ticket__airline",
            "group_ticket__departure_airport",
            "group_ticket__arrival_airport",
            "passenger"
        ),
        id=booking_id,
        agent=agent,
        status="CONFIRMED"
    )

    return render(
        request,
        "agent/group-view-ticket.html",
        {
            "agent": agent,
            "booking": group_booking,
        }
    )
# =====================================================
# AGENT - AGENCY PROFILE
# =====================================================

@login_required(login_url="login")
def agency_profile(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    if request.method == "POST":

        agency = request.POST.get(
            "agency",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        # -------------------------------------------------
        # UPDATE BASIC INFORMATION
        # -------------------------------------------------

        if agency:
            agent.agency = agency

        if email:
            agent.email = email

        if phone:
            agent.phone = phone

        # -------------------------------------------------
        # UPDATE LOGO
        # -------------------------------------------------

        if request.FILES.get("agency_logo"):

            agent.agency_logo = request.FILES[
                "agency_logo"
            ]

        agent.save()

        messages.success(
            request,
            "Agency profile updated successfully."
        )

        return redirect(
            "agency_profile"
        )

    return render(
        request,
        "agent/agency-profile.html",
        {
            "agent": agent
        }
    )
# =====================================================
# AGENT - BANKING
# =====================================================

@login_required(login_url="login")
def agent_banking(request):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    return render(
        request,
        "agent/banking.html",
        {
            "agent": agent
        }
    )

# =====================================================
# ADMIN - APPROVE WALLET TOP-UP
# =====================================================

# =====================================================
# ADMIN - APPROVE WALLET TOP-UP
# =====================================================

@login_required(login_url="login")
def admin_approve_topup(request, topup_id):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to approve wallet top-ups."
        )

        return redirect("login")

    # =================================================
    # ONLY POST ALLOWED
    # =================================================

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_wallet_requests"
        )

    # =================================================
    # DATABASE TRANSACTION
    # =================================================

    with transaction.atomic():

        # -------------------------------------------------
        # GET AND LOCK TOP-UP REQUEST
        # -------------------------------------------------

        topup = get_object_or_404(
            TopUpRequest.objects.select_for_update().select_related(
                "agent"
            ),
            id=topup_id
        )

        # -------------------------------------------------
        # CHECK STATUS
        # -------------------------------------------------

        if topup.status != "PENDING":

            messages.warning(
                request,
                "This top-up request has already been processed."
            )

            return redirect(
                "admin_wallet_request_detail",
                topup_id=topup.id
            )

        # -------------------------------------------------
        # GET / LOCK AGENT WALLET
        # -------------------------------------------------

        wallet, created = AgentWallet.objects.select_for_update().get_or_create(
            agent=topup.agent
        )

        # -------------------------------------------------
        # ADD MONEY TO WALLET
        # -------------------------------------------------

        wallet.balance += topup.amount

        wallet.total_deposited += topup.amount

        wallet.save(
            update_fields=[
                "balance",
                "total_deposited",
                "updated_at"
            ]
        )

        # -------------------------------------------------
        # CREATE WALLET TRANSACTION
        # -------------------------------------------------

        WalletTransaction.objects.create(

            agent=topup.agent,

            reference=f"TOPUP-{topup.id}",

            description="Wallet top-up approved",

            transaction_type="CREDIT",

            debit=0,

            credit=topup.amount,

            balance_after=wallet.balance
        )

        # -------------------------------------------------
        # UPDATE TOP-UP REQUEST
        # -------------------------------------------------

        topup.status = "APPROVED"

        topup.reviewed_at = timezone.now()

        topup.admin_note = (
            f"Top-up of PKR {topup.amount:,.0f} "
            f"approved successfully."
        )

        topup.save(
            update_fields=[
                "status",
                "reviewed_at",
                "admin_note"
            ]
        )

    # =================================================
    # SUCCESS MESSAGE
    # =================================================

    messages.success(
        request,
        (
            f"Top-up of PKR {topup.amount:,.0f} "
            f"for {topup.agent.agency} "
            f"has been approved successfully."
        )
    )

    # =================================================
    # RETURN TO DETAIL PAGE
    # =================================================

    return redirect(
        "admin_wallet_request_detail",
        topup_id=topup.id
    )


# =====================================================
# ADMIN - REJECT WALLET TOP-UP
# =====================================================

@login_required(login_url="login")
def admin_reject_topup(request, topup_id):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to reject wallet top-ups."
        )

        return redirect("login")

    # =================================================
    # ONLY POST ALLOWED
    # =================================================

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_wallet_requests"
        )

    # =================================================
    # GET TOP-UP REQUEST
    # =================================================

    topup = get_object_or_404(
        TopUpRequest,
        id=topup_id
    )

    # =================================================
    # CHECK STATUS
    # =================================================

    if topup.status != "PENDING":

        messages.warning(
            request,
            "This top-up request has already been processed."
        )

        return redirect(
            "admin_wallet_request_detail",
            topup_id=topup.id
        )

    # =================================================
    # REJECT TOP-UP
    # =================================================

    topup.status = "REJECTED"

    topup.reviewed_at = timezone.now()

    topup.admin_note = (
        f"Top-up of PKR {topup.amount:,.0f} "
        f"was rejected."
    )

    topup.save(
        update_fields=[
            "status",
            "reviewed_at",
            "admin_note"
        ]
    )

    # =================================================
    # SUCCESS MESSAGE
    # =================================================

    messages.warning(
        request,
        (
            f"Top-up request of PKR {topup.amount:,.0f} "
            f"from {topup.agent.agency} "
            f"has been rejected."
        )
    )

    # =================================================
    # RETURN TO DETAIL PAGE
    # =================================================

    return redirect(
        "admin_wallet_request_detail",
        topup_id=topup.id
    )


# =====================================================
# ADMIN - WALLET TOP-UP REQUESTS
# =====================================================

# =====================================================
# ADMIN - WALLET TOP-UP REQUESTS + WALLET LEDGER
# =====================================================

# =====================================================
# ADMIN - WALLET TOP-UP REQUESTS
# =====================================================

@login_required(login_url="login")
def admin_wallet_requests(request):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access Wallet Requests."
        )

        return redirect("login")

    # =================================================
    # GET ALL TOP-UP REQUESTS
    # =================================================

    topup_requests = TopUpRequest.objects.select_related(
        "agent"
    ).order_by(
        "-created_at"
    )

    # =================================================
    # GET ALL WALLET TRANSACTIONS
    # =================================================

    wallet_transactions = WalletTransaction.objects.select_related(
        "agent"
    ).order_by(
        "-created_at"
    )

    # =================================================
    # ADMIN LEDGER FILTERS
    # =================================================

    date_from = request.GET.get(
        "date_from",
        ""
    ).strip()

    date_to = request.GET.get(
        "date_to",
        ""
    ).strip()

    # -------------------------------------------------
    # FILTER FROM DATE
    # -------------------------------------------------

    if date_from:

        wallet_transactions = wallet_transactions.filter(
            created_at__date__gte=date_from
        )

    # -------------------------------------------------
    # FILTER TO DATE
    # -------------------------------------------------

    if date_to:

        wallet_transactions = wallet_transactions.filter(
            created_at__date__lte=date_to
        )

    # =================================================
    # COUNTS
    # =================================================

    pending_count = TopUpRequest.objects.filter(
        status="PENDING"
    ).count()

    approved_count = TopUpRequest.objects.filter(
        status="APPROVED"
    ).count()

    rejected_count = TopUpRequest.objects.filter(
        status="REJECTED"
    ).count()

    total_count = TopUpRequest.objects.count()

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        "topup_requests": topup_requests,

        "pending_count": pending_count,

        "approved_count": approved_count,

        "rejected_count": rejected_count,

        "total_count": total_count,

        # -----------------------------
        # WALLET LEDGER
        # -----------------------------

        "wallet_transactions": wallet_transactions,

        # -----------------------------
        # FILTER VALUES
        # -----------------------------

        "date_from": date_from,

        "date_to": date_to,

    }

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "admin/wallet-requests.html",
        context
    )
# =====================================================
# ADMIN - WALLET TOP-UP REQUEST DETAIL
# =====================================================

@login_required(login_url="login")
def admin_wallet_request_detail(request, topup_id):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access Wallet Request details."
        )

        return redirect("login")

    # =================================================
    # GET TOP-UP REQUEST
    # =================================================

    topup = get_object_or_404(
        TopUpRequest.objects.select_related(
            "agent"
        ),
        id=topup_id
    )

    # =================================================
    # RENDER DETAIL PAGE
    # =================================================

    return render(
        request,
        "admin/wallet-request-detail.html",
        {
            "topup": topup
        }
    )

# =====================================================
# ADMIN - REJECT WALLET TOP-UP
# =====================================================

# =====================================================
# ADMIN - REJECT WALLET TOP-UP
# =====================================================

@login_required(login_url="login")
def admin_reject_topup(request, topup_id):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to reject wallet top-ups."
        )

        return redirect("login")

    # =================================================
    # ONLY POST REQUEST ALLOWED
    # =================================================

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_wallet_requests"
        )

    # =================================================
    # GET TOP-UP REQUEST
    # =================================================

    topup = get_object_or_404(
        TopUpRequest.objects.select_related(
            "agent"
        ),
        id=topup_id
    )

    # =================================================
    # CHECK CURRENT STATUS
    # =================================================

    if topup.status != "PENDING":

        messages.warning(
            request,
            "This top-up request has already been processed."
        )

        return redirect(
            "admin_wallet_request_detail",
            topup_id=topup.id
        )

    # =================================================
    # REJECT TOP-UP
    # =================================================

    topup.status = "REJECTED"

    topup.reviewed_at = timezone.now()

    topup.admin_note = (
        f"Top-up of PKR {topup.amount:,.0f} "
        f"was rejected."
    )

    topup.save(
        update_fields=[
            "status",
            "reviewed_at",
            "admin_note"
        ]
    )

    # =================================================
    # SUCCESS MESSAGE
    # =================================================

    messages.warning(
        request,
        (
            f"Top-up request of PKR {topup.amount:,.0f} "
            f"from {topup.agent.agency} "
            f"has been rejected."
        )
    )

    # =================================================
    # RETURN TO DETAIL PAGE
    # =================================================

    return redirect(
        "admin_wallet_request_detail",
        topup_id=topup.id
    )
# =====================================================
# ADMIN - WALLET TOP-UP REQUESTS
# =====================================================

# =====================================================
# ADMIN - WALLET TOP-UP REQUESTS
# =====================================================

@login_required(login_url="login")
def admin_wallet_requests(request):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access Wallet Requests."
        )

        return redirect("login")

    # =================================================
    # GET ALL TOP-UP REQUESTS
    # =================================================

    topup_requests = TopUpRequest.objects.select_related(
        "agent"
    ).order_by(
        "-created_at"
    )

    # =================================================
    # GET ALL WALLET TRANSACTIONS
    # =================================================

    wallet_transactions = WalletTransaction.objects.select_related(
        "agent"
    ).order_by(
        "-created_at"
    )

    # =================================================
    # COUNTS
    # =================================================

    pending_count = TopUpRequest.objects.filter(
        status="PENDING"
    ).count()

    approved_count = TopUpRequest.objects.filter(
        status="APPROVED"
    ).count()

    rejected_count = TopUpRequest.objects.filter(
        status="REJECTED"
    ).count()

    total_count = TopUpRequest.objects.count()

    wallet_transaction_count = wallet_transactions.count()

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        "topup_requests": topup_requests,

        "pending_count": pending_count,

        "approved_count": approved_count,

        "rejected_count": rejected_count,

        "total_count": total_count,

        "wallet_transactions": wallet_transactions,

        "wallet_transaction_count": wallet_transaction_count,

    }

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "admin/wallet-requests.html",
        context
    )
# =====================================================
# ADMIN - WALLET TOP-UP REQUEST DETAIL
# =====================================================

@login_required(login_url="login")
def admin_wallet_request_detail(request, topup_id):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access Wallet Request details."
        )

        return redirect("login")

    topup = get_object_or_404(
        TopUpRequest.objects.select_related(
            "agent"
        ),
        id=topup_id
    )

    return render(
        request,
        "admin/wallet-request-detail.html",
        {
            "topup": topup
        }
    )
# =====================================================
# AGENT - EXPORT WALLET STATEMENT TO EXCEL
# =====================================================

@login_required(login_url="login")
def export_wallet_excel(request):

    # =================================================
    # GET LOGGED-IN AGENT
    # =================================================

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # GET DATE FILTERS
    # =================================================

    date_from = request.GET.get(
        "date_from",
        ""
    ).strip()

    date_to = request.GET.get(
        "date_to",
        ""
    ).strip()

    # =================================================
    # GET TRANSACTIONS
    # =================================================

    statement_transactions = WalletTransaction.objects.filter(
        agent=agent
    ).order_by(
        "created_at"
    )

    # =================================================
    # APPLY DATE FILTER - FROM
    # =================================================

    if date_from:

        statement_transactions = statement_transactions.filter(
            created_at__date__gte=date_from
        )

    # =================================================
    # APPLY DATE FILTER - TO
    # =================================================

    if date_to:

        statement_transactions = statement_transactions.filter(
            created_at__date__lte=date_to
        )

    # =================================================
    # CREATE EXCEL WORKBOOK
    # =================================================

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Wallet Statement"

    # =================================================
    # TITLE
    # =================================================

    worksheet["A1"] = "AL NAJAM Travel & Tours"
    worksheet["A1"].font = Font(
        bold=True,
        size=16
    )

    worksheet.merge_cells(
        "A1:F1"
    )

    worksheet["A2"] = "Agent Wallet Statement"

    worksheet["A2"].font = Font(
        bold=True,
        size=12
    )

    worksheet.merge_cells(
        "A2:F2"
    )

    worksheet["A3"] = (
        f"Agent: {agent.name} | "
        f"Agency: {agent.agency}"
    )

    worksheet.merge_cells(
        "A3:F3"
    )

    # =================================================
    # DATE RANGE
    # =================================================

    date_range_text = "All Transactions"

    if date_from and date_to:

        date_range_text = (
            f"From {date_from} To {date_to}"
        )

    elif date_from:

        date_range_text = (
            f"From {date_from}"
        )

    elif date_to:

        date_range_text = (
            f"Up To {date_to}"
        )

    worksheet["A4"] = date_range_text

    worksheet.merge_cells(
        "A4:F4"
    )

    # =================================================
    # TABLE HEADERS
    # =================================================

    headers = [

        "Date",
        "Reference",
        "Description",
        "Debit (PKR)",
        "Credit (PKR)",
        "Balance (PKR)",

    ]

    header_row = 6

    for column_number, header in enumerate(
        headers,
        start=1
    ):

        cell = worksheet.cell(
            row=header_row,
            column=column_number
        )

        cell.value = header

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="172033"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    # =================================================
    # TRANSACTION DATA
    # =================================================

    current_row = header_row + 1

    for transaction in statement_transactions:

        worksheet.cell(
            row=current_row,
            column=1
        ).value = transaction.created_at.strftime(
            "%d %b %Y"
        )

        worksheet.cell(
            row=current_row,
            column=2
        ).value = transaction.reference

        worksheet.cell(
            row=current_row,
            column=3
        ).value = transaction.description

        worksheet.cell(
            row=current_row,
            column=4
        ).value = float(
            transaction.debit or 0
        )

        worksheet.cell(
            row=current_row,
            column=5
        ).value = float(
            transaction.credit or 0
        )

        worksheet.cell(
            row=current_row,
            column=6
        ).value = float(
            transaction.balance_after or 0
        )

        current_row += 1

    # =================================================
    # NUMBER FORMATTING
    # =================================================

    for row in worksheet.iter_rows(
        min_row=header_row + 1,
        min_col=4,
        max_col=6
    ):

        for cell in row:

            cell.number_format = '#,##0.00'

    # =================================================
    # COLUMN WIDTHS
    # =================================================

    column_widths = {

        "A": 16,
        "B": 20,
        "C": 32,
        "D": 18,
        "E": 18,
        "F": 20,

    }

    for column, width in column_widths.items():

        worksheet.column_dimensions[
            column
        ].width = width

    # =================================================
    # FREEZE HEADER
    # =================================================

    worksheet.freeze_panes = "A7"

    # =================================================
    # CREATE RESPONSE
    # =================================================

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="AL_NAJAM_Wallet_Statement.xlsx"'
    )

    workbook.save(
        response
    )

    return response
# =====================================================
# AGENT - EXPORT WALLET STATEMENT TO PDF
# =====================================================

@login_required(login_url="login")
def export_wallet_pdf(request):

    # =================================================
    # GET LOGGED-IN AGENT
    # =================================================

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =================================================
    # GET DATE FILTERS
    # =================================================

    date_from = request.GET.get(
        "date_from",
        ""
    ).strip()

    date_to = request.GET.get(
        "date_to",
        ""
    ).strip()

    # =================================================
    # GET TRANSACTIONS
    # =================================================

    statement_transactions = WalletTransaction.objects.filter(
        agent=agent
    ).order_by(
        "created_at"
    )

    # =================================================
    # APPLY FROM DATE
    # =================================================

    if date_from:

        statement_transactions = statement_transactions.filter(
            created_at__date__gte=date_from
        )

    # =================================================
    # APPLY TO DATE
    # =================================================

    if date_to:

        statement_transactions = statement_transactions.filter(
            created_at__date__lte=date_to
        )

    # =================================================
    # CREATE PDF BUFFER
    # =================================================

    buffer = BytesIO()

    document = SimpleDocTemplate(

        buffer,

        pagesize=landscape(A4),

        rightMargin=15 * mm,

        leftMargin=15 * mm,

        topMargin=15 * mm,

        bottomMargin=15 * mm,

    )

    # =================================================
    # STYLES
    # =================================================

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(

        "WalletTitle",

        parent=styles["Title"],

        fontName="Helvetica-Bold",

        fontSize=18,

        leading=22,

        alignment=TA_CENTER,

        textColor=colors.HexColor("#172033"),

        spaceAfter=6,

    )

    subtitle_style = ParagraphStyle(

        "WalletSubtitle",

        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=9,

        leading=12,

        alignment=TA_CENTER,

        textColor=colors.HexColor("#758197"),

        spaceAfter=4,

    )

    section_style = ParagraphStyle(

        "Section",

        parent=styles["Normal"],

        fontName="Helvetica-Bold",

        fontSize=10,

        textColor=colors.HexColor("#172033"),

        alignment=TA_LEFT,

    )

    normal_style = ParagraphStyle(

        "NormalSmall",

        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=8,

        leading=10,

        textColor=colors.HexColor("#4f5d73"),

    )

    # =================================================
    # DOCUMENT CONTENT
    # =================================================

    elements = []

    elements.append(
        Paragraph(
            "AL NAJAM TRAVEL & TOURS",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Agent Wallet Statement",
            subtitle_style
        )
    )

    elements.append(
        Paragraph(
            f"Agent: {agent.name} | Agency: {agent.agency}",
            subtitle_style
        )
    )

    # =================================================
    # DATE RANGE TEXT
    # =================================================

    if date_from and date_to:

        date_text = (
            f"Statement Period: {date_from} to {date_to}"
        )

    elif date_from:

        date_text = (
            f"Statement Period: From {date_from}"
        )

    elif date_to:

        date_text = (
            f"Statement Period: Up to {date_to}"
        )

    else:

        date_text = "Statement Period: All Transactions"

    elements.append(
        Paragraph(
            date_text,
            subtitle_style
        )
    )

    elements.append(
        Spacer(
            1,
            8
        )
    )

    # =================================================
    # TRANSACTION TABLE
    # =================================================

    table_data = [

        [
            "Date",
            "Reference",
            "Description",
            "Debit (PKR)",
            "Credit (PKR)",
            "Balance (PKR)",
        ]

    ]

    for transaction in statement_transactions:

        table_data.append(

            [

                transaction.created_at.strftime(
                    "%d %b %Y"
                ),

                transaction.reference,

                transaction.description,

                f"{transaction.debit:,.2f}"
                if transaction.debit
                else "—",

                f"{transaction.credit:,.2f}"
                if transaction.credit
                else "—",

                f"{transaction.balance_after:,.2f}",

            ]

        )

    if len(table_data) == 1:

        table_data.append(

            [

                "—",

                "—",

                "No transactions recorded",

                "—",

                "—",

                "—",

            ]

        )

    transaction_table = Table(

        table_data,

        colWidths=[

            28 * mm,
            35 * mm,
            78 * mm,
            32 * mm,
            32 * mm,
            38 * mm,

        ],

        repeatRows=1,

    )

    transaction_table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#172033")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, 0),
                    8
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, 0),
                    "CENTER"
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica"
                ),

                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, -1),
                    7
                ),

                (
                    "TEXTCOLOR",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor("#4f5d73")
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#dfe4ea")
                ),

                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#f8fafc")
                    ]
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "ALIGN",
                    (3, 1),
                    (5, -1),
                    "RIGHT"
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),

            ]

        )

    )

    elements.append(
        transaction_table
    )

    elements.append(
        Spacer(
            1,
            12
        )
    )

    # =================================================
    # CLOSING BALANCE
    # =================================================

    if statement_transactions.exists():

        closing_balance = (
            statement_transactions
            .order_by("-created_at")
            .first()
            .balance_after
        )

    else:

        closing_balance = 0

    closing_data = [

        [

            Paragraph(
                "<b>CLOSING BALANCE</b>",
                normal_style
            ),

            Paragraph(
                f"<b>PKR {closing_balance:,.2f}</b>",
                normal_style
            ),

            Paragraph(
                "<b>STATEMENT STATUS</b>",
                normal_style
            ),

            Paragraph(
                f"<b>{statement_transactions.count()} transaction(s) recorded</b>",
                normal_style
            ),

        ]

    ]

    closing_table = Table(

        closing_data,

        colWidths=[

            42 * mm,
            55 * mm,
            45 * mm,
            55 * mm,

        ]

    )

    closing_table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#eef2f7")
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#d7dde6")
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.HexColor("#e1e6ed")
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),

            ]

        )

    )

    elements.append(
        closing_table
    )

    elements.append(
        Spacer(
            1,
            10
        )
    )

    elements.append(

        Paragraph(

            "Generated by AL NAJAM Travel & Tours Agent Portal",

            subtitle_style

        )

    )

    # =================================================
    # BUILD PDF
    # =================================================

    document.build(
        elements
    )

    # =================================================
    # RESPONSE
    # =================================================

    buffer.seek(0)

    response = HttpResponse(

        buffer.getvalue(),

        content_type="application/pdf"

    )

    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="AL_NAJAM_Wallet_Statement.pdf"'
    )

    return response
# =====================================================
# ADMIN - AGENT WALLET STATEMENT
# =====================================================

@login_required(login_url="login")
def admin_agent_wallet_statement(request, agent_id):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access agent wallet statements."
        )

        return redirect("login")

    # =================================================
    # GET AGENT
    # =================================================

    agent = get_object_or_404(
        Agent,
        id=agent_id
    )

    # =================================================
    # GET / CREATE WALLET
    # =================================================

    wallet, created = AgentWallet.objects.get_or_create(
        agent=agent
    )

    # =================================================
    # DATE FILTERS
    # =================================================

    date_from = request.GET.get(
        "date_from",
        ""
    ).strip()

    date_to = request.GET.get(
        "date_to",
        ""
    ).strip()

    # =================================================
    # BASE TRANSACTIONS
    # =================================================

    transactions = WalletTransaction.objects.filter(
        agent=agent
    ).order_by(
        "created_at"
    )

    # =================================================
    # OPENING BALANCE
    # =================================================

    opening_balance = 0

    if date_from:

        transactions_before = WalletTransaction.objects.filter(
            agent=agent,
            created_at__date__lt=date_from
        ).order_by(
            "-created_at"
        )

        previous_transaction = transactions_before.first()

        if previous_transaction:

            opening_balance = previous_transaction.balance_after

    # =================================================
    # APPLY FROM DATE
    # =================================================

    if date_from:

        transactions = transactions.filter(
            created_at__date__gte=date_from
        )

    # =================================================
    # APPLY TO DATE
    # =================================================

    if date_to:

        transactions = transactions.filter(
            created_at__date__lte=date_to
        )

    # =================================================
    # CLOSING BALANCE
    # =================================================

    last_transaction = transactions.last()

    if last_transaction:

        closing_balance = last_transaction.balance_after

    elif date_from or date_to:

        closing_balance = opening_balance

    else:

        closing_balance = wallet.balance

    # =================================================
    # TOTAL CREDIT
    # =================================================

    total_credit = transactions.aggregate(
        total=models.Sum("credit")
    )["total"] or 0

    # =================================================
    # TOTAL DEBIT
    # =================================================

    total_debit = transactions.aggregate(
        total=models.Sum("debit")
    )["total"] or 0

    # =================================================
    # TRANSACTION COUNT
    # =================================================

    transaction_count = transactions.count()

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        "agent": agent,

        "wallet": wallet,

        "transactions": transactions,

        "date_from": date_from,

        "date_to": date_to,

        "opening_balance": opening_balance,

        "closing_balance": closing_balance,

        "total_credit": total_credit,

        "total_debit": total_debit,

        "transaction_count": transaction_count,

    }

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "admin/agent-wallet-statement.html",
        context
    )
# =====================================================
# ADMIN - AGENT WALLET STATEMENT - EXCEL EXPORT
# =====================================================

@login_required(login_url="login")
def admin_agent_wallet_statement_excel(request, agent_id):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to export agent wallet statements."
        )

        return redirect("login")

    # =================================================
    # IMPORT EXCEL TOOLS
    # =================================================

    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from django.http import HttpResponse

    # =================================================
    # GET AGENT
    # =================================================

    agent = get_object_or_404(
        Agent,
        id=agent_id
    )

    # =================================================
    # DATE FILTERS
    # =================================================

    date_from = request.GET.get(
        "date_from",
        ""
    ).strip()

    date_to = request.GET.get(
        "date_to",
        ""
    ).strip()

    # =================================================
    # GET TRANSACTIONS
    # =================================================

    transactions = WalletTransaction.objects.filter(
        agent=agent
    ).order_by(
        "created_at"
    )

    # =================================================
    # APPLY DATE FILTER
    # =================================================

    if date_from:

        transactions = transactions.filter(
            created_at__date__gte=date_from
        )

    if date_to:

        transactions = transactions.filter(
            created_at__date__lte=date_to
        )

    # =================================================
    # CREATE WORKBOOK
    # =================================================

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Wallet Statement"

    # =================================================
    # TITLE
    # =================================================

    worksheet["A1"] = "AL NAJAM TRAVEL & TOURS"

    worksheet["A1"].font = Font(
        bold=True,
        size=16
    )

    worksheet.merge_cells(
        "A1:H1"
    )

    worksheet["A2"] = "Agent Wallet Statement"

    worksheet["A2"].font = Font(
        bold=True,
        size=13
    )

    worksheet.merge_cells(
        "A2:H2"
    )

    worksheet["A3"] = f"Agent: {agent.name}"

    worksheet["A4"] = f"Agency: {agent.agency}"

    worksheet["A5"] = (
        f"Date From: {date_from or 'All'}"
    )

    worksheet["A6"] = (
        f"Date To: {date_to or 'All'}"
    )

    # =================================================
    # HEADER
    # =================================================

    header_row = 8

    headers = [

        "Date",

        "Reference",

        "Description",

        "Type",

        "Debit (PKR)",

        "Credit (PKR)",

        "Balance After (PKR)",

    ]

    for column, header in enumerate(
        headers,
        start=1
    ):

        cell = worksheet.cell(
            row=header_row,
            column=column
        )

        cell.value = header

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            "solid",
            fgColor="F58220"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    # =================================================
    # TRANSACTIONS
    # =================================================

    row = header_row + 1

    for transaction in transactions:

        worksheet.cell(
            row=row,
            column=1
        ).value = transaction.created_at.strftime(
            "%d %b %Y %I:%M %p"
        )

        worksheet.cell(
            row=row,
            column=2
        ).value = transaction.reference

        worksheet.cell(
            row=row,
            column=3
        ).value = transaction.description

        worksheet.cell(
            row=row,
            column=4
        ).value = transaction.transaction_type

        worksheet.cell(
            row=row,
            column=5
        ).value = float(
            transaction.debit
        )

        worksheet.cell(
            row=row,
            column=6
        ).value = float(
            transaction.credit
        )

        worksheet.cell(
            row=row,
            column=7
        ).value = float(
            transaction.balance_after
        )

        row += 1

    # =================================================
    # COLUMN WIDTHS
    # =================================================

    worksheet.column_dimensions["A"].width = 24
    worksheet.column_dimensions["B"].width = 20
    worksheet.column_dimensions["C"].width = 32
    worksheet.column_dimensions["D"].width = 15
    worksheet.column_dimensions["E"].width = 18
    worksheet.column_dimensions["F"].width = 18
    worksheet.column_dimensions["G"].width = 22

    # =================================================
    # BORDERS
    # =================================================

    thin_border = Border(
        bottom=Side(
            style="thin",
            color="DDDDDD"
        )
    )

    for row_cells in worksheet.iter_rows(
        min_row=header_row,
        max_row=worksheet.max_row,
        min_col=1,
        max_col=7
    ):

        for cell in row_cells:

            cell.border = thin_border

    # =================================================
    # DOWNLOAD RESPONSE
    # =================================================

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="{agent.agency}_wallet_statement.xlsx"'
    )

    workbook.save(
        response
    )

    return response
# =====================================================
# ADMIN - AGENT WALLET STATEMENT PDF
# =====================================================

@login_required(login_url="login")
def admin_agent_wallet_statement_pdf(request, agent_id):

    # =================================================
    # ADMIN SECURITY CHECK
    # =================================================

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to export agent wallet statements."
        )

        return redirect("login")

    # =================================================
    # GET AGENT
    # =================================================

    agent = get_object_or_404(
        Agent,
        id=agent_id
    )

    # =================================================
    # GET WALLET
    # =================================================

    wallet, created = AgentWallet.objects.get_or_create(
        agent=agent
    )

    # =================================================
    # DATE FILTERS
    # =================================================

    date_from = request.GET.get(
        "date_from",
        ""
    ).strip()

    date_to = request.GET.get(
        "date_to",
        ""
    ).strip()

    # =================================================
    # GET TRANSACTIONS
    # =================================================

    transactions = WalletTransaction.objects.filter(
        agent=agent
    ).order_by(
        "created_at"
    )

    # =================================================
    # OPENING BALANCE
    # =================================================

    opening_balance = 0

    if date_from:

        transactions_before = WalletTransaction.objects.filter(
            agent=agent,
            created_at__date__lt=date_from
        ).order_by(
            "-created_at"
        )

        previous_transaction = transactions_before.first()

        if previous_transaction:

            opening_balance = previous_transaction.balance_after

    # =================================================
    # APPLY DATE FILTERS
    # =================================================

    if date_from:

        transactions = transactions.filter(
            created_at__date__gte=date_from
        )

    if date_to:

        transactions = transactions.filter(
            created_at__date__lte=date_to
        )

    # =================================================
    # CLOSING BALANCE
    # =================================================

    last_transaction = transactions.last()

    if last_transaction:

        closing_balance = last_transaction.balance_after

    elif date_from or date_to:

        closing_balance = opening_balance

    else:

        closing_balance = wallet.balance

    # =================================================
    # TOTAL CREDIT
    # =================================================

    total_credit = transactions.aggregate(
        total=models.Sum("credit")
    )["total"] or 0

    # =================================================
    # TOTAL DEBIT
    # =================================================

    total_debit = transactions.aggregate(
        total=models.Sum("debit")
    )["total"] or 0

    # =================================================
    # TRANSACTION COUNT
    # =================================================

    transaction_count = transactions.count()

    # =================================================
    # PDF TEMPLATE
    # =================================================

    html_string = render(
        request,
        "admin/agent-wallet-statement-pdf.html",
        {
            "agent": agent,
            "wallet": wallet,
            "transactions": transactions,
            "date_from": date_from,
            "date_to": date_to,
            "opening_balance": opening_balance,
            "closing_balance": closing_balance,
            "total_credit": total_credit,
            "total_debit": total_debit,
            "transaction_count": transaction_count,
        }
    ).content.decode("utf-8")

    # =================================================
    # GENERATE PDF
    # =================================================

    from xhtml2pdf import pisa
    from django.http import HttpResponse
    from io import BytesIO

    pdf_buffer = BytesIO()

    pdf_status = pisa.CreatePDF(
        html_string,
        dest=pdf_buffer
    )

    # =================================================
    # PDF ERROR
    # =================================================

    if pdf_status.err:

        messages.error(
            request,
            "Unable to generate the wallet statement PDF."
        )

        return redirect(
            "admin_agent_wallet_statement",
            agent_id=agent.id
        )

    # =================================================
    # RESPONSE
    # =================================================

    response = HttpResponse(
        pdf_buffer.getvalue(),
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="agent-wallet-statement-{agent.id}.pdf"'
    )

    return response

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Agent


@login_required
def agent_settings(request):

    agent = Agent.objects.filter(
        email=request.user.email
    ).first()

    if not agent:
        return redirect("agent_dashboard")

    return render(
        request,
        "agent-settings.html",
        {
            "agent": agent,
        }
    )

@login_required
def admin_umrah_packages(request):

    # Only superuser/admin can access
    if not request.user.is_superuser:
        return redirect("agent_dashboard")

    packages = (
        UmrahPackage.objects
        .select_related(
            "airline",
            "outbound_departure_airport",
            "outbound_arrival_airport",
            "return_departure_airport",
            "return_arrival_airport",
            "makkah_hotel",
            "madinah_hotel",
        )
        .order_by("-created_at")
    )

    # =========================================
    # PACKAGE STATISTICS
    # =========================================

    total_count = packages.count()

    active_count = packages.filter(
        status="ACTIVE"
    ).count()

    inactive_count = packages.filter(
        status="INACTIVE"
    ).count()

    sold_out_count = packages.filter(
        status="SOLD_OUT"
    ).count()

    # =========================================
    # PAGE
    # =========================================

    return render(
        request,
        "admin_umrah_packages.html",
        {
            "packages": packages,

            "total_count": total_count,
            "active_count": active_count,
            "inactive_count": inactive_count,
            "sold_out_count": sold_out_count,
        }
    )


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import UmrahPackage
from .forms import UmrahPackageForm
@login_required
def admin_create_umrah_package(request):

    # Only the main admin/superuser can create Umrah packages
    if not request.user.is_superuser:
        return redirect("agent_dashboard")

    if request.method == "POST":

        form = UmrahPackageForm(request.POST)

        if form.is_valid():

            package = form.save()

            messages.success(
                request,
                f"Umrah package '{package.name}' was created successfully."
            )

            return redirect("admin_umrah_packages")

    else:

        form = UmrahPackageForm()

    return render(
        request,
        "admin_create_umrah_package.html",
        {
            "form": form,
        }
    )
@login_required
def admin_umrah_package_detail(request, package_id):

    # Only the main admin/superuser can access
    if not request.user.is_superuser:
        return redirect("agent_dashboard")

    package = get_object_or_404(
        UmrahPackage.objects.select_related(
            "airline",
            "outbound_departure_airport",
            "outbound_arrival_airport",
            "return_departure_airport",
            "return_arrival_airport",
            "makkah_hotel",
            "madinah_hotel",
        ),
        id=package_id
    )

    return render(
        request,
        "admin_umrah_package_detail.html",
        {
            "package": package,
        }
    )
@login_required
def admin_edit_umrah_package(request, package_id):

    # Only the main admin/superuser can edit Umrah packages
    if not request.user.is_superuser:
        return redirect("agent_dashboard")

    package = get_object_or_404(
        UmrahPackage,
        id=package_id
    )

    if request.method == "POST":

        form = UmrahPackageForm(
            request.POST,
            instance=package
        )

        if form.is_valid():

            package = form.save()

            messages.success(
                request,
                f"Umrah package '{package.name}' was updated successfully."
            )

            return redirect(
                "admin_umrah_packages"
            )

    else:

        form = UmrahPackageForm(
            instance=package
        )

    return render(
        request,
        "admin_edit_umrah_package.html",
        {
            "form": form,
            "package": package,
        }
    )

# =====================================================
# AGENT - UMRAH PACKAGE DETAIL
# =====================================================

@login_required(login_url="login")
def agent_umrah_package_detail(
    request,
    package_id
):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    package = get_object_or_404(
        UmrahPackage.objects.select_related(
            "airline",
            "outbound_departure_airport",
            "outbound_arrival_airport",
            "return_departure_airport",
            "return_arrival_airport",
            "makkah_hotel",
            "madinah_hotel",
        ),
        id=package_id,
        status="ACTIVE"
    )

    return render(
        request,
        "agent/umrah-package-detail.html",
        {
            "agent": agent,
            "package": package,
        }
    )


# =====================================================
# AGENT - UMRAH PILGRIM DETAILS / CREATE BOOKING
# =====================================================

@login_required(login_url="login")
def agent_umrah_pilgrim_details(
    request,
    package_id
):

    # =====================================================
    # GET CURRENT AGENT
    # =====================================================

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    # =====================================================
    # GET ACTIVE PACKAGE
    # =====================================================

    package = get_object_or_404(
        UmrahPackage.objects.select_related(
            "airline",
            "outbound_departure_airport",
            "outbound_arrival_airport",
            "return_departure_airport",
            "return_arrival_airport",
            "makkah_hotel",
            "madinah_hotel",
        ),
        id=package_id,
        status="ACTIVE"
    )

    # =====================================================
    # CHECK AVAILABLE SEATS
    # =====================================================

    if package.available_seats <= 0:

        messages.error(
            request,
            "Sorry, this Umrah package is currently sold out."
        )

        return redirect(
            "agent_umrah_bookings"
        )

    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        pilgrims_count = request.POST.get(
            "pilgrims_count",
            "1"
        ).strip()

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        passport_number = request.POST.get(
            "passport_number",
            ""
        ).strip()

        date_of_birth = request.POST.get(
            "date_of_birth",
            ""
        ).strip()

        gender = request.POST.get(
            "gender",
            ""
        ).strip()

        nationality = request.POST.get(
            "nationality",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        # -------------------------------------------------
        # VALIDATE PILGRIM COUNT
        # -------------------------------------------------

        try:

            pilgrims_count = int(
                pilgrims_count
            )

        except (TypeError, ValueError):

            messages.error(
                request,
                "Please enter a valid number of pilgrims."
            )

            return render(
                request,
                "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        if pilgrims_count < 1:

            messages.error(
                request,
                "The number of pilgrims must be at least 1."
            )

            return render(
                request,
                "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        if pilgrims_count > package.available_seats:

            messages.error(
                request,
                f"Only {package.available_seats} seat(s) are available "
                f"for this package."
            )

            return render(
                request,
                "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        # -------------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # -------------------------------------------------

        if not first_name:

            messages.error(
                request,
                "First name is required."
            )

            return render(
                request,
              "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        if not last_name:

            messages.error(
                request,
                "Last name is required."
            )

            return render(
                request,
               "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        if not passport_number:

            messages.error(
                request,
                "Passport number is required."
            )

            return render(
                request,
              "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        if not date_of_birth:

            messages.error(
                request,
                "Date of birth is required."
            )

            return render(
                request,
               "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        if not gender:

            messages.error(
                request,
                "Please select gender."
            )

            return render(
                request,
               "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        if not nationality:

            nationality = "Pakistani"

        if not phone:

            messages.error(
                request,
                "Contact number is required."
            )

            return render(
                request,
                "agent/umrah-pilgrim-details.html",
                {
                    "agent": agent,
                    "package": package,
                }
            )

        # =================================================
        # CREATE LEAD PASSENGER
        # =================================================

        lead_passenger = Passenger.objects.create(

            first_name=first_name,

            last_name=last_name,

            passport_number=passport_number,

            date_of_birth=date_of_birth,

            gender=gender,

            nationality=nationality,

            phone=phone,

            email=email,

        )

        # =================================================
        # GENERATE UNIQUE BOOKING REFERENCE
        # =================================================

        while True:

            booking_reference = generate_unique_pnr()

            if not UmrahBooking.objects.filter(
                booking_reference=booking_reference
            ).exists():

                break

        # =================================================
        # CALCULATE TOTAL PRICE
        # =================================================

        total_price = (
            package.price *
            pilgrims_count
        )

        # =================================================
        # CREATE UMRAH BOOKING
        # =================================================

        booking = UmrahBooking.objects.create(

            booking_reference=booking_reference,

            agent=agent,

            package=package,

            lead_passenger=lead_passenger,

            pilgrims_count=pilgrims_count,

            total_price=total_price,

            status="PENDING",

        )

        # =================================================
        # ADD LEAD PASSENGER TO PILGRIMS
        # =================================================

        booking.pilgrims.add(
            lead_passenger
        )

        # =================================================
        # REDUCE AVAILABLE SEATS
        # =================================================

        package.available_seats -= pilgrims_count

        if package.available_seats < 0:

            package.available_seats = 0

        if package.available_seats == 0:

            package.status = "SOLD_OUT"

        package.save()

        # =================================================
        # SUCCESS MESSAGE
        # =================================================

        messages.success(
            request,
            f"Umrah booking {booking.booking_reference} "
            f"has been submitted successfully and is waiting for approval."
        )

        # =================================================
        # REDIRECT
        # =================================================

        return redirect(
            "agent_all_bookings"
        )

    # =====================================================
    # GET REQUEST
    # =====================================================

    return render(
        request,
      "agent/umrah-pilgrim-details.html",
        {
            "agent": agent,
            "package": package,
        }
    )


# =====================================================
# AGENT - UMRAH BOOKING CREATE
# =====================================================
#
# Kept so your existing URL named
# "agent_umrah_booking_create" continues to work.
# It sends the agent to the pilgrim details page.
# =====================================================

@login_required(login_url="login")
def agent_umrah_booking_create(
    request,
    package_id
):

    return redirect(
        "agent_umrah_pilgrim_details",
        package_id=package_id
    )


# =====================================================
# AGENT - UMRAH BOOKING SUCCESS
# =====================================================

@login_required(login_url="login")
def agent_umrah_booking_success(
    request,
    booking_id
):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    booking = get_object_or_404(
        UmrahBooking.objects.select_related(
            "agent",
            "package",
            "package__airline",
            "package__makkah_hotel",
            "package__madinah_hotel",
            "lead_passenger",
        ),
        id=booking_id,
        agent=agent
    )

    return render(
        request,
        "agent/umrah-booking-success.html",
        {
            "agent": agent,
            "booking": booking,
        }
    )


# =====================================================
# ADMIN - UMRAH BOOKINGS
# =====================================================

@login_required(login_url="login")
def admin_umrah_bookings(request):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access Umrah bookings."
        )

        return redirect(
            "login"
        )

    bookings = (
        UmrahBooking.objects
        .select_related(
            "agent",
            "package",
            "package__airline",
            "package__outbound_departure_airport",
            "package__outbound_arrival_airport",
            "package__makkah_hotel",
            "package__madinah_hotel",
            "lead_passenger",
        )
        .order_by("-booked_at")
    )

    pending_bookings = bookings.filter(
        status="PENDING"
    )

    confirmed_bookings = bookings.filter(
        status="CONFIRMED"
    )

    rejected_bookings = bookings.filter(
        status="REJECTED"
    )

    return render(
        request,
        "admin/umrah-bookings.html",
        {
            "bookings": bookings,
            "pending_bookings": pending_bookings,
            "confirmed_bookings": confirmed_bookings,
            "rejected_bookings": rejected_bookings,
        }
    )


# =====================================================
# ADMIN - UMRAH BOOKING DETAIL
# =====================================================

@login_required(login_url="login")
def admin_umrah_booking_detail(
    request,
    booking_id
):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to access this booking."
        )

        return redirect(
            "login"
        )

    booking = get_object_or_404(
        UmrahBooking.objects.select_related(
            "agent",
            "package",
            "package__airline",
            "package__outbound_departure_airport",
            "package__outbound_arrival_airport",
            "package__return_departure_airport",
            "package__return_arrival_airport",
            "package__makkah_hotel",
            "package__madinah_hotel",
            "lead_passenger",
        ),
        id=booking_id
    )

    return render(
        request,
        "admin/umrah-booking-detail.html",
        {
            "booking": booking,
        }
    )


# =====================================================
# ADMIN - APPROVE UMRAH BOOKING
# =====================================================

@login_required(login_url="login")
def admin_approve_umrah_booking(
    request,
    booking_id
):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to approve Umrah bookings."
        )

        return redirect(
            "login"
        )

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_umrah_booking_detail",
            booking_id=booking_id
        )

    booking = get_object_or_404(
        UmrahBooking,
        id=booking_id
    )

    if booking.status != "PENDING":

        messages.warning(
            request,
            "This Umrah booking has already been processed."
        )

        return redirect(
            "admin_umrah_booking_detail",
            booking_id=booking.id
        )

    now = timezone.now()

    booking.status = "CONFIRMED"

    booking.confirmed_at = now

    booking.expires_at = now + timedelta(
        hours=2
    )

    booking.rejection_reason = ""

    booking.save(
        update_fields=[
            "status",
            "confirmed_at",
            "expires_at",
            "rejection_reason",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Umrah booking {booking.booking_reference} "
        f"has been approved successfully."
    )

    return redirect(
        "admin_umrah_booking_detail",
        booking_id=booking.id
    )


# =====================================================
# ADMIN - REJECT UMRAH BOOKING
# =====================================================

@login_required(login_url="login")
def admin_reject_umrah_booking(
    request,
    booking_id
):

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to reject Umrah bookings."
        )

        return redirect(
            "login"
        )

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect(
            "admin_umrah_booking_detail",
            booking_id=booking_id
        )

    booking = get_object_or_404(
        UmrahBooking,
        id=booking_id
    )

    if booking.status != "PENDING":

        messages.warning(
            request,
            "This Umrah booking has already been processed."
        )

        return redirect(
            "admin_umrah_booking_detail",
            booking_id=booking.id
        )

    reason = request.POST.get(
        "rejection_reason",
        ""
    ).strip()

    if not reason:

        messages.error(
            request,
            "Please provide a rejection reason."
        )

        return redirect(
            "admin_umrah_booking_detail",
            booking_id=booking.id
        )

    booking.status = "REJECTED"

    booking.rejection_reason = reason

    booking.confirmed_at = None

    booking.expires_at = None

    booking.save(
        update_fields=[
            "status",
            "rejection_reason",
            "confirmed_at",
            "expires_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        f"Umrah booking {booking.booking_reference} "
        f"has been rejected."
    )

    return redirect(
        "admin_umrah_booking_detail",
        booking_id=booking.id
    )


# =====================================================
# AGENT - VIEW UMRAH TICKET
# =====================================================

@login_required(login_url="login")
def agent_umrah_view_ticket(
    request,
    booking_id
):

    agent = get_object_or_404(
        Agent,
        user=request.user
    )

    booking = get_object_or_404(
        UmrahBooking.objects.select_related(
            "agent",
            "package",
            "package__airline",
            "package__outbound_departure_airport",
            "package__outbound_arrival_airport",
            "package__return_departure_airport",
            "package__return_arrival_airport",
            "package__makkah_hotel",
            "package__madinah_hotel",
            "lead_passenger",
        ),
        id=booking_id,
        agent=agent
    )

    return render(
        request,
        "agent/umrah-ticket.html",
        {
            "agent": agent,
            "booking": booking,
        }
    )
# =====================================================
# GENERATE UNIQUE UMRAH PNR
# =====================================================

def generate_unique_pnr():

    while True:

        letters = ''.join(
            random.choices(
                string.ascii_uppercase,
                k=2
            )
        )

        numbers = ''.join(
            random.choices(
                string.digits,
                k=4
            )
        )

        pnr = letters + numbers

        if not UmrahBooking.objects.filter(
            booking_reference=pnr
        ).exists():

            return pnr