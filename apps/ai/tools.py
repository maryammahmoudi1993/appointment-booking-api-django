"""
Tool registry for AI copilot function calling.

Each tool is a dict with:
  - name: unique identifier matching the OpenAI function name
  - description: shown to the LLM
  - parameters: JSON Schema for the function's arguments
  - execute: callable(**kwargs) -> dict | str  (returns data the LLM can use)

The LLM never touches Django models directly — it only sees the data
these functions return.
"""

from datetime import date


def _get_business(user):
    """Resolve the business for the current user."""
    from apps.business.models import BusinessMembership

    membership = BusinessMembership.objects.filter(user=user).first()
    if membership:
        return membership.business
    from apps.business.models import Business

    return Business.objects.filter(is_active=True).first()


def _serialize_service(s):
    return {
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "duration_minutes": s.duration_minutes,
        "price": str(s.price),
        "category": s.category,
    }


def _serialize_staff(sp):
    return {
        "id": sp.user_id,
        "name": sp.user.get_full_name() or sp.user.username,
        "services": list(sp.services_offered.values_list("name", flat=True)),
    }


# ────────────────────────────────────────────────────────────────────
# Tool implementations
# ────────────────────────────────────────────────────────────────────


def execute_get_services(**kwargs):
    from apps.services.models import Service

    business = _get_business(kwargs.get("user"))
    qs = Service.objects.filter(is_active=True)
    if business:
        qs = qs.filter(business=business)
    if kwargs.get("category"):
        qs = qs.filter(category=kwargs["category"])
    return {"services": [_serialize_service(s) for s in qs[:20]]}


def execute_get_staff(**kwargs):
    from apps.staff.models import StaffProfile

    business = _get_business(kwargs.get("user"))
    qs = StaffProfile.objects.select_related("user").all()
    if business:
        qs = qs.filter(business=business)
    if kwargs.get("service_name"):
        qs = qs.filter(services_offered__name__icontains=kwargs["service_name"])
    return {"staff": [_serialize_staff(sp) for sp in qs[:20]]}


def execute_get_available_slots(**kwargs):
    from apps.staff.models import StaffProfile
    from apps.staff.services import get_available_slots

    staff_id = kwargs["staff_id"]
    target = kwargs["date"]

    if isinstance(target, str):
        try:
            target = date.fromisoformat(target)
        except ValueError:
            return {"error": f"Invalid date format: {target}. Use YYYY-MM-DD."}

    sp = StaffProfile.objects.filter(user_id=staff_id).first()
    business = sp.business if sp else None
    business_settings = getattr(business, "settings", None) if business else None

    slots = get_available_slots(staff_id, target, business_settings)
    available = [s for s in slots if s["available"]]
    return {
        "date": target.isoformat(),
        "staff_id": staff_id,
        "available_slots": [
            {"start": s["start"].strftime("%H:%M"), "end": s["end"].strftime("%H:%M")}
            for s in available
        ],
        "total_available": len(available),
    }


def execute_get_appointments(**kwargs):
    from apps.appointments.models import Appointment

    user = kwargs.get("user")
    if not user or not user.is_authenticated:
        return {"error": "Authentication required to view appointments."}

    qs = Appointment.objects.filter(
        customer=user, status__in=["pending", "confirmed"]
    ).select_related("staff", "service")

    status_filter = kwargs.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    results = []
    for a in qs[:20]:
        results.append(
            {
                "id": a.id,
                "service": a.service.name,
                "staff": a.staff.get_full_name() or a.staff.username,
                "start": a.start_datetime.isoformat(),
                "end": a.end_datetime.isoformat(),
                "status": a.status,
            }
        )
    return {"appointments": results}


def execute_get_business_info(**kwargs):
    business = _get_business(kwargs.get("user"))
    if not business:
        return {"error": "No business information available."}

    return {
        "name": business.name,
        "type": business.get_business_type_display(),
        "phone": business.phone,
        "email": business.email,
        "address": business.address,
        "timezone": business.timezone,
        "currency": business.currency,
    }


# ────────────────────────────────────────────────────────────────────
# Registry
# ────────────────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "get_services",
        "description": (
            "List available services offered by the business. "
            "Returns name, description, duration, price, and category."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional filter by service category.",
                }
            },
            "required": [],
        },
        "execute": execute_get_services,
    },
    {
        "name": "get_staff",
        "description": (
            "List staff members. Optionally filter by service name. "
            "Returns staff ID (for booking), name, and services offered."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Optional: filter staff who offer this service (fuzzy match).",
                }
            },
            "required": [],
        },
        "execute": execute_get_staff,
    },
    {
        "name": "get_available_slots",
        "description": (
            "Get available time slots for a specific staff member on a given date. "
            "Returns ISO time slots (HH:MM). Use staff ID from get_staff."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "staff_id": {
                    "type": "integer",
                    "description": "The staff member's user ID (from get_staff).",
                },
                "date": {
                    "type": "string",
                    "description": "The date to check availability, format YYYY-MM-DD.",
                },
            },
            "required": ["staff_id", "date"],
        },
        "execute": execute_get_available_slots,
    },
    {
        "name": "get_appointments",
        "description": (
            "Get the current customer's upcoming appointments. "
            "Returns service, staff, datetime, and status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "confirmed", "cancelled", "completed"],
                    "description": "Optional filter by appointment status.",
                }
            },
            "required": [],
        },
        "execute": execute_get_appointments,
    },
    {
        "name": "get_business_info",
        "description": (
            "Get basic business information: name, type, phone, email, address, "
            "timezone, and currency."
        ),
        "parameters": {"type": "object", "properties": {}, "required": []},
        "execute": execute_get_business_info,
    },
]

TOOL_MAP = {t["name"]: t for t in TOOL_DEFINITIONS}


def get_openai_tools():
    """Return tool definitions formatted for the OpenAI chat completions API."""
    return [
        {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}}
        for t in TOOL_DEFINITIONS
    ]


def execute_tool(tool_name, user, **kwargs):
    """Execute a registered tool by name. Returns (result_dict, error_string|None)."""
    if tool_name not in TOOL_MAP:
        return None, f"Unknown tool: {tool_name}"
    try:
        result = TOOL_MAP[tool_name]["execute"](user=user, **kwargs)
        return result, None
    except Exception as e:
        return None, f"Tool execution error: {e}"
