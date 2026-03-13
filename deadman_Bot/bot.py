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

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def load_data():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if "channels" not in data:
        data["channels"] = []

    return data


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
async def addcontact(ctx, user_id: int):

    data = load_data()

    if ctx.author.id != data["Him_id"]:
        await ctx.send("Only Him can add contacts.")
        return

    if user_id not in data["contacts"]:
        data["contacts"].append(user_id)
        save_data(data)

        await ctx.send(f"Added user ID {user_id} as emergency contact.")
    else:
        await ctx.send("User already in contact list.")


@bot.command()
async def addchannel(ctx, channel_id: int):

    data = load_data()

    if ctx.author.id != data["Him_id"]:
        await ctx.send("Only Him can add channels.")
        return

    if channel_id not in data["channels"]:
        data["channels"].append(channel_id)
        save_data(data)

        await ctx.send(f"Channel {channel_id} added.")
    else:
        await ctx.send("Channel already registered.")


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
Channels: {len(data["channels"])}
"""
    )


@bot.command()
async def testalert(ctx):

    data = load_data()

    if ctx.author.id != data["Him_id"]:
        await ctx.send("Only Him can run this test.")
        return

    success_dm = 0
    failed_dm = 0
    success_channel = 0

    # TEST DM
    for uid in data["contacts"]:

        try:
            user = await bot.fetch_user(uid)

            await user.send(
                "⚠️ TEST ALERT ⚠️\n\n"
                "Last Signal system test message.\n"
                "Emergency notifications are working."
            )

            success_dm += 1

        except discord.Forbidden:
            failed_dm += 1

        except Exception as e:
            print(e)
            failed_dm += 1

    # TEST CHANNEL
    for cid in data["channels"]:

        try:
            channel = await bot.fetch_channel(cid)

            await channel.send(
                "⚠️ TEST ALERT ⚠️\n"
                "Last Signal system test successful."
            )

            success_channel += 1

        except discord.Forbidden:
            print(f"No permission in channel {cid}")

        except discord.NotFound:
            print(f"Channel not found: {cid}")

        except Exception as e:
            print(e)

    await ctx.send(
        f"""
Test Finished

DM Delivered: {success_dm}
DM Failed: {failed_dm}
Server Messages Sent: {success_channel}
"""
    )


@tasks.loop(hours=CHECK_INTERVAL_HOURS)
async def check_status():

    data = load_data()

    if data["last_checkin"] is None:
        return

    days = get_days_since(data["last_checkin"])

    # REMINDER
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

    # EMERGENCY ALERT
    if days >= DEADLINE_DAYS:

        # DM CONTACTS
        for uid in data["contacts"]:

            try:
                user = await bot.fetch_user(uid)

                await user.send(
                    "⚠️ Last Signal ALERT\n\n"
                    "User hasn't checked in for 14 days."
                )

            except:
                pass

        # SERVER CHANNELS
        for cid in data["channels"]:

            try:
                channel = await bot.fetch_channel(cid)

                await channel.send(
                    "⚠️ **Last Signal ALERT**\n\n"
                    "User hasn't checked in for 14 days.\n"
                    "Please check on them."
                )

            except discord.Forbidden:
                print(f"No permission in channel {cid}")

            except discord.NotFound:
                print(f"Channel not found: {cid}")

            except Exception as e:
                print(e)


bot.run(TOKEN)