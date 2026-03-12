# EchoLife -- Dead Man's Switch Discord Bot

A Discord bot that acts as a dead man's switch. it periodically checks whether the owner has confirmed they are active. If no check-in is received within a set deadline, the bot automatically alerts a list of emergency contacts via direct message.

---

## How It Works

1. The owner registers by running the `!alive` command for the first time.
2. A background task runs every **6 hours** to monitor the time since the last check-in.
3. Reminder DMs are sent to the owner at **10, 12, and 13 days** of inactivity.
4. If **14 days** pass with no check-in, **all emergency contacts** are notified via DM.
5. Running `!alive` at any point resets the timer and clears all sent reminders.

---

## Commands

| Command | Description |
|---|---|
| `!alive` | Confirm you are active. Resets the countdown timer. Owner only. |
| `!addcontact @user` | Add a Discord user to the emergency contact list. Owner only. |
| `!removecontact @user` | Remove a Discord user from the emergency contact list. Owner only. |
| `!status` | Display days since last check-in, deadline, and number of contacts. |

---

## Configuration

Default values are set in `bot.py` and can be adjusted:

| Parameter | Default | Description |
|---|---|---|
| `CHECK_INTERVAL_HOURS` | 6 | How often the bot checks inactivity (in hours) |
| `DEADLINE_DAYS` | 14 | Days of inactivity before contacts are alerted |
| `REMINDER_DAYS` | [10, 12, 13] | Days at which the owner receives reminder DMs |

---

## Setup

### Prerequisites

- Python 3.8+
- A Discord bot token (from the [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. Clone the repository:

```
git clone https://github.com/<your-username>/EchoLife.git
cd EchoLife
```

2. Create a virtual environment and install dependencies:

```
python -m venv .venv
.venv\Scripts\activate
pip install discord.py python-dotenv
```

3. Create a `.env` file in the project root (you can copy `.env.example` as a template):

```bash
cp .env.example .env
```
Then, edit `.env` and paste your token:
```
DISCORD_TOKEN=your_bot_token_here
```

4. Run the bot:

```
python deadman_Bot/bot.py
```

---

## Project Structure

```
EchoLife/
  .env                  # Discord bot token (do not commit)
  deadman_Bot/
    bot.py              # Main bot logic
    data.json           # Persistent state (check-in time, contacts, reminders)
```

---

## Data Storage

All persistent data is stored in `data.json`:

- `Him_id` -- Discord user ID of the owner (auto-set on first `!alive`)
- `last_checkin` -- ISO timestamp of the last check-in
- `contacts` -- List of Discord user IDs to notify on deadline
- `reminders_sent` -- Tracks which reminder thresholds have already been sent

---

## Important Notes

- Add `.env` to your `.gitignore` to avoid leaking your bot token.
- The bot requires the **Message Content** privileged intent enabled in the Discord Developer Portal.
- `data.json` is read and written at runtime. Back it up if needed.

---
