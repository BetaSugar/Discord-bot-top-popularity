import discord
import datetime
import sqlite3
import bot_config

intents = discord.Intents.default()
intents.members = True

now = datetime.datetime.now()
currentTime=now.strftime("%d-%m-%Y %H:%M:%S")
conn=sqlite3.connect("bot_base_points.db")   
cursor=conn.cursor()
try:
    cursor.execute('''CREATE TABLE detail (id int, nickname text, points int)''')
except:
    pass 

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_member_remove(member):
    if member.guild.system_channel:
        now = datetime.datetime.now()
        currentTime=now.strftime("%d-%m-%Y %H:%M:%S")
        await member.guild.system_channel.send(f"<@{member.id}> ушел с сервера! [{currentTime}]")    

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments or 'https://' in message.content:
        emojiLike= client.get_emoji(int(bot_config.emojiLikeId))
        emojiDislike= client.get_emoji(int(bot_config.emojiDislikeId))
        await message.add_reaction(emojiLike)
        await message.add_reaction(emojiDislike)


    if message.content.startswith('!счет'):
        try:
            for row in cursor.execute(f"Select points FROM detail where id={message.author.id}"):
                points_was=(row[0])
            author_nick=await client.fetch_user(message.author.id)
            await message.channel.send(f'{author_nick} --> {points_was} лайков')
        except:
            await message.channel.send(f'к сожалению, у {author_nick} ни одного лайка')

@client.event
async def on_raw_reaction_add(payload):

        liker_id=payload.user_id                                    # айди лайкавшего(чтобы не засчитать айди бота)
        if liker_id == client.user.id:                              
            return 
        channel = client.get_channel(payload.channel_id)            # получаем объект канала
        message = await channel.fetch_message(payload.message_id)   # получаем объект сообщения
        author_ID = message.author.id                               # автор залайконого поста
        author_nick=await client.fetch_user(author_ID)              # ник автора залайконого поста
        if liker_id == author_ID:                              
            return
        liker_nick=await client.fetch_user(payload.user_id)           
        list_of_ip=[]                                       
        cursor.execute('SELECT id FROM detail')                    
        massive_big = cursor.fetchall()
        for z in range(len(massive_big)):
            list_of_ip.append(massive_big[z][0])
                          
        if payload.emoji.id==int(bot_config.emojiLikeId):   #лайк                  
            if author_ID not in list_of_ip:
                cursor.execute(f"Insert into detail VALUES ('{author_ID}', '{author_nick}','{0}')")
                conn.commit()
            for row in cursor.execute(f"Select points FROM detail where id={author_ID}"):
                points_was=(row[0])
            cursor.execute(f"UPDATE detail SET points = {points_was+1} WHERE id = {author_ID}")
            conn.commit()
            now = datetime.datetime.now()
            currentTime=now.strftime("%d-%m-%Y %H:%M:%S")          
            print(f'[{currentTime}] {liker_nick} dobavil {author_nick} +1 ({points_was}-->{points_was+1})')

            channel_top = client.get_channel(int(bot_config.channelTopId))
            try:    lstmessage= await channel_top.fetch_message(int(bot_config.messageTopId))
            except:
                try:    lstmessage= await channel_top.fetch_message(channel_top.last_message_id)
                except: await channel_top.send(f'Звёзды подполья:')
                lstmessage= await channel_top.fetch_message(channel_top.last_message_id)
            actualTopID=[]
            actualTopPoints=[]
            for row in cursor.execute(f"Select id FROM detail ORDER BY points DESC"):
                actualTopID.append(row[0])
            for row in cursor.execute(f"Select points FROM detail ORDER BY points DESC"):
                actualTopPoints.append(row[0])

        
            await lstmessage.edit(content=f'''**Звёзды подполья:**
🥇 <@{actualTopID[0]}> - **{actualTopPoints[0]}**
🥈 <@{actualTopID[1]}> - **{actualTopPoints[1]}**
🥉 <@{actualTopID[2]}> - **{actualTopPoints[2]}**
__4.__   <@{actualTopID[3]}> - **{actualTopPoints[3]}**
__5.__   <@{actualTopID[4]}> - **{actualTopPoints[4]}**
__6.__   <@{actualTopID[5]}> - **{actualTopPoints[5]}**
__7.__   <@{actualTopID[6]}> - **{actualTopPoints[6]}**
__8.__   <@{actualTopID[7]}> - **{actualTopPoints[7]}**
__9.__   <@{actualTopID[8]}> - **{actualTopPoints[8]}**
__10.__ <@{actualTopID[9]}> - **{actualTopPoints[9]}**''')

        if payload.emoji.id==int(bot_config.emojiDislikeId):       #дизлайк            
            if author_ID not in list_of_ip:
                cursor.execute(f"Insert into detail VALUES ('{author_ID}', '{author_nick}','{0}')")
                conn.commit()
            for row in cursor.execute(f"Select points FROM detail where id={author_ID}"):
                points_was=(row[0])
            cursor.execute(f"UPDATE detail SET points = {points_was-1} WHERE id = {author_ID}")
            conn.commit()
            now = datetime.datetime.now()
            currentTime=now.strftime("%d-%m-%Y %H:%M:%S")          
            print(f'[{currentTime}] {liker_nick} dobavil {author_nick} -1 ({points_was}-->{points_was-1})') 

            channel_top = client.get_channel(int(bot_config.channelTopId))
            try:    lstmessage= await channel_top.fetch_message(int(bot_config.messageTopId))
            except:
                try:    lstmessage= await channel_top.fetch_message(channel_top.last_message_id)
                except: await channel_top.send(f'Звёзды подполья:')
                lstmessage= await channel_top.fetch_message(channel_top.last_message_id)
            actualTopID=[]
            actualTopPoints=[]
            for row in cursor.execute(f"Select id FROM detail ORDER BY points DESC"):
                actualTopID.append(row[0])
            for row in cursor.execute(f"Select points FROM detail ORDER BY points DESC"):
                actualTopPoints.append(row[0])

        
            await lstmessage.edit(content=f'''**Звёзды подполья:**
🥇 <@{actualTopID[0]}> - **{actualTopPoints[0]}**
🥈 <@{actualTopID[1]}> - **{actualTopPoints[1]}**
🥉 <@{actualTopID[2]}> - **{actualTopPoints[2]}**
__4.__   <@{actualTopID[3]}> - **{actualTopPoints[3]}**
__5.__   <@{actualTopID[4]}> - **{actualTopPoints[4]}**
__6.__   <@{actualTopID[5]}> - **{actualTopPoints[5]}**
__7.__   <@{actualTopID[6]}> - **{actualTopPoints[6]}**
__8.__   <@{actualTopID[7]}> - **{actualTopPoints[7]}**
__9.__   <@{actualTopID[8]}> - **{actualTopPoints[8]}**
__10.__ <@{actualTopID[9]}> - **{actualTopPoints[9]}**''') 

            
            
@client.event
async def on_raw_reaction_remove(payload):

        liker_id=payload.user_id                                    # айди лайкавшего(чтобы не считать айди бота)
        if liker_id == client.user.id:                              
            return 
        channel = client.get_channel(payload.channel_id)            # получаем объект канала
        message = await channel.fetch_message(payload.message_id)   # получаем объект сообщения
        author_ID = message.author.id                               # автор залайконого поста
        author_nick=await client.fetch_user(author_ID)              # ник автора залайконого поста
        if liker_id == author_ID:                              
            return
        liker_nick=await client.fetch_user(payload.user_id)
        list_of_ip=[]                                       
        cursor.execute('SELECT id FROM detail')                    
        massive_big = cursor.fetchall()
        for z in range(len(massive_big)):
            list_of_ip.append(massive_big[z][0])
                          
        if payload.emoji.id==int(bot_config.emojiLikeId):   #лайк                  
            if author_ID not in list_of_ip:
                cursor.execute(f"Insert into detail VALUES ('{author_ID}', '{author_nick}','{0}')")
                conn.commit()
            for row in cursor.execute(f"Select points FROM detail where id={author_ID}"):
                points_was=(row[0])
            cursor.execute(f"UPDATE detail SET points = {points_was-1} WHERE id = {author_ID}")
            conn.commit()
            now = datetime.datetime.now()
            currentTime=now.strftime("%d-%m-%Y %H:%M:%S")          
            print(f'[{currentTime}] {liker_nick} ubral {author_nick} +1 ({points_was}-->{points_was-1})')

            channel_top = client.get_channel(int(bot_config.channelTopId))
            try:    lstmessage= await channel_top.fetch_message(int(bot_config.messageTopId))
            except:
                try:    lstmessage= await channel_top.fetch_message(channel_top.last_message_id)
                except: await channel_top.send(f'Звёзды подполья:')
                lstmessage= await channel_top.fetch_message(channel_top.last_message_id)
            actualTopID=[]
            actualTopPoints=[]
            for row in cursor.execute(f"Select id FROM detail ORDER BY points DESC"):
                actualTopID.append(row[0])
            for row in cursor.execute(f"Select points FROM detail ORDER BY points DESC"):
                actualTopPoints.append(row[0])

        
            await lstmessage.edit(content=f'''**Звёзды подполья:**
🥇 <@{actualTopID[0]}> - **{actualTopPoints[0]}**
🥈 <@{actualTopID[1]}> - **{actualTopPoints[1]}**
🥉 <@{actualTopID[2]}> - **{actualTopPoints[2]}**
__4.__   <@{actualTopID[3]}> - **{actualTopPoints[3]}**
__5.__   <@{actualTopID[4]}> - **{actualTopPoints[4]}**
__6.__   <@{actualTopID[5]}> - **{actualTopPoints[5]}**
__7.__   <@{actualTopID[6]}> - **{actualTopPoints[6]}**
__8.__   <@{actualTopID[7]}> - **{actualTopPoints[7]}**
__9.__   <@{actualTopID[8]}> - **{actualTopPoints[8]}**
__10.__ <@{actualTopID[9]}> - **{actualTopPoints[9]}**''')


        if payload.emoji.id==int(bot_config.emojiDislikeId):       #дизлайк            
            if author_ID not in list_of_ip:
                cursor.execute(f"Insert into detail VALUES ('{author_ID}', '{author_nick}','{0}')")
                conn.commit()
            for row in cursor.execute(f"Select points FROM detail where id={author_ID}"):
                points_was=(row[0])
            cursor.execute(f"UPDATE detail SET points = {points_was+1} WHERE id = {author_ID}")
            conn.commit()
            now = datetime.datetime.now()
            currentTime=now.strftime("%d-%m-%Y %H:%M:%S")          
            print(f'[{currentTime}] {liker_nick} ubral {author_nick} -1 ({points_was}-->{points_was+1})')

            channel_top = client.get_channel(int(bot_config.channelTopId))
            try:    lstmessage= await channel_top.fetch_message(int(bot_config.messageTopId))
            except:
                try:    lstmessage= await channel_top.fetch_message(channel_top.last_message_id)
                except: await channel_top.send(f'Звёзды подполья:')
                lstmessage= await channel_top.fetch_message(channel_top.last_message_id)
            actualTopID=[]
            actualTopPoints=[]
            for row in cursor.execute(f"Select id FROM detail ORDER BY points DESC"):
                actualTopID.append(row[0])
            for row in cursor.execute(f"Select points FROM detail ORDER BY points DESC"):
                actualTopPoints.append(row[0])

        
            await lstmessage.edit(content=f'''**Звёзды подполья:**
🥇 <@{actualTopID[0]}> - **{actualTopPoints[0]}**
🥈 <@{actualTopID[1]}> - **{actualTopPoints[1]}**
🥉 <@{actualTopID[2]}> - **{actualTopPoints[2]}**
__4.__   <@{actualTopID[3]}> - **{actualTopPoints[3]}**
__5.__   <@{actualTopID[4]}> - **{actualTopPoints[4]}**
__6.__   <@{actualTopID[5]}> - **{actualTopPoints[5]}**
__7.__   <@{actualTopID[6]}> - **{actualTopPoints[6]}**
__8.__   <@{actualTopID[7]}> - **{actualTopPoints[7]}**
__9.__   <@{actualTopID[8]}> - **{actualTopPoints[8]}**
__10.__ <@{actualTopID[9]}> - **{actualTopPoints[9]}**''')


client.run(bot_config.TOKEN)

