"""Google Calendar adapter. Booking creation succeeds locally before calendar sync."""
from .config import GOOGLE_CALENDAR_ID

async def create_event(appointment: dict) -> str | None:
    # Implement OAuth token loading and calendar.events.insert here after the owner grants consent.
    # Return the Google event ID so future cancellation/reprogramming stays synchronized.
    del appointment, GOOGLE_CALENDAR_ID
    return None
