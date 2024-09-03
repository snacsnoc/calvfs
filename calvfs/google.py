import os
import re
from datetime import timedelta, datetime

import googleapiclient
import tzlocal
from googleapiclient.discovery import build

from calvfs.event_files import get_event_id_from_file


def get_local_timezone():
    local_timezone = tzlocal.get_localzone()
    return local_timezone


def parse_duration(duration_str):
    match = re.match(r"(\d+)\s*(hour|minute|second)s?", duration_str, re.IGNORECASE)
    if not match:
        return None
    quantity, unit = int(match.group(1)), match.group(2).lower()
    if unit == "hour":
        return timedelta(hours=quantity)
    elif unit == "minute":
        return timedelta(minutes=quantity)
    elif unit == "second":
        return timedelta(seconds=quantity)


def clean_text(text):
    # Remove problematic characters and strip leading/trailing whitespace
    return text.translate(str.maketrans("", "", "\n\t\r")).strip()


def fetch_calendar_events(service, year):
    # Build time min and max for the full year
    time_min = datetime(year, 1, 1, 0, 0, 0).isoformat() + "Z"
    time_max = datetime(year, 12, 31, 23, 59, 59).isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return events


def parse_event_details(file_path):
    with open(file_path, "r") as file:
        lines = {
            line.split(": ", 1)[0].strip(): line.split(": ", 1)[1].strip()
            for line in file
            if ": " in line
        }

    # Get the duration and convert it
    # TODO: Allow user to change default event duration
    duration_str = lines.get("Duration", "1 hour")
    duration = parse_duration(duration_str)

    # Calculate start and end times based on the current time
    now = datetime.now(tz=get_local_timezone())
    start = now

    # Fallback to 1 hour
    end = now + duration if duration else now + timedelta(hours=1)

    # Get the description if available
    description = lines.get("Description", "")
    return start, end, description, duration_str


def create_google_event(service, file_path):
    try:
        start, end, description, duration_str = parse_event_details(file_path)
        summary = os.path.splitext(os.path.basename(file_path))[0]
        event = {
            "summary": summary,
            "start": {"dateTime": start.isoformat(), "timeZone": str(start.tzinfo)},
            "end": {"dateTime": end.isoformat(), "timeZone": str(end.tzinfo)},
            "description": description,
        }
        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )
        if not created_event["id"]:
            # Check if the event was created successfully
            raise Exception("Failed to create event")
        event_id = created_event["id"]

        # Rewrite file with event ID and standardized format
        with open(file_path, "w") as file:
            file.write(f"Event ID: {event_id}\n")
            file.write(f"Duration: {duration_str}\n")
            file.write(f"Description: {description}\n")
    except Exception as e:
        print(f"Failed to create event from file {file_path}: {e}")


def update_google_event(service, file_path):
    event_id = get_event_id_from_file(file_path)
    try:
        start, end, description, duration_str = parse_event_details(file_path)

        if event_id:
            # Update the event in Google Calendar
            event = {
                "summary": os.path.splitext(os.path.basename(file_path))[0],
                "start": {"dateTime": start.isoformat(), "timeZone": str(start.tzinfo)},
                "end": {"dateTime": end.isoformat(), "timeZone": str(end.tzinfo)},
                "description": description,
            }
            service.events().update(
                calendarId="primary", eventId=event_id, body=event
            ).execute()
        else:
            # If no event ID, assume it's a new event and create it
            create_google_event(service, file_path)

    except Exception as e:
        print(f"Failed to update or create event from file {file_path}: {e}")


def delete_google_event(service, file_path):
    event_id = get_event_id_from_file(file_path)
    service.events().delete(calendarId="primary", eventId=event_id).execute()


def get_calendar_service():
    from auth import authenticate_google_calendar

    creds = authenticate_google_calendar()
    return build("calendar", "v3", credentials=creds)


def update_or_create_google_event(service, file_path):
    event_id = get_event_id_from_file(file_path)
    try:
        start, end, description, duration_str = parse_event_details(file_path)
        event = {
            "summary": os.path.splitext(os.path.basename(file_path))[0],
            "start": {"dateTime": start.isoformat(), "timeZone": str(start.tzinfo)},
            "end": {"dateTime": end.isoformat(), "timeZone": str(end.tzinfo)},
            "description": description,
        }

        if event_id:
            # Try to update the existing event
            try:
                service.events().update(
                    calendarId="primary", eventId=event_id, body=event
                ).execute()
                print(f"Updated event {event_id}")
            except googleapiclient.errors.HttpError as e:
                # Not Found or Gone
                if e.resp.status in [404, 410]:
                    print(
                        f"Event ID {event_id} not found, creating a new event instead."
                    )
                    # Remove ID if present
                    event.pop("id", None)
                    created_event = (
                        service.events()
                        .insert(calendarId="primary", body=event)
                        .execute()
                    )
                    print(f"Created new event {created_event['id']}")
                else:
                    raise
        else:
            # Create new event if no ID exists
            created_event = (
                service.events().insert(calendarId="primary", body=event).execute()
            )
            print(f"Created new event {created_event['id']}")
            with open(file_path, "w") as file:
                file.write(f"Event ID: {created_event['id']}\n")
                file.write(f"Duration: {duration_str}\n")
                file.write(f"Description: {description}\n")

    except Exception as e:
        print(f"Failed to update or create event from file {file_path}: {e}")
