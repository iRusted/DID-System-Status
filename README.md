# DID System Status

A Discord bot for managing system status, alters, and messages.

**Currently a WIP.**

## Features

* Check current fronter
* Set current fronter
* View alters
* Add alters
* Remove alters
* Edit alter information
* Send/read messages
* Branch user bans
* Sets the current Fronter as the Discord Bots status
* Probably other stuff I forgot

## Requirements

* Python 3
* `discord.py`
* SQLite

Install dependencies:

```bash
pip install discord.py
```

## User Level Abilities

Super Users:

* Create/Delete/Edit Alters
* Set Current Alter
* Administrator of the System 

## Setup

1. Clone the repository.
2. Create `botConfig.py`.
3. Put your bot token and IDs in there.
4. Run `discordbot.py`.

Example:

```python
token = "YOUR_BOT_TOKEN"

superUserIDs = [
    123456789,
]

acceptedIDs = [
    123456789,
]

current_bot_host = "Your Name"
```

## Database

Uses SQLite because I don't feel like setting up an actual database server.

Database file:

```text
AlterDB.db
```

## Development 

This is currently under active development.

Things will probably break.

If something breaks, fix it.

I am always am open to new code, feel free to submit things to me. My discord is: iRustedzz

## Disclaimer

This project is a work in progress and the code is probably held together by comments, SQLite, and questionable decisions.

---

© 2026 Russell Rags. All Rights Reserved.
