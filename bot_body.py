import configparser
import sqlite3
import datetime
import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


conn = sqlite3.connect("bot_base_points.db")
cursor = conn.cursor()
try:
    cursor.execute(
        """CREATE TABLE detail (id int, nickname text, points int)""")
    print('Database created')
except:
    print('The database has already been created')


def createConfig(path: str):
    # Create a config file
    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section('discord')
    config.add_section('wasd.tv')
    config.add_section('twitch.tv')
    config.set('discord', 'token', '')
    config.set('discord',
               '#If True, the bot puts likes under the posts and forms the top of popularity. (default: false)')
    config.set('discord', 'top_popularity', 'false')
    config.set('discord',
               '#If True, custom emoji will be registered (default: false)')
    config.set('discord', 'custom_like_emojis', 'false')
    config.set('discord',
               '#id like emojis')
    config.set('discord', 'emoji_like_id', '')
    config.set('discord',
               '#id dislike emojis')
    config.set('discord', 'emoji_dislike_id', '')
    config.set('discord',
               '#ID of the channel and the message-top that is stored in this channel')
    config.set('discord', 'channel_top_id', '')
    config.set('discord', 'message_top_id', '')
    config.set('discord', '#id role for notifications')
    config.set('discord', 'notif_role_id', '')

    with open(path, 'w') as conf:
        config.write(conf)


def getConfig(path):
    # Returns the config object
    if not os.path.exists(path):
        createConfig(path)

    config = configparser.ConfigParser()
    config.read(path)
    return config


def currentTime():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


def top_PopularityStr(actualTopID: list, actualTopPoints: list):
    topTitle = "**Звёзды:**\n"
    if len(actualTopID) > 9:
        topList = f"""🥇 <@{actualTopID[0]}> - **{actualTopPoints[0]}**
                        🥈 <@{actualTopID[1]}> - **{actualTopPoints[1]}**
                        🥉 <@{actualTopID[2]}> - **{actualTopPoints[2]}**
                        __4.__   <@{actualTopID[3]}> - **{actualTopPoints[3]}**
                        __5.__   <@{actualTopID[4]}> - **{actualTopPoints[4]}**
                        __6.__   <@{actualTopID[5]}> - **{actualTopPoints[5]}**
                        __7.__   <@{actualTopID[6]}> - **{actualTopPoints[6]}**
                        __8.__   <@{actualTopID[7]}> - **{actualTopPoints[7]}**
                        __9.__   <@{actualTopID[8]}> - **{actualTopPoints[8]}**
                        __10.__ <@{actualTopID[9]}> - **{actualTopPoints[9]}**"""
        return topTitle + topList
    topList1, topList2 = "", ""
    for i in range(len(actualTopID)):
        topList1 += f"__{i+1}.__   <@{actualTopID[i]}> - **{actualTopPoints[i]}**\n"
    for i in range(len(actualTopID), 10):
        topList2 += f"__{i+1}.__\n"
    return topTitle + topList1 + topList2


@bot.event
async def on_ready():
    game = discord.Game("Praise BetaSugar")
    await bot.change_presence(activity=game)
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_member_remove(member):
    if member.guild.system_channel:
        await member.guild.system_channel.send(
            f"<@{member.id}> ({member.name}) ушел с сервера! [{currentTime()}]"
        )


@bot.command()
async def score(ctx):
    author = ctx.author
    try:
        for row in cursor.execute(f"Select points FROM detail where id={author.id}"):
            points_was = row[0]
        await ctx.send(f"{author} --> {points_was} лайков")
    except:
        await ctx.send(f"к сожалению, у {author} ни одного лайка")


@bot.command()
async def notifications(ctx):
    notif = False

    for roles in ctx.author.roles:
        if roles.id == int(config['discord']['notif_role_id']):
            notif = True
            role = roles
            break

    role = ctx.guild.get_role(int(config['discord']['notif_role_id']))
    if notif:
        await ctx.author.remove_roles(role)
    else:
        await ctx.author.add_roles(role)


@bot.command()
async def f(ctx):
    author_nick = ctx.author
    await ctx.send(type(ctx))


@bot.event
async def on_raw_reaction_add(payload):

    liker_id = payload.user_id  # айди лайкавшего(чтобы не засчитать айди бота)
    if liker_id == bot.user.id:
        return
    channel = bot.get_channel(payload.channel_id)  # получаем объект канала
    # получаем объект сообщения
    message = await channel.fetch_message(payload.message_id)
    author_ID = message.author.id  # автор залайконого поста
    # ник автора залайконого поста
    author_nick = await bot.fetch_user(author_ID)
    if liker_id == author_ID:
        return
    liker_nick = await bot.fetch_user(payload.user_id)
    list_of_ip = []
    cursor.execute("SELECT id FROM detail")
    massive_big = cursor.fetchall()
    for z in range(len(massive_big)):
        list_of_ip.append(massive_big[z][0])

    if payload.emoji.id == int(config['discord']['emoji_like_id']):  # лайк
        if author_ID not in list_of_ip:
            cursor.execute(
                f"Insert into detail VALUES ('{author_ID}', '{author_nick}','{0}')"
            )
            conn.commit()
        for row in cursor.execute(f"Select points FROM detail where id={author_ID}"):
            points_was = row[0]
        cursor.execute(
            f"UPDATE detail SET points = {points_was+1} WHERE id = {author_ID}"
        )
        conn.commit()
        print(
            f"[{currentTime()}] {liker_nick} dobavil {author_nick} +1 ({points_was}-->{points_was+1})"
        )

        channel_top = bot.get_channel(int(config['discord']['channel_top_id']))
        try:
            lstmessage = await channel_top.fetch_message(int(config['discord']['message_top_id']))
        except:
            try:
                lstmessage = await channel_top.fetch_message(
                    channel_top.last_message_id
                )
            except:
                await channel_top.send(f"Звёзды:")
            lstmessage = await channel_top.fetch_message(channel_top.last_message_id)
        actualTopID = []
        actualTopPoints = []
        for row in cursor.execute(f"Select id FROM detail ORDER BY points DESC"):
            actualTopID.append(row[0])
        for row in cursor.execute(f"Select points FROM detail ORDER BY points DESC"):
            actualTopPoints.append(row[0])

        await lstmessage.edit(content=top_PopularityStr(actualTopID, actualTopPoints))

    # дизлайк
    if payload.emoji.id == int(config['discord']['emoji_dislike_id']):
        if author_ID not in list_of_ip:
            cursor.execute(
                f"Insert into detail VALUES ('{author_ID}', '{author_nick}','{0}')"
            )
            conn.commit()
        for row in cursor.execute(f"Select points FROM detail where id={author_ID}"):
            points_was = row[0]
        cursor.execute(
            f"UPDATE detail SET points = {points_was-1} WHERE id = {author_ID}"
        )
        conn.commit()
        print(
            f"[{currentTime()}] {liker_nick} dobavil {author_nick} -1 ({points_was}-->{points_was-1})"
        )

        channel_top = bot.get_channel(int(config['discord']['channel_top_id']))
        try:
            lstmessage = await channel_top.fetch_message(int(config['discord']['message_top_id']))
        except:
            try:
                lstmessage = await channel_top.fetch_message(
                    channel_top.last_message_id
                )
            except:
                await channel_top.send(f"Звёзды:")
            lstmessage = await channel_top.fetch_message(channel_top.last_message_id)
        actualTopID = []
        actualTopPoints = []
        for row in cursor.execute(f"Select id FROM detail ORDER BY points DESC"):
            actualTopID.append(row[0])
        for row in cursor.execute(f"Select points FROM detail ORDER BY points DESC"):
            actualTopPoints.append(row[0])

        await lstmessage.edit(content=top_PopularityStr(actualTopID, actualTopPoints))


@bot.event
async def on_raw_reaction_remove(payload):

    liker_id = payload.user_id
    if liker_id == bot.user.id:
        return

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    author_ID = message.author.id
    author_nick = await bot.fetch_user(author_ID)

    if liker_id == author_ID:
        return

    liker_nick = await bot.fetch_user(payload.user_id)
    list_of_ip = []

    cursor.execute("SELECT id FROM detail")
    massive_big = cursor.fetchall()
    for z in range(len(massive_big)):
        list_of_ip.append(massive_big[z][0])

    if payload.emoji.id == int(config['discord']['emoji_like_id']):  # лайк
        if author_ID not in list_of_ip:
            cursor.execute(
                f"Insert into detail VALUES ('{author_ID}', '{author_nick}','{0}')"
            )
            conn.commit()
        for row in cursor.execute(f"Select points FROM detail where id={author_ID}"):
            points_was = row[0]
        cursor.execute(
            f"UPDATE detail SET points = {points_was-1} WHERE id = {author_ID}"
        )
        conn.commit()
        print(
            f"[{currentTime()}] {liker_nick} ubral {author_nick} +1 ({points_was}-->{points_was-1})"
        )

        channel_top = bot.get_channel(int(config['discord']['channel_top_id']))
        try:
            lstmessage = await channel_top.fetch_message(int(config['discord']['message_top_id']))
        except:
            try:
                lstmessage = await channel_top.fetch_message(
                    channel_top.last_message_id
                )
            except:
                await channel_top.send(f"Звёзды:")
            lstmessage = await channel_top.fetch_message(channel_top.last_message_id)
        actualTopID = []
        actualTopPoints = []
        for row in cursor.execute(f"Select id FROM detail ORDER BY points DESC"):
            actualTopID.append(row[0])
        for row in cursor.execute(f"Select points FROM detail ORDER BY points DESC"):
            actualTopPoints.append(row[0])

        await lstmessage.edit(content=top_PopularityStr(actualTopID, actualTopPoints))

    if payload.emoji.id == int(config['discord']['emoji_dislike_id']):  # дизлайк
        if author_ID not in list_of_ip:
            cursor.execute(
                f"Insert into detail VALUES ('{author_ID}', '{author_nick}','{0}')"
            )
            conn.commit()
        for row in cursor.execute(f"Select points FROM detail where id={author_ID}"):
            points_was = row[0]
        cursor.execute(
            f"UPDATE detail SET points = {points_was+1} WHERE id = {author_ID}"
        )
        conn.commit()
        print(
            f"[{currentTime()}] {liker_nick} ubral {author_nick} -1 ({points_was}-->{points_was+1})"
        )

        channel_top = bot.get_channel(int(config['discord']['channel_top_id']))
        try:
            lstmessage = await channel_top.fetch_message(int(config['discord']['message_top_id']))
        except:
            try:
                lstmessage = await channel_top.fetch_message(
                    channel_top.last_message_id
                )
            except:
                await channel_top.send(f"Звёзды:")
            lstmessage = await channel_top.fetch_message(channel_top.last_message_id)
        actualTopID = []
        actualTopPoints = []
        for row in cursor.execute(f"Select id FROM detail ORDER BY points DESC"):
            actualTopID.append(row[0])
        for row in cursor.execute(f"Select points FROM detail ORDER BY points DESC"):
            actualTopPoints.append(row[0])

        await lstmessage.edit(content=top_PopularityStr(actualTopID, actualTopPoints))


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.attachments or 'https://' in message.content:
        emojiLike = bot.get_emoji(int(config['discord']['emoji_like_id']))
        emojiDislike = bot.get_emoji(
            int(config['discord']['emoji_dislike_id']))
        await message.add_reaction(emojiLike)
        await message.add_reaction(emojiDislike)

config = getConfig('conf.ini')


#token = config['discord']['token']
#loop = asyncio.get_event_loop()
# loop.run_until_complete(bot.start(token))
bot.run(config['discord']['token'])
