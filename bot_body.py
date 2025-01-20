import discord
import asyncio

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # Запуск функции для чтения терминала
    asyncio.create_task(terminal_listener())


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


with open('token.txt') as r:
    token = r.read()

client.run(token)
