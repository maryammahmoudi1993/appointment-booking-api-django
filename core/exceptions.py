from rest_framework.exceptions import APIException


class BookingConflict(APIException):
    status_code = 409
    default_detail = "The requested time slot conflicts with an existing booking."
    default_code = "booking_conflict"


class OutsideWorkingHours(APIException):
    status_code = 400
    default_detail = (
        "The requested time falls outside the staff member's working hours."
    )
    default_code = "outside_working_hours"


class DuringTimeOff(APIException):
    status_code = 400
    default_detail = "The requested time falls during the staff member's time off."
    default_code = "during_time_off"


class InvalidTimeRange(APIException):
    status_code = 400
    default_detail = "End time must be after start time."
    default_code = "invalid_time_range"
