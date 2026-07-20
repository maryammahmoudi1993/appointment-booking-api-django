import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.appointments.models import Appointment
from apps.services.models import Service
from apps.staff.models import StaffProfile, TimeOff, WorkingHours


class Command(BaseCommand):
    help = "Seed the database with demo data for portfolio demonstration."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # Services
        services_data = [
            {
                "name": "Haircut",
                "description": "Standard haircut and styling",
                "duration_minutes": 30,
                "price": 25.00,
            },
            {
                "name": "Beard Trim",
                "description": "Beard shaping and trim",
                "duration_minutes": 15,
                "price": 15.00,
            },
            {
                "name": "Hair Color",
                "description": "Full hair coloring service",
                "duration_minutes": 90,
                "price": 75.00,
            },
            {
                "name": "Manicure",
                "description": "Classic manicure treatment",
                "duration_minutes": 45,
                "price": 35.00,
            },
            {
                "name": "Massage",
                "description": "60-minute relaxation massage",
                "duration_minutes": 60,
                "price": 60.00,
            },
        ]
        services = []
        for s in services_data:
            service, _ = Service.objects.get_or_create(name=s["name"], defaults=s)
            services.append(service)
            self.stdout.write(f"  Service: {service.name}")

        # Admin user
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@demo.com",
                "role": "admin",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.set_password("admin123")
        admin_user.save()
        self.stdout.write(f"  Admin: {admin_user.username}")

        # Staff users
        staff_users = []
        staff_data = [
            {
                "username": "staff_alice",
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice@demo.com",
            },
            {
                "username": "staff_bob",
                "first_name": "Bob",
                "last_name": "Smith",
                "email": "bob@demo.com",
            },
        ]
        for s in staff_data:
            user, _ = User.objects.get_or_create(
                username=s["username"],
                defaults={**s, "role": "staff"},
            )
            user.set_password("staff123")
            user.save()
            profile, _ = StaffProfile.objects.get_or_create(user=user)
            profile.services_offered.set(
                random.sample(services, k=min(3, len(services)))
            )
            staff_users.append(user)
            self.stdout.write(f"  Staff: {user.username}")

        # Working hours (Mon-Fri, 9-17)
        for staff in staff_users:
            for weekday in range(5):
                WorkingHours.objects.get_or_create(
                    staff=staff,
                    weekday=weekday,
                    defaults={"start_time": "09:00", "end_time": "17:00"},
                )

        # Time off for first staff member next week
        next_monday = timezone.now().date() + timedelta(
            days=(7 - timezone.now().weekday())
        )
        TimeOff.objects.get_or_create(
            staff=staff_users[0],
            start_datetime=timezone.make_aware(
                timezone.datetime.combine(
                    next_monday, timezone.datetime.min.time().replace(hour=12)
                )
            ),
            end_datetime=timezone.make_aware(
                timezone.datetime.combine(
                    next_monday, timezone.datetime.min.time().replace(hour=14)
                )
            ),
            defaults={"reason": "Lunch meeting"},
        )
        self.stdout.write(f"  Time off created for {staff_users[0].username}")

        # Customer users
        customers = []
        customer_data = [
            {
                "username": "customer_john",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@demo.com",
                "phone_number": "+1234567890",
            },
            {
                "username": "customer_jane",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@demo.com",
                "phone_number": "+0987654321",
            },
        ]
        for c in customer_data:
            user, _ = User.objects.get_or_create(
                username=c["username"],
                defaults={**c, "role": "customer"},
            )
            user.set_password("customer123")
            user.save()
            customers.append(user)
            self.stdout.write(f"  Customer: {user.username}")

        # Appointments
        now = timezone.now()
        appointment_data = [
            {
                "customer": customers[0],
                "staff": staff_users[0],
                "service": services[0],
                "start_datetime": now.replace(
                    hour=10, minute=0, second=0, microsecond=0
                )
                + timedelta(days=1),
                "status": "confirmed",
            },
            {
                "customer": customers[1],
                "staff": staff_users[1],
                "service": services[1],
                "start_datetime": now.replace(
                    hour=11, minute=0, second=0, microsecond=0
                )
                + timedelta(days=1),
                "status": "pending",
            },
            {
                "customer": customers[0],
                "staff": staff_users[0],
                "service": services[2],
                "start_datetime": now.replace(
                    hour=14, minute=0, second=0, microsecond=0
                )
                + timedelta(days=2),
                "status": "pending",
            },
        ]
        for a in appointment_data:
            service = a["service"]
            a["end_datetime"] = a["start_datetime"] + timedelta(
                minutes=service.duration_minutes
            )
            appointment, created = Appointment.objects.get_or_create(
                customer=a["customer"],
                staff=a["staff"],
                service=a["service"],
                start_datetime=a["start_datetime"],
                defaults={"end_datetime": a["end_datetime"], "status": a["status"]},
            )
            if created:
                self.stdout.write(f"  Appointment: {appointment}")

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
        self.stdout.write("")
        self.stdout.write("Demo accounts:")
        self.stdout.write(f"  Admin:    admin / admin123")
        self.stdout.write(f"  Staff:    staff_alice / staff123")
        self.stdout.write(f"  Staff:    staff_bob / staff123")
        self.stdout.write(f"  Customer: customer_john / customer123")
        self.stdout.write(f"  Customer: customer_jane / customer123")
