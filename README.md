calvfs
================
Your Google Calendar as flat files in a virtual filesystem.


## How?
**Auth:**
```bash
python3 calvfs.py cli_auth
```
**Manual sync:**
```bash
python3 calvfs.py sync
```


**List:**
```bash
ls -ls calendar/2024/

total 0
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 01
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 02
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 03
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 04
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 05
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 06
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 07
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 08
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 09
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 10
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 11
0 drwxr-xr-x  33 easto  staff  1056  6 Aug 01:07 12

```

```bash
tree  ~/calendar/

calendar/
└── 2024
    ├── 01
    │   ├── 01
    │   │   ├── Work 1:1.txt
    │   │   └── Vendor Event.txt
    │   ├── 02
    │   ├── 03
    │   │   ├── Car payment.txt
    │   │   ├── Mortgage.txt
    │   │   └── Lunch date.txt
    │   ├── 04
    │   ├── 05
    │   │   └── Payday.txt
    │   ├── 06
    │   │   └── Vet appointment.txt
```

**Create calendar entry:**
```bash
touch "~/calendar/2024/08/05/Doctor appointment.txt"
python3 calvfs.py sync
```

```bash
cat "~/calendar/2024/08/05/Doctor appointment.txt"

Event ID: 7pj1fuh[...]nbk3cs
Duration: 1 hour
```

**Autosync - *⚠️ work in progress*:**

Runs as a watchdog service monitoring for file changes then syncs.
```bash
python3 calvfs.py autosync
```

## Setup
**Google API Console Setup:**

Before running the script, you need a `credentials.json` file from Google. This file contains your OAuth 2.0 credentials.
    
* Go to the Google Developer Console.
* Create a new project or select an existing one.
* Enable the Google Calendar API for your project.
* Go to "Credentials", click "Create Credentials", and choose "OAuth client ID".
* Set the application type to "Desktop app", give it a name, and create the credentials.
* Download the credentials.json file and place it in the same directory as `calvfs/`.

**Requirements:**

* Python 3.9+
* Google `credentials.json` auth keys
* A smile on your face

**Packages:**
```bash
pip install -r requirement.txt
```
**Running:**
```bash
python3 calvfs.py 

usage: calvfs.py [-h] {cli_auth,deauth,sync,autosync} ...

calvfs: Google Calendar synchronization with a local filesystem

positional arguments:
  {cli_auth,deauth,sync,autosync}
    cli_auth            Authenticate and save authentication token
    deauth              Remove saved authentication token
    sync                Perform a one-time sync
    autosync            Continuous background synchronization

options:
  -h, --help            show this help message and exit


```

## TODO:
* Make calvfs installable with pip
* Store `credentials.json` somewhat global (~/.config)
* Fix autosync when syncing existing events