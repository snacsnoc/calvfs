import argparse
import os

from googleapiclient.discovery import build

from calvfs.auth import authenticate_google_calendar, deauthenticate
from calvfs.sync import sync_calendar, auto_sync


def main():
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    if not service:
        print("Please run calvfs.py cli_auth")
        return
    parser = argparse.ArgumentParser(
        description="calvfs: Google Calendar synchronization with a local filesystem"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Authentication command
    subparsers.add_parser("cli_auth", help="Authenticate and save authentication token")

    # Deauthentication command
    subparsers.add_parser("deauth", help="Remove saved authentication token")

    # One-time synchronization command
    subparsers.add_parser("sync", help="Perform a one-time sync")

    # Continuous synchronization command
    subparsers.add_parser("autosync", help="Continuous background synchronization")

    args = parser.parse_args()
    home_dir = os.path.expanduser("~")
    calendar_path = os.path.join(home_dir, "calendar")
    # File to store the last sync timestamp
    sync_info_path = os.path.join(calendar_path, ".last_sync_time")

    if args.command == "cli_auth":
        authenticate_google_calendar()
    elif args.command == "deauth":
        deauthenticate()
    elif args.command == "sync":
        sync_calendar(calendar_path, service, sync_info_path)
    elif args.command == "autosync":
        auto_sync(calendar_path, service)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
