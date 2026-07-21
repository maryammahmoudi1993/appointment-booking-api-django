from .business import get_default_business, get_user_business


class BusinessScopedMixin:
    business_field = "business"

    def get_business(self):
        if self.request.user.is_authenticated:
            business = get_user_business(self.request.user)
            if business:
                return business
        return get_default_business()

    def get_queryset(self):
        qs = super().get_queryset()
        business = self.get_business()
        if business:
            return qs.filter(**{self.business_field: business})
        return qs.none()
