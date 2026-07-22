import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.engagement.models import Review
from apps.services.models import Service
from apps.staff.models import StaffProfile, TimeOff, WorkingHours
from core.business import get_default_business

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = "customer"
    phone_number = factory.LazyAttribute(lambda o: f"+1555{o.username[-4:]:0>4}")


class CustomerFactory(UserFactory):
    role = "customer"


class StaffFactory(UserFactory):
    role = "staff"


class AdminFactory(UserFactory):
    role = "admin"
    is_staff = True
    is_superuser = True


class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    name = factory.Sequence(lambda n: f"Service {n}")
    description = factory.Faker("sentence")
    duration_minutes = 30
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    is_active = True
    business = factory.LazyFunction(get_default_business)


class StaffProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StaffProfile

    user = factory.SubFactory(StaffFactory)
    bio = factory.Faker("paragraph")
    business = factory.LazyFunction(get_default_business)


class WorkingHoursFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkingHours

    staff = factory.SubFactory(StaffFactory)
    weekday = 0
    start_time = "09:00"
    end_time = "17:00"


class TimeOffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimeOff

    staff = factory.SubFactory(StaffFactory)
    start_datetime = factory.LazyFunction(
        lambda: timezone.now() + __import__("datetime").timedelta(days=1)
    )
    end_datetime = factory.LazyAttribute(
        lambda o: o.start_datetime + __import__("datetime").timedelta(hours=2)
    )
    reason = factory.Faker("sentence")


class AppointmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appointment

    customer = factory.SubFactory(CustomerFactory)
    staff = factory.SubFactory(StaffFactory)
    service = factory.SubFactory(ServiceFactory)
    business = factory.LazyFunction(get_default_business)
    start_datetime = factory.LazyFunction(
        lambda: timezone.now() + __import__("datetime").timedelta(days=2, hours=10)
    )
    end_datetime = factory.LazyAttribute(
        lambda o: o.start_datetime + __import__("datetime").timedelta(minutes=30)
    )
    status = "pending"
    notes = factory.Faker("sentence")


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    appointment = factory.SubFactory(AppointmentFactory)
    customer = factory.SubFactory(CustomerFactory)
    staff = factory.SubFactory(StaffFactory)
    business = factory.LazyFunction(get_default_business)
    rating = 4
    comment = factory.Faker("sentence")
