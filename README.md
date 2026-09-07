# Last-Signal: a dead man's switch Discord bot

Last-Signal watches for a check-in. The owner runs `!alive` from time to time. If that
stops happening, the bot sends reminders, and once the deadline passes it notifies a list
of emergency contacts by DM and posts an alert embed in every registered channel.

## How it works

1. The owner claims the bot by running `!alive` for the first time. Whoever runs it first
   becomes the owner, and `Him_id` is written to `data.json`.
2. A background task runs every 6 hours and compares the current UTC time against the last
   check-in.
3. At 10, 12, and 13 days of silence, the owner gets a reminder DM. Each threshold fires
   once, tracked in `reminders_sent`.
4. At 14 days, every emergency contact gets a DM and every registered channel gets the
   alert embed, with an optional role mention.
5. Running `!alive` resets the timer and clears the reminder flags.

## Commands

Every command except `!status` and `!listchannels` is owner only.

| Command | What it does |
|---|---|
| `!alive` | Confirm you are active. Resets the countdown and clears reminder flags. |
| `!addcontact <user_id>` | Add a Discord user ID to the emergency contact list. Takes a numeric ID, not a mention. |
| `!removecontact @user` | Remove a contact. Takes a mention or a resolvable user. |
| `!addchannel <channel_id>` | Register a channel that receives the alert embed. |
| `!listchannels` | List the registered alert channels. |
| `!setrole <role_id>` | Set a role to mention in channel alerts. |
| `!status` | Days since last check-in, the deadline, days remaining, and the number of contacts and channels. |
| `!panic` | Send the alert embed to every registered channel right now, without waiting for the deadline. |
| `!testalert` | Send a test message to every contact and channel, then report how many went through. |

## Configuration

The three timing constants live at the top of `deadman_Bot/bot.py`:

| Constant | Default | Meaning |
|---|---|---|
| `CHECK_INTERVAL_HOURS` | 6 | How often the background task checks for inactivity |
| `DEADLINE_DAYS` | 14 | Days of silence before contacts are alerted |
| `REMINDER_DAYS` | `[10, 12, 13]` | Days at which the owner gets a reminder DM |

If you change `REMINDER_DAYS`, update the keys in `reminders_sent` inside `data.json` to
match. The loop looks each day up by its string key and raises a `KeyError` if it is
missing.

## Setup

Requirements: Python 3.8 or newer, and a bot token from the
[Discord Developer Portal](https://discord.com/developers/applications).

The bot needs the Message Content privileged intent, which is toggled per application in
the portal. Without it the prefix commands never fire.

```bash
git clone https://github.com/Ihsan-p1/Last-Signal.git
cd Last-Signal

python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux, macOS

pip install discord.py python-dotenv
```

There is no `requirements.txt`. Those two packages are the whole dependency list.

Create the token file and the state file:

```bash
cp .env.example .env
cp deadman_Bot/data.example.json deadman_Bot/data.json
```

Put your token in `.env`:

```
DISCORD_TOKEN=your_bot_token_here
```

`data.json` has to exist before the first run. The bot reads it on every command and does
not create it.

Then run the bot:

```bash
python deadman_Bot/bot.py
```

## Project structure

```
Last-Signal/
├── deadman_Bot/
│   ├── bot.py                 # All bot logic: commands, the 6-hour loop, alert embed
│   ├── data.example.json      # Template for the state file
│   └── data.json              # Live state, gitignored
├── .env.example
└── .env                       # Discord token, gitignored
```

## State file

`data.json` is the only persistence. No database.

| Key | Meaning |
|---|---|
| `Him_id` | Discord user ID of the owner. `0` until the first `!alive` claims it. |
| `last_checkin` | ISO timestamp of the last check-in, or `null` before the first one. |
| `contacts` | User IDs that get a DM at the deadline. |
| `channels` | Channel IDs that get the alert embed. |
| `alert_role_id` | Role mentioned in channel alerts, or `null`. |
| `reminders_sent` | Which reminder thresholds have already fired since the last check-in. |

Back it up if the contact list matters. Losing the file means losing the owner ID, the
contacts, and the check-in history.

## Known limits

- Once past the deadline, the alert repeats on every check, so contacts get a DM every 6
  hours until someone runs `!alive`. There is no "already alerted" flag.
- Timestamps use naive `datetime.utcnow()`, and the day count is a floor division, so a
  check-in 13 days and 23 hours old still reads as 13 days.
- A contact who blocks DMs from server members is skipped silently at the deadline.
  `!testalert` is the way to find that out in advance.
- Only one owner. The first user to run `!alive` on a fresh `data.json` claims the bot, and
  changing owners means editing `Him_id` by hand.
