import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.appointments.models import Appointment
from apps.business.models import Business, BusinessMembership
from apps.engagement.models import LoyaltyReward, PromoCode, Review
from apps.services.models import Service
from apps.staff.models import StaffProfile, TimeOff, WorkingHours

BLOOM_STUDIO = {
    "name": "Bloom Studio",
    "slug": "bloom-studio",
    "business_type": "beauty_salon",
    "timezone": "America/New_York",
    "currency": "USD",
    "phone": "+1-555-0100",
    "email": "hello@bloomstudio.com",
    "address": "142 Spring Street, Suite 200, New York, NY 10012",
}

SERVICES_DATA = [
    {
        "name": "Women's Haircut & Style",
        "description": "Precision cut with wash, conditioning treatment, and professional blow-dry styling",
        "duration_minutes": 60,
        "price": 85.00,
        "category": "Hair",
    },
    {
        "name": "Men's Haircut",
        "description": "Classic or modern cut with hot towel finish",
        "duration_minutes": 30,
        "price": 45.00,
        "category": "Hair",
    },
    {
        "name": "Balayage / Ombre",
        "description": "Hand-painted highlights for a natural, sun-kissed gradient effect",
        "duration_minutes": 150,
        "price": 220.00,
        "category": "Hair",
    },
    {
        "name": "Gel Manicure",
        "description": "Long-lasting gel polish application with cuticle care and hand massage",
        "duration_minutes": 45,
        "price": 55.00,
        "category": "Nails",
    },
    {
        "name": "Spa Pedicure",
        "description": "Luxurious pedicure with exfoliation, mask, hot stones, and polish",
        "duration_minutes": 60,
        "price": 70.00,
        "category": "Nails",
    },
    {
        "name": "Classic Facial",
        "description": "Deep cleanse, exfoliation, extractions, and hydrating mask for glowing skin",
        "duration_minutes": 60,
        "price": 95.00,
        "category": "Skincare",
    },
    {
        "name": "Deep Tissue Massage",
        "description": "Therapeutic 60-minute massage targeting muscle tension and knots",
        "duration_minutes": 60,
        "price": 110.00,
        "category": "Wellness",
    },
    {
        "name": "Lash Extensions — Full Set",
        "description": "Individual semi-permanent lash extensions for a full, natural look",
        "duration_minutes": 120,
        "price": 180.00,
        "category": "Beauty",
    },
    {
        "name": "Brow Lamination & Tint",
        "description": "Semi-permanent brow shaping with color tint for defined, fluffy brows",
        "duration_minutes": 45,
        "price": 75.00,
        "category": "Beauty",
    },
    {
        "name": "Hair Coloring — Full",
        "description": "Single-process all-over color with gloss finish",
        "duration_minutes": 120,
        "price": 150.00,
        "category": "Hair",
    },
]

STAFF_DATA = [
    {
        "username": "mia salon",
        "first_name": "Mia",
        "last_name": "Rodriguez",
        "email": "mia@bloomstudio.com",
        "services": [
            "Women's Haircut & Style",
            "Balayage / Ombre",
            "Hair Coloring — Full",
        ],
    },
    {
        "username": "james park",
        "first_name": "James",
        "last_name": "Park",
        "email": "james@bloomstudio.com",
        "services": ["Men's Haircut", "Women's Haircut & Style"],
    },
    {
        "username": "sofia chen",
        "first_name": "Sofia",
        "last_name": "Chen",
        "email": "sofia@bloomstudio.com",
        "services": ["Gel Manicure", "Spa Pedicure"],
    },
    {
        "username": "aria williams",
        "first_name": "Aria",
        "last_name": "Williams",
        "email": "aria@bloomstudio.com",
        "services": ["Classic Facial", "Deep Tissue Massage"],
    },
    {
        "username": "noah kim",
        "first_name": "Noah",
        "last_name": "Kim",
        "email": "noah@bloomstudio.com",
        "services": ["Lash Extensions — Full Set", "Brow Lamination & Tint"],
    },
]

CUSTOMER_DATA = [
    {
        "username": "emma.johnson",
        "first_name": "Emma",
        "last_name": "Johnson",
        "email": "emma.j@email.com",
        "phone": "+1-555-0201",
    },
    {
        "username": "liam.martinez",
        "first_name": "Liam",
        "last_name": "Martinez",
        "email": "liam.m@email.com",
        "phone": "+1-555-0202",
    },
    {
        "username": "olivia.brown",
        "first_name": "Olivia",
        "last_name": "Brown",
        "email": "olivia.b@email.com",
        "phone": "+1-555-0203",
    },
    {
        "username": "noah.davis",
        "first_name": "Noah",
        "last_name": "Davis",
        "email": "noah.d@email.com",
        "phone": "+1-555-0204",
    },
    {
        "username": "ava.garcia",
        "first_name": "Ava",
        "last_name": "Garcia",
        "email": "ava.g@email.com",
        "phone": "+1-555-0205",
    },
    {
        "username": "ethan.wilson",
        "first_name": "Ethan",
        "last_name": "Wilson",
        "email": "ethan.w@email.com",
        "phone": "+1-555-0206",
    },
    {
        "username": "sophia.anderson",
        "first_name": "Sophia",
        "last_name": "Anderson",
        "email": "sophia.a@email.com",
        "phone": "+1-555-0207",
    },
    {
        "username": "mason.thomas",
        "first_name": "Mason",
        "last_name": "Thomas",
        "email": "mason.t@email.com",
        "phone": "+1-555-0208",
    },
]

REWARD_DATA = [
    {
        "name": "10% Off Next Visit",
        "description": "Valid on any single service",
        "points_cost": 50,
    },
    {
        "name": "Free Scalp Treatment",
        "description": "Add-on during any hair service",
        "points_cost": 75,
    },
    {
        "name": "Free Gel Manicure",
        "description": "One complimentary manicure session",
        "points_cost": 120,
    },
    {
        "name": "Free Haircut",
        "description": "Complimentary haircut and style session",
        "points_cost": 200,
    },
    {
        "name": "Spa Day Package",
        "description": "Facial + massage combo (2 hours)",
        "points_cost": 350,
    },
]

PROMO_DATA = [
    {
        "code": "WELCOME20",
        "description": "New client welcome — 20% off first visit",
        "discount_type": "percent",
        "discount_value": 20,
    },
    {
        "code": "SPRING25",
        "description": "Spring special — $25 off any service over $100",
        "discount_type": "fixed",
        "discount_value": 25,
    },
    {
        "code": "REFERAFRIEND",
        "description": "Refer a friend — $15 credit for both",
        "discount_type": "fixed",
        "discount_value": 15,
    },
]

APPOINTMENT_STATUSES = [
    "completed",
    "completed",
    "completed",
    "cancelled",
    "confirmed",
    "pending",
    "completed",
    "completed",
    "pending",
]

REVIEW_COMMENTS = [
    (5, "Absolutely loved my balayage! Mia is a true artist."),
    (5, "Best facial I've ever had. Sofia's hands are magic."),
    (4, "Great massage, very professional. Will book again."),
    (5, "Noah did an incredible job on my lashes. So natural!"),
    (4, "Solid haircut, exactly what I asked for."),
    (5, "The spa pedicure was heavenly. Perfect relaxation."),
    (3, "Good service but had to wait 10 minutes past my appointment time."),
    (5, "Brow lamination changed my life. Best brows ever!"),
    (4, "Nice salon atmosphere, friendly staff."),
]


class Command(BaseCommand):
    help = "Seed Bloom Studio with 6 months of realistic demo data for portfolio demonstration."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Bloom Studio demo data...\n")

        business, _ = Business.objects.update_or_create(
            slug=BLOOM_STUDIO["slug"], defaults=BLOOM_STUDIO
        )
        self.stdout.write(f"  Business: {business.name}")

        services = []
        for s in SERVICES_DATA:
            svc, _ = Service.objects.update_or_create(
                name=s["name"], defaults={**s, "business": business}
            )
            services.append(svc)
        self.stdout.write(f"  Services: {len(services)}")

        # Admin
        admin_user, _ = User.objects.update_or_create(
            username="admin",
            defaults={
                "email": "admin@bloomstudio.com",
                "role": "admin",
                "first_name": "Bloom",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.set_password("admin123")
        admin_user.save()
        BusinessMembership.objects.get_or_create(
            user=admin_user, business=business, defaults={"role": "admin"}
        )
        self.stdout.write(f"  Admin: {admin_user.username}")

        # Staff
        staff_users = []
        for s in STAFF_DATA:
            user, _ = User.objects.update_or_create(
                username=s["username"],
                defaults={
                    **{k: v for k, v in s.items() if k != "services"},
                    "role": "staff",
                },
            )
            user.set_password("staff123")
            user.save()
            profile, _ = StaffProfile.objects.update_or_create(
                user=user, defaults={"business": business}
            )
            staff_svc = [svc for svc in services if svc.name in s["services"]]
            profile.services_offered.set(staff_svc)
            BusinessMembership.objects.get_or_create(
                user=user, business=business, defaults={"role": "staff"}
            )
            staff_users.append(user)
            self.stdout.write(f"  Staff: {user.first_name} {user.last_name}")

        # Working hours — Mon-Fri 9-5, Sat 10-2
        for staff in staff_users:
            for weekday in range(5):
                WorkingHours.objects.update_or_create(
                    staff=staff,
                    weekday=weekday,
                    defaults={"start_time": "09:00", "end_time": "17:00"},
                )
            WorkingHours.objects.update_or_create(
                staff=staff,
                weekday=5,
                defaults={"start_time": "10:00", "end_time": "14:00"},
            )

        # Customers
        customers = []
        for c in CUSTOMER_DATA:
            user, _ = User.objects.update_or_create(
                username=c["username"],
                defaults={
                    "first_name": c["first_name"],
                    "last_name": c["last_name"],
                    "email": c["email"],
                    "phone_number": c["phone"],
                    "role": "customer",
                },
            )
            user.set_password("customer123")
            user.save()
            BusinessMembership.objects.get_or_create(
                user=user, business=business, defaults={"role": "customer"}
            )
            customers.append(user)
        self.stdout.write(f"  Customers: {len(customers)}")

        # Generate 6 months of appointments
        now = timezone.now()
        appointments = []
        for month_offset in range(6):
            base_date = now - timedelta(days=30 * month_offset)
            num_bookings = random.randint(6, 12)
            for _ in range(num_bookings):
                day_offset = random.randint(0, 29)
                hour = random.choice([9, 10, 10, 11, 11, 13, 14, 14, 15, 16])
                staff = random.choice(staff_users)
                service = random.choice(
                    [
                        s
                        for s in services
                        if s in staff.staff_profile.services_offered.all()
                    ]
                    or services[:2]
                )
                start = timezone.make_aware(
                    timezone.datetime.combine(
                        (base_date - timedelta(days=day_offset)).date(),
                        timezone.datetime.min.time().replace(hour=hour),
                    )
                )
                end = start + timedelta(minutes=service.duration_minutes)

                status = random.choice(APPOINTMENT_STATUSES)
                if month_offset > 2:
                    status = random.choice(["completed", "completed", "cancelled"])
                if month_offset == 0 and day_offset < 0:
                    status = random.choice(["confirmed", "pending"])

                customer = random.choice(customers)
                apt, created = Appointment.objects.get_or_create(
                    customer=customer,
                    staff=staff,
                    service=service,
                    start_datetime=start,
                    defaults={
                        "end_datetime": end,
                        "status": status,
                        "business": business,
                    },
                )
                if created:
                    if status == "completed":
                        apt.points_earned = int(service.price)
                        apt.save(update_fields=["points_earned"])
                    appointments.append(apt)

        completed = [a for a in appointments if a.status == "completed"]
        self.stdout.write(
            f"  Appointments: {len(appointments)} ({len(completed)} completed)"
        )

        # Reviews — ~40% of completed appointments
        reviewed = set()
        for apt in random.sample(
            completed, k=min(int(len(completed) * 0.4), len(completed))
        ):
            if apt.id in reviewed:
                continue
            rating, comment = random.choice(REVIEW_COMMENTS)
            Review.objects.get_or_create(
                appointment=apt,
                defaults={
                    "customer": apt.customer,
                    "staff": apt.staff,
                    "rating": rating,
                    "comment": comment,
                    "business": business,
                },
            )
            reviewed.add(apt.id)
        self.stdout.write(f"  Reviews: {len(reviewed)}")

        # Loyalty rewards
        for r in REWARD_DATA:
            LoyaltyReward.objects.update_or_create(
                name=r["name"], defaults={**r, "business": business}
            )
        self.stdout.write(f"  Loyalty rewards: {len(REWARD_DATA)}")

        # Promo codes
        for p in PROMO_DATA:
            PromoCode.objects.update_or_create(
                code=p["code"], defaults={**p, "business": business}
            )
        self.stdout.write(f"  Promo codes: {len(PROMO_DATA)}")

        # Time off — random staff member, 2 upcoming days
        future = now + timedelta(days=random.randint(3, 10))
        TimeOff.objects.get_or_create(
            staff=random.choice(staff_users),
            start_datetime=timezone.make_aware(
                timezone.datetime.combine(
                    future.date(), timezone.datetime.min.time().replace(hour=12)
                )
            ),
            end_datetime=timezone.make_aware(
                timezone.datetime.combine(
                    future.date(), timezone.datetime.min.time().replace(hour=15)
                )
            ),
            defaults={"reason": "Personal appointment"},
        )
        self.stdout.write("  Time off: 1 upcoming")

        self.stdout.write(self.style.SUCCESS("\nBloom Studio seeded successfully!"))
        self.stdout.write("")
        self.stdout.write("Demo accounts:")
        self.stdout.write("  Admin:    admin / admin123")
        self.stdout.write("  Staff:    mia salon / staff123  (Hair specialist)")
        self.stdout.write("  Staff:    james park / staff123  (Hair)")
        self.stdout.write("  Staff:    sofia chen / staff123  (Nails)")
        self.stdout.write("  Staff:    aria williams / staff123  (Wellness)")
        self.stdout.write("  Staff:    noah kim / staff123  (Lashes & Brows)")
        self.stdout.write("  Customer: emma.johnson / customer123")
        self.stdout.write("  Customer: liam.martinez / customer123")
