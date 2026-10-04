
from django import forms
from .models import (
    Passenger,
    GroupTicket,
    UmrahPackage,
    Flight,
    Hotel,
    Airline,
    Airport,
)


# =====================================================
# PASSENGER FORM
# =====================================================

class PassengerForm(forms.ModelForm):

    class Meta:

        model = Passenger

        fields = [
            "first_name",
            "last_name",
            "passport_number",
            "date_of_birth",
            "gender",
            "nationality",
            "phone",
            "email",
        ]

        widgets = {

            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter first name"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter last name"
            }),

            "passport_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter passport number"
            }),

            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "gender": forms.Select(attrs={
                "class": "form-select"
            }),

            "nationality": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter nationality"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter phone number"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email address"
            }),
        }


# =====================================================
# GROUP TICKET FORM
# =====================================================

class GroupTicketForm(forms.ModelForm):

    class Meta:

        model = GroupTicket

        fields = [
            "airline",
            "flight_number",
            "departure_airport",
            "arrival_airport",
            "category",
            "departure_date",
            "departure_time",
            "arrival_time",
            "baggage",
            "meal",
            "price",
            "total_seats",
            "available_seats",
            "is_active",
        ]

        widgets = {

            "airline": forms.Select(attrs={
                "class": "form-select"
            }),

            "flight_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter flight number"
            }),

            "departure_airport": forms.Select(attrs={
                "class": "form-select"
            }),

            "arrival_airport": forms.Select(attrs={
                "class": "form-select"
            }),

            "category": forms.Select(attrs={
                "class": "form-select"
            }),

            "departure_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "departure_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),

            "arrival_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),

            "baggage": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: 20+7 KG"
            }),

            "meal": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Included / No"
            }),

            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Price per seat",
                "step": "0.01",
                "min": "0"
            }),

            "total_seats": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Total group seats",
                "min": "0"
            }),

            "available_seats": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Available seats",
                "min": "0"
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def clean(self):

        cleaned_data = super().clean()

        total_seats = cleaned_data.get("total_seats")
        available_seats = cleaned_data.get("available_seats")

        if (
            total_seats is not None
            and available_seats is not None
            and available_seats > total_seats
        ):

            self.add_error(
                "available_seats",
                "Available seats cannot be greater than total seats."
            )

        return cleaned_data


# =====================================================
# UMRAH PACKAGE FORM
# =====================================================


            # =====================================================
# UMRAH PACKAGE FORM
# =====================================================

class UmrahPackageForm(forms.ModelForm):

    class Meta:

        model = UmrahPackage

        fields = [

            "name",
            "sector",

            "nights_in_makkah",
            "nights_in_madinah",
            "room_type",

            # AIRLINE
            "airline",

            # OUTBOUND
            "outbound_departure_airport",
            "outbound_arrival_airport",
            "outbound_flight_number",
            "outbound_departure_date",
            "outbound_departure_time",
            "outbound_arrival_time",
            "outbound_baggage",
            "outbound_meal",

            # RETURN
            "return_departure_airport",
            "return_arrival_airport",
            "return_flight_number",
            "return_departure_date",
            "return_departure_time",
            "return_arrival_time",
            "return_baggage",
            "return_meal",

            # HOTELS
            "makkah_hotel",
            "madinah_hotel",

            # PRICE / SEATS
            "price",
            "total_seats",
            "available_seats",

            # STATUS
            "status",
            "description",
        ]

        widgets = {

            # =========================================
            # PACKAGE
            # =========================================

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Premium Umrah Package"
            }),

            "sector": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: LHE-JED-LHE"
            }),

            "nights_in_makkah": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "Makkah nights"
            }),

            "nights_in_madinah": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "Madinah nights"
            }),

            "room_type": forms.Select(attrs={
                "class": "form-select"
            }),

            # =========================================
            # AIRLINE
            # =========================================

            "airline": forms.Select(attrs={
                "class": "form-select"
            }),

            # =========================================
            # OUTBOUND AIRPORTS
            # =========================================

            "outbound_departure_airport": forms.Select(attrs={
                "class": "form-select"
            }),

            "outbound_arrival_airport": forms.Select(attrs={
                "class": "form-select"
            }),

            # =========================================
            # OUTBOUND FLIGHT
            # =========================================

            "outbound_flight_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: PA 470"
            }),

            "outbound_departure_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "outbound_departure_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),

            "outbound_arrival_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),

            "outbound_baggage": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: 20+7 KG"
            }),

            "outbound_meal": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Yes / No"
            }),

            # =========================================
            # RETURN AIRPORTS
            # =========================================

            "return_departure_airport": forms.Select(attrs={
                "class": "form-select"
            }),

            "return_arrival_airport": forms.Select(attrs={
                "class": "form-select"
            }),

            # =========================================
            # RETURN FLIGHT
            # =========================================

            "return_flight_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: PA 471"
            }),

            "return_departure_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "return_departure_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),

            "return_arrival_time": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),

            "return_baggage": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: 30+7 KG"
            }),

            "return_meal": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Yes / No"
            }),

            # =========================================
            # HOTELS
            # =========================================

            "makkah_hotel": forms.Select(attrs={
                "class": "form-select"
            }),

            "madinah_hotel": forms.Select(attrs={
                "class": "form-select"
            }),

            # =========================================
            # PRICE
            # =========================================

            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Package price in PKR",
                "step": "0.01",
                "min": "0"
            }),

            # =========================================
            # SEATS
            # =========================================

            "total_seats": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Total seats",
                "min": "0"
            }),

            "available_seats": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Available seats",
                "min": "0"
            }),

            # =========================================
            # STATUS
            # =========================================

            "status": forms.Select(attrs={
                "class": "form-select"
            }),

            # =========================================
            # DESCRIPTION
            # =========================================

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter package details..."
            }),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # =========================================
        # AIRLINE DROPDOWN
        # =========================================

        self.fields["airline"].queryset = (
            Airline.objects
            .filter(is_active=True)
            .order_by("name")
        )

        # =========================================
        # AIRPORT DROPDOWNS
        # =========================================

        active_airports = (
            Airport.objects
            .filter(is_active=True)
            .order_by("city", "code")
        )

        self.fields["outbound_departure_airport"].queryset = active_airports

        self.fields["outbound_arrival_airport"].queryset = active_airports

        self.fields["return_departure_airport"].queryset = active_airports

        self.fields["return_arrival_airport"].queryset = active_airports

        # =========================================
        # HOTEL DROPDOWNS
        # =========================================

        self.fields["makkah_hotel"].queryset = (
            Hotel.objects
            .filter(
                location="MAKKAH",
                is_active=True
            )
            .order_by("name")
        )

        self.fields["madinah_hotel"].queryset = (
            Hotel.objects
            .filter(
                location="MADINAH",
                is_active=True
            )
            .order_by("name")
        )

        # =========================================
        # AIRLINE LABEL
        # =========================================

        self.fields["airline"].label_from_instance = (
            lambda obj:
            f"{obj.name} ({obj.code})"
        )

        # =========================================
        # AIRPORT LABEL
        # =========================================

        self.fields["outbound_departure_airport"].label_from_instance = (
            lambda obj:
            f"{obj.city} ({obj.code}) - {obj.name}"
        )

        self.fields["outbound_arrival_airport"].label_from_instance = (
            lambda obj:
            f"{obj.city} ({obj.code}) - {obj.name}"
        )

        self.fields["return_departure_airport"].label_from_instance = (
            lambda obj:
            f"{obj.city} ({obj.code}) - {obj.name}"
        )

        self.fields["return_arrival_airport"].label_from_instance = (
            lambda obj:
            f"{obj.city} ({obj.code}) - {obj.name}"
        )

        # =========================================
        # HOTEL LABEL
        # =========================================

        def hotel_label(obj):

            if obj.distance_from_reference:

                return (
                    f"{obj.name} — "
                    f"{obj.distance_from_reference}"
                )

            return obj.name

        self.fields["makkah_hotel"].label_from_instance = hotel_label

        self.fields["madinah_hotel"].label_from_instance = hotel_label

    def clean(self):

        cleaned_data = super().clean()

        total_seats = cleaned_data.get("total_seats")

        available_seats = cleaned_data.get("available_seats")

        # =========================================
        # SEAT VALIDATION
        # =========================================

        if (
            total_seats is not None
            and available_seats is not None
            and available_seats > total_seats
        ):

            self.add_error(
                "available_seats",
                "Available seats cannot be greater than total seats."
            )

        # =========================================
        # OUTBOUND ROUTE VALIDATION
        # =========================================

        outbound_departure = cleaned_data.get(
            "outbound_departure_airport"
        )

        outbound_arrival = cleaned_data.get(
            "outbound_arrival_airport"
        )

        if (
            outbound_departure
            and outbound_arrival
            and outbound_departure.id == outbound_arrival.id
        ):

            self.add_error(
                "outbound_arrival_airport",
                "Outbound arrival airport must be different from departure airport."
            )

        # =========================================
        # RETURN ROUTE VALIDATION
        # =========================================

        return_departure = cleaned_data.get(
            "return_departure_airport"
        )

        return_arrival = cleaned_data.get(
            "return_arrival_airport"
        )

        if (
            return_departure
            and return_arrival
            and return_departure.id == return_arrival.id
        ):

            self.add_error(
                "return_arrival_airport",
                "Return arrival airport must be different from departure airport."
            )

        return cleaned_data