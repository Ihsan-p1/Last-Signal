import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import json
import datetime
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

CHECK_INTERVAL_HOURS = 6
DEADLINE_DAYS = 14
REMINDER_DAYS = [10, 12, 13]

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")\

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_days_since(last_checkin):
    if last_checkin is None:
        return 0

    last = datetime.datetime.fromisoformat(last_checkin)
    now = datetime.datetime.utcnow()

    return (now - last).days


@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")
    check_status.start()


@bot.command()
async def alive(ctx):
    data = load_data()

    if data["Him_id"] == 0:
        data["Him_id"] = ctx.author.id

    if ctx.author.id != data["Him_id"]:
        await ctx.send("Only Him can use this command.")
        return

    data["last_checkin"] = datetime.datetime.utcnow().isoformat()

    for r in data["reminders_sent"]:
        data["reminders_sent"][r] = False

    save_data(data)

    await ctx.send("Copy. Pathetic, but still Alive.")


@bot.command()
async def addcontact(ctx, user: discord.User):

    data = load_data()

    if ctx.author.id != data["Him_id"]:
        await ctx.send("Only Him can add contacts.")
        return

    if user.id not in data["contacts"]:
        data["contacts"].append(user.id)
        save_data(data)

        await ctx.send(f"Added {user.name} as list contact")
    else:
        await ctx.send("User already in contact list.")


@bot.command()
async def removecontact(ctx, user: discord.User):

    data = load_data()

    if ctx.author.id != data["Him_id"]:
        return

    if user.id in data["contacts"]:
        data["contacts"].remove(user.id)
        save_data(data)

        await ctx.send(f"Removed {user.name}")
    else:
        await ctx.send("User not in contact list.")


@bot.command()
async def status(ctx):

    data = load_data()

    if data["last_checkin"] is None:
        await ctx.send("No Check-in yet.")
        return

    days = get_days_since(data["last_checkin"])
    remaining = DEADLINE_DAYS - days

    await ctx.send(
        f"""
Status

Last Check-in: {days} days ago
Deadline: {DEADLINE_DAYS} days
Remaining: {remaining} days
Contacts: {len(data["contacts"])}
"""
    )


@tasks.loop(hours=CHECK_INTERVAL_HOURS)
async def check_status():

    data = load_data()

    if data["last_checkin"] is None:
        return

    days = get_days_since(data["last_checkin"])
    Him = await bot.fetch_user(data["Him_id"])

    for r in REMINDER_DAYS:

        if days >= r and not data["reminders_sent"][str(r)]:

            try:
                await Him.send(
                    f"Reminder: You haven't checked in for {r} days.\n"
                    f"Use !alive to reset timer."
                )
            except:
                pass

            data["reminders_sent"][str(r)] = True
            save_data(data)

    if days >= DEADLINE_DAYS:

        for uid in data["contacts"]:

            try:
                user = await bot.fetch_user(uid)

                await user.send(
                    "⚠️ ALERT\n\n"
                    "User hasn't checked in for 14 days.\n"
                    "Please check on them."
                )

            except:
                pass


bot.run(TOKEN)