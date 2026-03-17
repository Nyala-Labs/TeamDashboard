"""Google Calendar API integration for scheduling meetings."""
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.core.config import settings

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_credentials() -> Credentials | None:
    """Obtain valid user credentials from storage or OAuth flow."""
    creds = None
    token_path = Path(settings.google_calendar_token_path)
    creds_path = Path(settings.google_calendar_credentials_path)

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif creds_path.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            return None

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def create_calendar_event(
    summary: str,
    start_time: datetime,
    end_time: datetime,
    description: str = "",
    attendees: list[str] | None = None,
) -> str | None:
    """
    Create a Google Calendar event. Returns the event ID if successful, None otherwise.
    """
    creds = get_calendar_credentials()
    if not creds:
        return None

    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
        "attendees": [{"email": email} for email in (attendees or [])],
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return created.get("id")
