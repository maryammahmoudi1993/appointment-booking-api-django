from django.db import migrations


BLOOM_STUDIO_SLUG = "bloom-studio"


def create_bloom_studio(apps, schema_editor):
    Business = apps.get_model("business", "Business")
    BusinessSettings = apps.get_model("business", "BusinessSettings")
    BusinessMembership = apps.get_model("business", "BusinessMembership")
    Service = apps.get_model("services", "Service")
    StaffProfile = apps.get_model("staff", "StaffProfile")
    Appointment = apps.get_model("appointments", "Appointment")
    User = apps.get_model("accounts", "User")

    business, created = Business.objects.get_or_create(
        slug=BLOOM_STUDIO_SLUG,
        defaults={
            "name": "Bloom Studio",
            "business_type": "beauty_salon",
            "timezone": "UTC",
            "currency": "USD",
            "is_active": True,
        },
    )
    BusinessSettings.objects.get_or_create(
        business=business,
        defaults={
            "slot_interval_minutes": 30,
            "minimum_booking_notice_minutes": 60,
            "maximum_advance_booking_days": 60,
            "cancellation_window_hours": 24,
            "loyalty_enabled": True,
            "ai_enabled": True,
        },
    )

    Service.objects.filter(business__isnull=True).update(business=business)
    StaffProfile.objects.filter(business__isnull=True).update(business=business)
    Appointment.objects.filter(business__isnull=True).update(business=business)

    for user in User.objects.all():
        BusinessMembership.objects.get_or_create(
            user=user,
            business=business,
            defaults={"role": user.role},
        )


def reverse_bloom_studio(apps, schema_editor):
    Business = apps.get_model("business", "Business")
    try:
        business = Business.objects.get(slug=BLOOM_STUDIO_SLUG)
        Service = apps.get_model("services", "Service")
        StaffProfile = apps.get_model("staff", "StaffProfile")
        Appointment = apps.get_model("appointments", "Appointment")
        Service.objects.filter(business=business).update(business=None)
        StaffProfile.objects.filter(business=business).update(business=None)
        Appointment.objects.filter(business=business).update(business=None)
        business.delete()
    except Business.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("business", "0001_initial"),
        ("services", "0002_service_business_service_category"),
        ("staff", "0002_staffprofile_business"),
        ("appointments", "0003_appointment_business"),
    ]

    operations = [
        migrations.RunPython(create_bloom_studio, reverse_bloom_studio),
    ]
