import discord
import asyncio
import sqlite3
from datetime import datetime


# Соединение с базой данных
conn = sqlite3.connect('reputation.db')
cursor = conn.cursor()

# Создание таблицы, если её ещё нет
cursor.execute('''
CREATE TABLE IF NOT EXISTS reputation (
    user_id INTEGER PRIMARY KEY,
    reputation INTEGER DEFAULT 0
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
            increase_reputation(user.id, 1)
            print(f'{user.id} +1 {currentTime()}')
        elif reaction.emoji == '👎':
            increase_reputation(user.id, -1)
            print(f'{user.id} -1 {currentTime()}')


@client.event
async def on_reaction_remove(reaction, user):
    if user == client.user:
        return  # Игнорируем реакции от самого бота

    if reaction.message.attachments:
        if reaction.emoji == '👍':
            increase_reputation(user.id, -1)
            print(f'{user.id} -1 {currentTime()}')
        elif reaction.emoji == '👎':
            increase_reputation(user.id, 1)
            print(f'{user.id} +1 {currentTime()}')


def increase_reputation(user_id, delta):
    try:
        cursor.execute(
            'SELECT reputation FROM reputation WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()

        if result:
            new_reputation = result[0] + delta
            cursor.execute(
                'UPDATE reputation SET reputation = ? WHERE user_id = ?', (new_reputation, user_id))
        else:
            cursor.execute(
                'INSERT INTO reputation (user_id, reputation) VALUES (?, ?)', (user_id, delta))

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


with open('token.txt') as r:
    token = r.read()

with open('top10.txt') as r:
    channel_id = r.read()

client.run(token)
