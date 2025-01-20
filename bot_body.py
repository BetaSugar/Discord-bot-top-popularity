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

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # Запуск функции для чтения терминала
    asyncio.create_task(terminal_listener())
    asyncio.create_task(update_top_10())


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


async def update_top_10():
    global top_message_id

    while True:
        # Получаем топ-10 пользователей по репутации
        cursor.execute(
            'SELECT user_id, reputation FROM reputation ORDER BY reputation DESC LIMIT 10')
        top_users = cursor.fetchall()

        # Формируем текст топа
        top_text = "Топ 10 пользователей с наибольшей репутацией:\n"
        for idx, (user_id, reputation) in enumerate(top_users, 1):
            user = await client.fetch_user(user_id)
            top_text += f"{idx}. {user.name} - {reputation} репутации\n"

        # Получаем канал для отправки топа
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            if top_message_id:
                # Если ID сообщения с топом уже есть, редактируем это сообщение
                try:
                    top_message = await channel.fetch_message(top_message_id)
                    await top_message.edit(content=top_text)
                except discord.NotFound:
                    # В случае, если сообщение не найдено (например, оно было удалено)
                    print("Предыдущее сообщение с топом не найдено.")
                    top_message_id = None
            else:
                # Если сообщение с топом еще не отправлено, отправляем новое
                top_message = await channel.send(top_text)
                top_message_id = top_message.id

        # Ждем 5 минут (300 секунд) до следующего обновления
        await asyncio.sleep(300)


# Глобальная переменная для хранения ID сообщения с топом
top_message_id = None


def currentTime():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


with open('token.txt') as r:
    token = r.read()

with open('top10.txt') as r:
    CHANNEL_ID = r.read()

client.run(token)
