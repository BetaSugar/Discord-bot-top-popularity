import discord
import asyncio
import sqlite3
from datetime import datetime


# Соединение с базой данных
conn = sqlite3.connect('points.db')
cursor = conn.cursor()

# Создание таблицы, если её ещё нет
cursor.execute('''
CREATE TABLE IF NOT EXISTS points (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0
)
''')
conn.commit()
print('Соединение с базой данных установлено')

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # Запуск функции для чтения терминала
    asyncio.create_task(terminal_listener())


@client.event
async def on_member_remove(member):
    if member.guild.system_channel:
        await member.guild.system_channel.send(f"<@{member.id}> ({member.name}) ушел с сервера! [{currentTime()}]\nhttps://imgur.com/MMWbJZy")


@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Игнорировать сообщения от самого бота

    # Проверка, есть ли в сообщении медиа
    if message.attachments or 'https://' in message.content:
        # Ставим эмодзи
        like_emoji = '👍'
        dislike_emoji = '👎'
        await message.add_reaction(like_emoji)
        await message.add_reaction(dislike_emoji)


@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return  # Игнорировать реакции от самого бота

    if reaction.message.attachments:
        if reaction.emoji == '👍':
            increase_points(user.id, 1)
            print(f'{user.id} +1 {currentTime()}')
        elif reaction.emoji == '👎':
            increase_points(user.id, -1)
            print(f'{user.id} -1 {currentTime()}')


@client.event
async def on_reaction_remove(reaction, user):
    if user == client.user:
        return  # Игнорируем реакции от самого бота

    if reaction.message.attachments:
        if reaction.emoji == '👍':
            increase_points(user.id, -1)
            print(f'{user.id} -1 {currentTime()}')
        elif reaction.emoji == '👎':
            increase_points(user.id, 1)
            print(f'{user.id} +1 {currentTime()}')


def increase_points(user_id, delta):
    try:
        cursor.execute(
            'SELECT points FROM points WHERE id = ?', (user_id,))
        result = cursor.fetchone()

        if result:
            new_points = result[0] + delta
            cursor.execute(
                'UPDATE points SET points = ? WHERE id = ?', (new_points, user_id))
        else:
            cursor.execute(
                'INSERT INTO points (id, points) VALUES (?, ?)', (user_id, delta))

        conn.commit()
        print('изменение зафиксировано')
    except sqlite3.Error as e:
        print(f"Ошибка работы с базой данных: {e}")


async def terminal_listener():
    """
    Асинхронная функция для чтения ввода из терминала
    """

    await client.wait_until_ready()  # Дождаться, пока бот будет готов
    channel = client.get_channel(970562443078168619)  # Получить объект канала

    print("Введите сообщение, чтобы отправить его в канал. Напишите 'exit' для выхода.")
    while True:
        try:
            # Асинхронное чтение из терминала
            message = await asyncio.get_event_loop().run_in_executor(None, input)
            if message.lower() == "exit":
                print("Остановка бота...")
                await client.close()
                break
            if message.strip():  # Проверка, что сообщение не пустое
                await channel.send(message)
        except Exception as e:
            print(f"Ошибка: {e}")
            break


def currentTime():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


def topPopularityStr(actualTopID, actualTopPoints):
    topTitle = '**Звёзды:**\n'
    if len(actualTopID) > 9:
        topList = f'''🥇 <@{actualTopID[0]}> - **{actualTopPoints[0]}**
🥈 <@{actualTopID[1]}> - **{actualTopPoints[1]}**
🥉 <@{actualTopID[2]}> - **{actualTopPoints[2]}**
__4.__   <@{actualTopID[3]}> - **{actualTopPoints[3]}**
__5.__   <@{actualTopID[4]}> - **{actualTopPoints[4]}**
__6.__   <@{actualTopID[5]}> - **{actualTopPoints[5]}**
__7.__   <@{actualTopID[6]}> - **{actualTopPoints[6]}**
__8.__   <@{actualTopID[7]}> - **{actualTopPoints[7]}**
__9.__   <@{actualTopID[8]}> - **{actualTopPoints[8]}**
__10.__ <@{actualTopID[9]}> - **{actualTopPoints[9]}**'''
        return topTitle+topList
    topList1, topList2 = '', ''
    for i in range(len(actualTopID)):
        topList1 += f'__{i +
                         1}.__   <@{actualTopID[i]}> - **{actualTopPoints[i]}**\n'
    for i in range(len(actualTopID), 10):
        topList2 += f'__{i+1}.__\n'
    return topTitle+topList1+topList2


with open('token.txt') as r:
    token = r.read()

with open('top10.txt') as r:
    channel_id = r.read()

client.run(token)
