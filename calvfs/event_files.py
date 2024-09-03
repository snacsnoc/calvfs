import os
from dateutil import parser
from datetime import datetime


def get_event_id_from_file_normal(file_path):
    try:
        with open(file_path, "r") as file:
            for line in file:
                if "Event ID:" in line:
                    return line.split(": ")[1].strip()
    except FileNotFoundError:
        print("File not found:", file_path)
    return None


def get_event_id_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("Event ID:"):
                    return line.split(": ")[1].strip()
    except FileNotFoundError:
        return None
    except UnicodeDecodeError:
        print(
            f"Error decoding {file_path}. File may be corrupted or in a non-UTF-8 format."
        )
        return None


def get_event_id_from_file_split(file_path):
    try:
        with open(file_path, "r") as file:
            event_id_line = file.readline()
            event_id = event_id_line.split(": ")[1].strip()
        return event_id
    except FileNotFoundError:
        return None


def create_event_files(base_path, year, events):
    for event in events:
        start_time = event["start"].get("dateTime", event["start"].get("date"))
        end_time = event["end"].get("dateTime", event["end"].get("date"))
        is_full_datetime = "dateTime" in event["start"]
        # Google Calendar event ID
        event_id = event["id"]

        start_date = parser.parse(start_time)
        file_path = os.path.join(
            base_path,
            str(year),
            f"{start_date.month:02d}",
            f"{start_date.day:02d}",
            f"{event['summary']}.txt",
        )

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            # Write the event ID at the top of the file
            file.write(f"Event ID: {event_id}\n")
            if is_full_datetime:
                formatted_duration = format_duration(start_time, end_time)
                file.write(f"Duration: {formatted_duration}\n")
            else:
                file.write("Duration: All day\n")

            if "description" in event:
                file.write(f"Details: {event['description']}\n")


def setup_calendar_directory(base_path):
    current_year = datetime.now().year
    year_path = os.path.join(base_path, str(current_year))
    if not os.path.exists(year_path):
        os.makedirs(year_path)
        for month in range(1, 13):
            month_path = os.path.join(year_path, f"{month:02d}")
            os.makedirs(month_path)
            # Assuming 31 days in each month for initial setup
            for day in range(1, 32):
                try:
                    # date = datetime(current_year, month, day)
                    day_path = os.path.join(month_path, f"{day:02d}")
                    os.makedirs(day_path)
                # This handles months with less than 31 days
                except ValueError:
                    break


def format_duration(start_time, end_time):
    # Parse the start and end times
    start_dt = parser.parse(start_time)
    end_dt = parser.parse(end_time)
    # Calculate the duration as a timedelta
    duration = end_dt - start_dt

    # Format the duration in a more friendly way
    hours, remainder = divmod(duration.seconds, 3600)
    minutes = remainder // 60

    if hours and minutes:
        return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"
    elif hours:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return (
            "0 minutes"  # TODO: or some default for very short or zero duration events
        )
