import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os
from datetime import datetime
from calvfs.event_files import setup_calendar_directory, create_event_files
from calvfs.google import (
    fetch_calendar_events,
    delete_google_event,
    update_or_create_google_event,
)


def get_last_sync_time(sync_info_path):
    try:
        with open(sync_info_path, "r") as file:
            return datetime.fromisoformat(file.read().strip())
    except FileNotFoundError:
        # Return the earliest possible date if no sync has occurred
        return datetime.min


def update_last_sync_time(sync_info_path):
    with open(sync_info_path, "w") as file:
        file.write(datetime.now().isoformat())


def file_last_modified_time(file_path):
    return datetime.fromtimestamp(os.path.getmtime(file_path))


def needs_sync(file_path, sync_info_path):
    last_sync_time = get_last_sync_time(sync_info_path)
    last_modified_time = file_last_modified_time(file_path)
    return last_modified_time > last_sync_time


def scan_local_changes_and_push(base_path, service, sync_info_path):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            # Check file extension
            # TODO: allow other filetypes
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                if needs_sync(file_path, sync_info_path):
                    print(f"{file_path} needs syncing")
                    update_or_create_google_event(service, file_path)
                else:
                    print(f"{file_path} no sync needed")
            else:
                print(f"Ignored non-txt file: {file}")


def sync_calendar(base_path, service, sync_info_path):
    current_year = datetime.now().year
    setup_calendar_directory(base_path)

    # Pull updates from Google Calendar and update local files
    events = fetch_calendar_events(service, current_year)
    if events:
        print("Fetching calendar events")
    create_event_files(base_path, current_year, events)

    # Push local changes to Google Calendar
    scan_local_changes_and_push(base_path, service, sync_info_path)

    update_last_sync_time(sync_info_path)


## TODO: move AutoSyncHandler out of sync.py
class AutoSyncHandler(FileSystemEventHandler):
    def __init__(self, service):
        self.service = service

    def on_modified(self, event):
        if not event.is_directory:
            print(f"File {event.src_path} has been modified.")
            update_or_create_google_event(self.service, event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            print(f"File {event.src_path} has been created.")
            update_or_create_google_event(self.service, event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File {event.src_path} has been deleted.")
            delete_google_event(self.service, event.src_path)


def auto_sync(path, service):
    event_handler = AutoSyncHandler(service)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("Auto-sync started. Monitoring changes in the directory.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        print("Auto-sync stopped.")
