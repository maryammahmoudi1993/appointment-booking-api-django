from apps.business.models import Business, BusinessMembership


def get_user_business(user):
    membership = (
        BusinessMembership.objects.filter(user=user).select_related("business").first()
    )
    return membership.business if membership else None


def get_user_business_or_404(user):
    business = get_user_business(user)
    if business is None:
        from django.http import Http404

        raise Http404("No business found for this user")
    return business


def get_default_business():
    return Business.objects.filter(is_active=True).first()
