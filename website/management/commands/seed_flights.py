from datetime import date, time, timedelta
from decimal import Decimal
from random import choice, randint

from django.core.management.base import BaseCommand
from django.db import transaction

from website.models import Airline, Airport, Flight


class Command(BaseCommand):

    help = "Create realistic sample flight data for AL NAJAM."

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.WARNING(
                "Starting AL NAJAM flight database setup..."
            )
        )

        # =====================================================
        # 1. AIRLINES
        # =====================================================

        airlines_data = [
            ("Fly Jinnah", "9P"),
            ("SalamAir", "OV"),
            ("Flynas", "XY"),
            ("Airblue", "PA"),
            ("PIA", "PK"),
            ("Flyadeal", "F3"),
            ("Saudia", "SV"),
            ("AirSial", "PF"),
            ("Air Arabia", "G9"),
            ("Flydubai", "FZ"),
            ("Emirates", "EK"),
            ("Qatar Airways", "QR"),
            ("Gulf Air", "GF"),
        ]

        airlines = {}

        for name, code in airlines_data:

            airline, created = Airline.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "is_active": True,
                }
            )

            airlines[code] = airline

        self.stdout.write(
            self.style.SUCCESS(
                f"Airlines ready: {len(airlines)}"
            )
        )

        # =====================================================
        # 2. AIRPORTS
        # =====================================================

        airports_data = [

            # Pakistan
            (
                "LHE",
                "Allama Iqbal International Airport",
                "Lahore",
                "Pakistan",
            ),

            (
                "ISB",
                "Islamabad International Airport",
                "Islamabad",
                "Pakistan",
            ),

            (
                "SKT",
                "Sialkot International Airport",
                "Sialkot",
                "Pakistan",
            ),

            (
                "MUX",
                "Multan International Airport",
                "Multan",
                "Pakistan",
            ),

            (
                "LYP",
                "Faisalabad International Airport",
                "Faisalabad",
                "Pakistan",
            ),

            (
                "PEW",
                "Bacha Khan International Airport",
                "Peshawar",
                "Pakistan",
            ),

            (
                "KHI",
                "Jinnah International Airport",
                "Karachi",
                "Pakistan",
            ),

            # Saudi Arabia
            (
                "JED",
                "King Abdulaziz International Airport",
                "Jeddah",
                "Saudi Arabia",
            ),

            (
                "RUH",
                "King Khalid International Airport",
                "Riyadh",
                "Saudi Arabia",
            ),

            (
                "DMM",
                "King Fahd International Airport",
                "Dammam",
                "Saudi Arabia",
            ),

            (
                "MED",
                "Prince Mohammad Bin Abdulaziz Airport",
                "Madinah",
                "Saudi Arabia",
            ),

            # UAE
            (
                "DXB",
                "Dubai International Airport",
                "Dubai",
                "UAE",
            ),

            (
                "SHJ",
                "Sharjah International Airport",
                "Sharjah",
                "UAE",
            ),

            (
                "AUH",
                "Zayed International Airport",
                "Abu Dhabi",
                "UAE",
            ),

            (
                "RKT",
                "Ras Al Khaimah International Airport",
                "Ras Al Khaimah",
                "UAE",
            ),

            # Bahrain
            (
                "BAH",
                "Bahrain International Airport",
                "Manama",
                "Bahrain",
            ),

            # Oman
            (
                "MCT",
                "Muscat International Airport",
                "Muscat",
                "Oman",
            ),

            # Qatar
            (
                "DOH",
                "Hamad International Airport",
                "Doha",
                "Qatar",
            ),

            # Kuwait
            (
                "KWI",
                "Kuwait International Airport",
                "Kuwait City",
                "Kuwait",
            ),
        ]

        airports = {}

        for code, name, city, country in airports_data:

            airport, created = Airport.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "city": city,
                    "country": country,
                    "is_active": True,
                }
            )

            airports[code] = airport

        self.stdout.write(
            self.style.SUCCESS(
                f"Airports ready: {len(airports)}"
            )
        )

        # =====================================================
        # 3. ROUTES / CATEGORIES
        # =====================================================

        routes = [

            # BAHRAIN
            ("LHE", "BAH", "BAHRAIN"),
            ("ISB", "BAH", "BAHRAIN"),
            ("SKT", "BAH", "BAHRAIN"),

            # KSA
            ("ISB", "DMM", "KSA"),
            ("ISB", "JED", "KSA"),
            ("ISB", "RUH", "KSA"),

            ("LHE", "DMM", "KSA"),
            ("LHE", "JED", "KSA"),
            ("LHE", "RUH", "KSA"),

            ("PEW", "RUH", "KSA"),
            ("SKT", "RUH", "KSA"),
            ("SKT", "JED", "KSA"),

            ("MUX", "JED", "KSA"),
            ("LYP", "JED", "KSA"),

            # OMAN
            ("LHE", "MCT", "OMAN"),
            ("SKT", "MCT", "OMAN"),
            ("MUX", "MCT", "OMAN"),
            ("ISB", "MCT", "OMAN"),

            # UAE
            ("ISB", "DXB", "UAE"),
            ("ISB", "SHJ", "UAE"),

            ("LHE", "DXB", "UAE"),
            ("LHE", "SHJ", "UAE"),

            ("LYP", "SHJ", "UAE"),
            ("PEW", "SHJ", "UAE"),
            ("MUX", "SHJ", "UAE"),

            ("ISB", "RKT", "UAE"),

            # UMRAH
            ("LHE", "JED", "UMRAH"),
            ("LYP", "JED", "UMRAH"),
            ("ISB", "JED", "UMRAH"),
            ("SKT", "JED", "UMRAH"),
        ]

        # =====================================================
        # 4. FLIGHT NUMBER PREFIXES
        # =====================================================

        airline_prefixes = {
            "9P": 700,
            "OV": 500,
            "XY": 300,
            "PA": 200,
            "PK": 600,
            "F3": 100,
            "SV": 800,
            "PF": 400,
            "G9": 900,
            "FZ": 1000,
            "EK": 2000,
            "QR": 3000,
            "GF": 4000,
        }

        # =====================================================
        # 5. CREATE FLIGHTS
        # =====================================================

        created_flights = 0

        start_date = date.today()

        for route_from, route_to, category in routes:

            for day_number in range(45):

                flight_date = (
                    start_date
                    + timedelta(days=day_number)
                )

                # 1–3 flights per route each day
                number_of_flights = randint(1, 3)

                for flight_index in range(
                    number_of_flights
                ):

                    airline_code = choice(
                        list(airlines.keys())
                    )

                    airline = airlines[
                        airline_code
                    ]

                    prefix = airline_prefixes.get(
                        airline_code,
                        5000
                    )

                    flight_number = (
                        f"{airline_code} "
                        f"{prefix + day_number + flight_index}"
                    )

                    # -----------------------------------------
                    # Departure time
                    # -----------------------------------------

                    departure_hours = [
                        2,
                        5,
                        8,
                        11,
                        14,
                        17,
                        20,
                        23,
                    ]

                    hour = choice(
                        departure_hours
                    )

                    minute = choice(
                        [
                            0,
                            10,
                            15,
                            20,
                            30,
                            40,
                            45,
                            50,
                        ]
                    )

                    departure_time = time(
                        hour,
                        minute
                    )

                    # -----------------------------------------
                    # Arrival time
                    # -----------------------------------------

                    arrival_hour = (
                        hour + randint(2, 5)
                    ) % 24

                    arrival_minute = choice(
                        [
                            0,
                            10,
                            20,
                            30,
                            40,
                            50,
                        ]
                    )

                    arrival_time = time(
                        arrival_hour,
                        arrival_minute
                    )

                    # -----------------------------------------
                    # Price
                    # -----------------------------------------

                    if category == "UMRAH":

                        price = randint(
                            75000,
                            180000
                        )

                    elif category == "KSA":

                        price = randint(
                            45000,
                            120000
                        )

                    elif category == "UAE":

                        price = randint(
                            35000,
                            95000
                        )

                    elif category == "OMAN":

                        price = randint(
                            45000,
                            100000
                        )

                    elif category == "BAHRAIN":

                        price = randint(
                            40000,
                            95000
                        )

                    else:

                        price = randint(
                            40000,
                            100000
                        )

                    # -----------------------------------------
                    # Seats
                    # -----------------------------------------

                    total_seats = choice(
                        [
                            10,
                            15,
                            20,
                            25,
                            30,
                        ]
                    )

                    available_seats = randint(
                        2,
                        total_seats
                    )

                    # -----------------------------------------
                    # Baggage
                    # -----------------------------------------

                    baggage = choice(
                        [
                            "20+7 KG",
                            "25+7 KG",
                            "30+7 KG",
                            "40+7 KG",
                        ]
                    )

                    # -----------------------------------------
                    # Meal
                    # -----------------------------------------

                    meal = choice(
                        [
                            "No",
                            "Yes",
                            "On Request",
                        ]
                    )

                    # -----------------------------------------
                    # Save flight
                    # -----------------------------------------

                    flight, created = (
                        Flight.objects.get_or_create(

                            airline=airline,

                            flight_number=flight_number,

                            departure_airport=airports[
                                route_from
                            ],

                            arrival_airport=airports[
                                route_to
                            ],

                            departure_date=flight_date,

                            defaults={

                                "category":
                                    category,

                                "departure_time":
                                    departure_time,

                                "arrival_time":
                                    arrival_time,

                                "baggage":
                                    baggage,

                                "meal":
                                    meal,

                                "price":
                                    Decimal(price),

                                "total_seats":
                                    total_seats,

                                "available_seats":
                                    available_seats,

                                "is_active":
                                    True,
                            }
                        )
                    )

                    if created:

                        created_flights += 1

        # =====================================================
        # 6. FINAL RESULT
        # =====================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "=========================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "AL NAJAM FLIGHT DATABASE READY"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Airlines: {Airline.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Airports: {Airport.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"New flights created: {created_flights}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Total flights: {Flight.objects.count()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "=========================================="
            )
        )