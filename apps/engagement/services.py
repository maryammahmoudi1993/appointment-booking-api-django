from decimal import Decimal

from django.utils import timezone

from .models import PromoCode


class PromoCodeError(Exception):
    pass


def validate_promo_code(code: str, service=None) -> PromoCode:
    try:
        promo = PromoCode.objects.get(code=code.upper().strip())
    except PromoCode.DoesNotExist:
        raise PromoCodeError("Invalid promo code.")

    if not promo.is_active:
        raise PromoCodeError("This promo code is no longer active.")

    now = timezone.now()
    if promo.starts_at and now < promo.starts_at:
        raise PromoCodeError("This promo code is not active yet.")
    if promo.ends_at and now > promo.ends_at:
        raise PromoCodeError("This promo code has expired.")
    if (
        promo.max_redemptions is not None
        and promo.redemptions.count() >= promo.max_redemptions
    ):
        raise PromoCodeError("This promo code has reached its redemption limit.")

    applicable_services = promo.services.all()
    if applicable_services.exists() and service is not None:
        if not applicable_services.filter(pk=service.pk).exists():
            raise PromoCodeError(
                "This promo code does not apply to the selected service."
            )

    return promo


def compute_discount(promo: PromoCode, price: Decimal) -> Decimal:
    if promo.discount_type == "percent":
        discount = (price * promo.discount_value / Decimal("100")).quantize(
            Decimal("0.01")
        )
    else:
        discount = promo.discount_value
    return min(discount, price)
