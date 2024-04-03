import configparser
import sqlite3
import datetime
import discord
from discord.ext import commands
import asyncio


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


conn = sqlite3.connect("bot_base_points.db")
cursor = conn.cursor()

cursor.execute(
    """CREATE TABLE if not exists detail (id int, nickname text, points int)""")


def create_config(path):

    # Create a config file

    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section('discord')
    config.add_section('wasd.tv')
    config.add_section('twitch.tv')
    config.set('discord', 'token', '')
    config.set('discord', '#ID like and dislike emojis')
    config.set('discord', 'emoji_like_id', '')
    config.set('discord', 'emoji_dislike_id', '')
    config.set('discord',
               '#ID of the channel and the message-top that is stored in this channel')
    config.set('discord', 'channel_top_id', '')
    config.set('discord', 'message_top_id', '')
    config.set('discord', '#ID role for notifications')
    config.set('discord', 'notif_role_id', '')

    with open(path, 'w') as conf:
        config.write(conf)
    return config


async def current_time():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


def top_popularity_str(actual_top_id: list, actual_top_points: list):
    top_title = "**Звёзды:**\n"
    if len(actual_top_id) > 9:
        top_list = f"""🥇 <@{actual_top_id[0]}> - **{actual_top_points[0]}**
                        🥈 <@{actual_top_id[1]}> - **{actual_top_points[1]}**
                        🥉 <@{actual_top_id[2]}> - **{actual_top_points[2]}**
                        __4.__   <@{actual_top_id[3]}> - **{actual_top_points[3]}**
                        __5.__   <@{actual_top_id[4]}> - **{actual_top_points[4]}**
                        __6.__   <@{actual_top_id[5]}> - **{actual_top_points[5]}**
                        __7.__   <@{actual_top_id[6]}> - **{actual_top_points[6]}**
                        __8.__   <@{actual_top_id[7]}> - **{actual_top_points[7]}**
                        __9.__   <@{actual_top_id[8]}> - **{actual_top_points[8]}**
                        __10.__ <@{actual_top_id[9]}> - **{actual_top_points[9]}**"""
        return top_title + top_list
    top_list1, top_list2 = "", ""
    for i in range(len(actual_top_id)):
        top_list1 += f"__{i+1}.__   <@{actual_top_id[i]}> - **{actual_top_points[i]}**\n"
    for i in range(len(actual_top_id), 10):
        top_list2 += f"__{i+1}.__\n"
    return top_title + top_list1 + top_list2


async def get_info_database(request: str):
    global cursor
    answer = None
    for row in cursor.execute(request):
        answer = row[0]
    return answer


async def update_database(author_id: int, author_name: str, value: int):
    global cursor
    list_of_ip = []
    cursor.execute("SELECT id FROM detail")
    massive_big = cursor.fetchall()
    for i in range(len(massive_big)):
        list_of_ip.append(massive_big[i][0])

    if author_id not in list_of_ip:
        cursor.execute(
            f"Insert into detail VALUES ('{author_id}', '{author_name}','{0}')")
        conn.commit()

    for row in cursor.execute(f"Select points FROM detail where id={author_id}"):
        points_was = row[0]
    cursor.execute(
        f"UPDATE detail SET points = {points_was+value} WHERE id = {author_id}")
    conn.commit()
    if config['discord'].getboolean('channel_logs'):
        update_logs(
            f"[{current_time()}] Update score {author_name} {value} ({points_was}-->{points_was+value})")


async def update_logs(message: str):
    if config['discord'].getboolean('channel_logs'):
        channel = bot.get_channel(config['discord']['channel_log_id'])
        await channel.send(message)


@bot.event
async def on_ready():
    game = discord.Game("Praise BetaSugar")
    await bot.change_presence(activity=game)
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_member_remove(member):
    if member.guild.system_channel:
        await member.guild.system_channel.send(
            f"<@{member.id}> ({member.name}) ушел с сервера! [{current_time()}]"
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
    author_name = ctx.author
    await ctx.send(type(ctx))


@bot.event
async def on_raw_reaction_add(payload):

    liker_id = payload.user_id  # айди лайкавшего(чтобы не засчитать айди бота)
    if liker_id == bot.user.id:
        return
    # получаем объект канала
    channel = bot.get_channel(payload.channel_id)
    # получаем объект сообщения
    message = await channel.fetch_message(payload.message_id)
    # автор залайконого поста
    author_id = message.author.id
    # ник автора залайконого поста
    if liker_id == author_id:
        return
    author_name = await bot.fetch_user(author_id)
    liker_nick = await bot.fetch_user(payload.user_id)

    if config['discord'].getboolean('custom_like_emojis'):
        if payload.emoji.id == int(config['discord']['emoji_like_id']):
            update_database(author_id, author_name, 1)
            if config['discord'].getboolean('channel_top'):
                channel_top = bot.get_channel(
                    int(config['discord']['channel_top_id']))

                try:
                    lstmessage = await channel_top.fetch_message(int(config['discord']['message_top_id']))
                except:
                    await channel_top.send(f"Звёзды:")

                lstmessage = await channel_top.fetch_message(channel_top.last_message_id)

                actual_top_id = get_info_database(
                    f'Select id FROM detail ORDER BY points DESC')
                actual_top_points = get_info_database(
                    f'Select points FROM detail ORDER BY points DESC')

                await lstmessage.edit(content=top_popularity_str(actual_top_id, actual_top_points))

        if payload.emoji.id == int(config['discord']['emoji_dislike_id']):
            update_database(author_id, author_name, -1)
            if config['discord'].getboolean('channel_top'):
                channel_top = bot.get_channel(
                    int(config['discord']['channel_top_id']))

                try:
                    lstmessage = await channel_top.fetch_message(int(config['discord']['message_top_id']))
                except:
                    await channel_top.send(f"Звёзды:")

                lstmessage = await channel_top.fetch_message(channel_top.last_message_id)

                actual_top_id = get_info_database(
                    f'Select id FROM detail ORDER BY points DESC')
                actual_top_points = get_info_database(
                    f'Select points FROM detail ORDER BY points DESC')

                await lstmessage.edit(content=top_popularity_str(actual_top_id, actual_top_points))


@bot.event
async def on_raw_reaction_remove(payload):

    liker_id = payload.user_id  # айди лайкавшего(чтобы не засчитать айди бота)
    if liker_id == bot.user.id:
        return
    # получаем объект канала
    channel = bot.get_channel(payload.channel_id)
    # получаем объект сообщения
    message = await channel.fetch_message(payload.message_id)
    # автор залайконого поста
    author_id = message.author.id
    # ник автора залайконого поста
    if liker_id == author_id:
        return
    author_name = await bot.fetch_user(author_id)
    liker_nick = await bot.fetch_user(payload.user_id)

    if config['discord'].getboolean('custom_like_emojis'):
        if payload.emoji.id == int(config['discord']['emoji_like_id']):
            update_database(author_id, author_name, -1)
            if config['discord'].getboolean('channel_top'):
                channel_top = bot.get_channel(
                    int(config['discord']['channel_top_id']))

                try:
                    lstmessage = await channel_top.fetch_message(int(config['discord']['message_top_id']))
                except:
                    await channel_top.send(f"Звёзды:")

                lstmessage = await channel_top.fetch_message(channel_top.last_message_id)

                actual_top_id = get_info_database(
                    f'Select id FROM detail ORDER BY points DESC')
                actual_top_points = get_info_database(
                    f'Select points FROM detail ORDER BY points DESC')

                await lstmessage.edit(content=top_popularity_str(actual_top_id, actual_top_points))

        if payload.emoji.id == int(config['discord']['emoji_dislike_id']):
            update_database(author_id, author_name, 1)
            if config['discord'].getboolean('channel_top'):
                channel_top = bot.get_channel(
                    int(config['discord']['channel_top_id']))

                try:
                    lstmessage = await channel_top.fetch_message(int(config['discord']['message_top_id']))
                except:
                    await channel_top.send(f"Звёзды:")

                lstmessage = await channel_top.fetch_message(channel_top.last_message_id)

                actual_top_id = get_info_database(
                    f'Select id FROM detail ORDER BY points DESC')
                actual_top_points = get_info_database(
                    f'Select points FROM detail ORDER BY points DESC')

                await lstmessage.edit(content=top_popularity_str(actual_top_id, actual_top_points))


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.attachments or 'https://' in message.content:
        emojiLike = bot.get_emoji(int(config['discord']['emoji_like_id']))
        emojiDislike = bot.get_emoji(
            int(config['discord']['emoji_dislike_id']))
        await message.add_reaction(emojiLike)
        await message.add_reaction(emojiDislike)


try:
    config = configparser.ConfigParser()
    config.read('conf.ini')
except:
    config = create_config('conf.ini')


#token = config['discord']['token']
#loop = asyncio.get_event_loop()
# loop.run_until_complete(bot.start(token))
bot.run(config['discord']['token'])
