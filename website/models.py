from django.db import models
from django.contrib.auth.models import User


# =========================
# CONTACT MESSAGE
# =========================

class ContactMessage(models.Model):

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} - {self.email}"


# =========================
# AGENT
# =========================

# =========================
# AGENT
# =========================

class Agent(models.Model):

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        ("APPROVED", "Approved"),

        ("REJECTED", "Rejected"),

        ("SUSPENDED", "Suspended"),

    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="agent_profile",
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    agency = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=20
    )

    # =========================
    # AGENCY LOGO
    # =========================

    agency_logo = models.ImageField(
        upload_to="agency_logos/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.name} - {self.agency}"

# =========================
# AIRLINE
# =========================

class Airline(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=10,
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
    
        # =========================
    # AIRLINE LOGO
    # =========================

    logo = models.ImageField(
        upload_to="airlines/",
        blank=True,
        null=True
    )


# =========================
# AIRPORT
# =========================

class Airport(models.Model):

    code = models.CharField(
        max_length=3,
        unique=True
    )

    name = models.CharField(
        max_length=150
    )

    city = models.CharField(
        max_length=100
    )

    country = models.CharField(
        max_length=100
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.city} ({self.code})"

# =====================================================
# HOTEL
# =====================================================

class Hotel(models.Model):

    LOCATION_CHOICES = [

        ("MAKKAH", "Makkah"),

        ("MADINAH", "Madinah"),

    ]

    name = models.CharField(
        max_length=150
    )

    location = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES
    )

    distance_from_reference = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    image = models.ImageField(
        upload_to="umrah_hotels/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "location",
            "name"
        ]

    def __str__(self):

        return f"{self.name} - {self.get_location_display()}"

# =========================
# FLIGHT
# =========================

class Flight(models.Model):

    CATEGORY_CHOICES = [

        ("BAHRAIN", "Bahrain Oneway"),

        ("KSA", "KSA One Way"),

        ("OMAN", "Oman One Way"),

        ("UAE", "UAE Oneway"),

        ("UMRAH", "Umrah"),

    ]

    airline = models.ForeignKey(
        Airline,
        on_delete=models.CASCADE,
        related_name="flights"
    )

    flight_number = models.CharField(
        max_length=30
    )

    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_flights"
    )

    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_flights"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    departure_date = models.DateField()

    departure_time = models.TimeField()

    arrival_time = models.TimeField()

    baggage = models.CharField(
        max_length=50,
        default="20+7 KG"
    )

    meal = models.CharField(
        max_length=50,
        default="No"
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    total_seats = models.PositiveIntegerField(
        default=0
    )

    available_seats = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.airline.name} - "
            f"{self.flight_number} - "
            f"{self.departure_airport.code} "
            f"to "
            f"{self.arrival_airport.code}"
        )


# =====================================================
# UMRAH PACKAGE
# =====================================================

class UmrahPackage(models.Model):

    ROOM_TYPE_CHOICES = [

        ("SHARING", "Sharing"),

        ("QUAD", "Quad Sharing"),

        ("TRIPLE", "Triple"),

        ("DOUBLE", "Double"),

        ("SINGLE", "Single"),

    ]

    STATUS_CHOICES = [

        ("ACTIVE", "Active"),

        ("INACTIVE", "Inactive"),

        ("SOLD_OUT", "Sold Out"),

    ]

    # =================================================
    # PACKAGE INFORMATION
    # =================================================

    name = models.CharField(
        max_length=150,
        default="Umrah Package"
    )

    sector = models.CharField(
        max_length=50,
        default="LHE-JED-LHE"
    )

    nights_in_makkah = models.PositiveIntegerField(
        default=0
    )

    nights_in_madinah = models.PositiveIntegerField(
        default=0
    )

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default="SHARING"
    )

    # =================================================
    # AIRLINE
    # =================================================

    airline = models.ForeignKey(
        Airline,
        on_delete=models.PROTECT,
        related_name="umrah_packages",
        null=True,
        blank=True
    )

    # =================================================
    # OUTBOUND FLIGHT
    # =================================================

    outbound_departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="umrah_outbound_departures",
        null=True,
        blank=True
    )

    outbound_arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="umrah_outbound_arrivals",
        null=True,
        blank=True
    )

    outbound_flight_number = models.CharField(
        max_length=30,
        null=True,
        blank=True
    )

    outbound_departure_date = models.DateField(
        null=True,
        blank=True
    )

    outbound_departure_time = models.TimeField(
        null=True,
        blank=True
    )

    outbound_arrival_time = models.TimeField(
        null=True,
        blank=True
    )

    outbound_baggage = models.CharField(
        max_length=50,
        default="20+7 KG"
    )

    outbound_meal = models.CharField(
        max_length=50,
        default="No"
    )

    # =================================================
    # RETURN FLIGHT
    # =================================================

    return_departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="umrah_return_departures",
        null=True,
        blank=True
    )

    return_arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="umrah_return_arrivals",
        null=True,
        blank=True
    )

    return_flight_number = models.CharField(
        max_length=30,
        null=True,
        blank=True
    )

    return_departure_date = models.DateField(
        null=True,
        blank=True
    )

    return_departure_time = models.TimeField(
        null=True,
        blank=True
    )

    return_arrival_time = models.TimeField(
        null=True,
        blank=True
    )

    return_baggage = models.CharField(
        max_length=50,
        default="20+7 KG"
    )

    return_meal = models.CharField(
        max_length=50,
        default="No"
    )

    # =================================================
    # HOTELS
    # =================================================

    makkah_hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name="makkah_umrah_packages",
        limit_choices_to={
            "location": "MAKKAH",
            "is_active": True,
        }
    )

    madinah_hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name="madinah_umrah_packages",
        limit_choices_to={
            "location": "MADINAH",
            "is_active": True,
        }
    )

    # =================================================
    # PRICE
    # =================================================

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # =================================================
    # SEATS
    # =================================================

    total_seats = models.PositiveIntegerField(
        default=0
    )

    available_seats = models.PositiveIntegerField(
        default=0
    )

    # =================================================
    # STATUS
    # =================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    # =================================================
    # DESCRIPTION
    # =================================================

    description = models.TextField(
        blank=True
    )

    # =================================================
    # CREATED / UPDATED
    # =================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return (
            f"{self.name} - "
            f"{self.sector} - "
            f"PKR {self.price}"
        )


# =========================
# GROUP TICKET
# =========================

class GroupTicket(models.Model):

    CATEGORY_CHOICES = [

        ("BAHRAIN", "Bahrain Oneway"),

        ("KSA", "KSA One Way"),

        ("OMAN", "Oman One Way"),

        ("UAE", "UAE Oneway"),

        ("UMRAH", "Umrah"),

    ]

    airline = models.ForeignKey(
        Airline,
        on_delete=models.CASCADE,
        related_name="group_tickets"
    )

    flight_number = models.CharField(
        max_length=30
    )

    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="group_ticket_departures"
    )

    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="group_ticket_arrivals"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    departure_date = models.DateField()

    departure_time = models.TimeField()

    arrival_time = models.TimeField()

    baggage = models.CharField(
        max_length=50,
        default="20+7 KG"
    )

    meal = models.CharField(
        max_length=50,
        default="No"
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    total_seats = models.PositiveIntegerField(
        default=0
    )

    available_seats = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.airline.name} - "
            f"{self.flight_number} - "
            f"{self.departure_airport.code} "
            f"to "
            f"{self.arrival_airport.code}"
        )


# =========================
# PASSENGER
# =========================

class Passenger(models.Model):

    GENDER_CHOICES = [

        ("MALE", "Male"),

        ("FEMALE", "Female"),

        ("OTHER", "Other"),

    ]

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    passport_number = models.CharField(
        max_length=50
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    nationality = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.first_name} {self.last_name}"
# =====================================================
# UMRAH BOOKING
# =====================================================

class UmrahBooking(models.Model):

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        ("CONFIRMED", "Confirmed"),

        ("REJECTED", "Rejected"),

        ("CANCELLED", "Cancelled"),

        ("COMPLETED", "Completed"),

        ("EXPIRED", "Expired"),

    ]

    # =================================================
    # BOOKING REFERENCE
    # =================================================

    booking_reference = models.CharField(
        max_length=30,
        unique=True
    )

    # =================================================
    # AGENT
    # =================================================

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="umrah_bookings"
    )

    # =================================================
    # UMRAH PACKAGE
    # =================================================

    package = models.ForeignKey(
        UmrahPackage,
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    # =================================================
    # LEAD PASSENGER
    # =================================================

    lead_passenger = models.ForeignKey(
        Passenger,
        on_delete=models.PROTECT,
        related_name="lead_umrah_bookings"
    )

    # =================================================
    # OTHER PILGRIMS
    # =================================================

    pilgrims = models.ManyToManyField(
        Passenger,
        related_name="umrah_bookings",
        blank=True
    )

    # =================================================
    # PILGRIM COUNT
    # =================================================

    pilgrims_count = models.PositiveIntegerField(
        default=1
    )

    # =================================================
    # TOTAL PRICE
    # =================================================

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # =================================================
    # STATUS
    # =================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    # =================================================
    # REJECTION REASON
    # =================================================

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    # =================================================
    # BOOKING TIME
    # =================================================

    booked_at = models.DateTimeField(
        auto_now_add=True
    )

    # =================================================
    # CONFIRMATION TIME
    # =================================================

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =================================================
    # EXPIRY TIME
    # 24 HOURS AFTER ADMIN APPROVAL
    # =================================================

    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =================================================
    # LAST UPDATE
    # =================================================

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return self.booking_reference


# =========================
# BOOKING
# =========================

class Booking(models.Model):

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        ("CONFIRMED", "Confirmed"),

        ("REJECTED", "Rejected"),

        ("CANCELLED", "Cancelled"),

        ("COMPLETED", "Completed"),

    ]

    booking_reference = models.CharField(
        max_length=30,
        unique=True
    )

    # =========================
    # PNR
    # =========================

    pnr = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    # =========================
    # TICKET NUMBER
    # =========================

    ticket_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    seats_booked = models.PositiveIntegerField(
        default=1
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    booked_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.booking_reference


# =========================
# GROUP BOOKING
# =========================

class GroupBooking(models.Model):

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        ("CONFIRMED", "Confirmed"),

        ("REJECTED", "Rejected"),

        ("CANCELLED", "Cancelled"),

        ("COMPLETED", "Completed"),

        ("EXPIRED", "Expired"),

    ]

    booking_reference = models.CharField(
        max_length=30,
        unique=True
    )

    # =========================
    # PNR
    # 2 letters + 4 numbers
    # Example: AK2715
    # =========================

    pnr = models.CharField(
        max_length=6,
        unique=True,
        null=True,
        blank=True
    )

    # =========================
    # TICKET NUMBER
    # =========================

    ticket_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )

    # =========================
    # AGENT
    # =========================

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="group_bookings"
    )

    # =========================
    # GROUP TICKET
    # =========================

    group_ticket = models.ForeignKey(
        GroupTicket,
        on_delete=models.PROTECT,
        related_name="group_bookings"
    )

    # =========================
    # PASSENGER
    # =========================

    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.PROTECT,
        related_name="group_bookings"
    )

    # =========================
    # SEATS
    # =========================

    seats_booked = models.PositiveIntegerField(
        default=1
    )

    # =========================
    # TOTAL PRICE
    # =========================

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # =========================
    # STATUS
    # =========================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    # =========================
    # REJECTION REASON
    # =========================

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    # =========================
    # BOOKING TIME
    # =========================

    booked_at = models.DateTimeField(
        auto_now_add=True
    )

    # =========================
    # CONFIRMATION TIME
    # =========================

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =========================
    # EXPIRY TIME
    # 2 hours after confirmation
    # =========================

    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =========================
    # LAST UPDATE
    # =========================

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return self.booking_reference

# =====================================================
# AGENT WALLET
# =====================================================

class AgentWallet(models.Model):

    agent = models.OneToOneField(
        Agent,
        on_delete=models.CASCADE,
        related_name="wallet"
    )

    # Current available wallet balance
    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    # Total amount approved and deposited
    total_deposited = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    # Total amount spent on bookings
    total_spent = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return f"{self.agent.agency} Wallet"


# =====================================================
# TOP-UP REQUEST
# =====================================================

class TopUpRequest(models.Model):

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        ("APPROVED", "Approved"),

        ("REJECTED", "Rejected"),

    ]

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="topup_requests"
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    transaction_date = models.DateField()

    receipt = models.ImageField(
        upload_to="wallet_receipts/"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    admin_note = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):

        return (
            f"{self.agent.agency} - "
            f"PKR {self.amount} - "
            f"{self.status}"
        )


# =====================================================
# WALLET TRANSACTION
# =====================================================

class WalletTransaction(models.Model):

    TRANSACTION_TYPES = [

        ("CREDIT", "Credit"),

        ("DEBIT", "Debit"),

    ]

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="wallet_transactions"
    )

    reference = models.CharField(
        max_length=50
    )

    description = models.CharField(
        max_length=255
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    debit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    balance_after = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return (
            f"{self.agent.agency} - "
            f"{self.reference}"
        )

