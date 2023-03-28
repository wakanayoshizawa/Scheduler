# coding: utf-8

import os
import re
import datetime
import discord
import pandas as pd

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

client = discord.Client()

reaction_list = {
    0: '1️⃣',
    1: '2️⃣',
    2: '3️⃣',
    3: '4️⃣',
    4: '5️⃣',
    5: '6️⃣',
    6: '7️⃣',
    7: '8️⃣',
    8: '9️⃣',
    9: '🔟',
}

reaction_list_num = {
    0: '1',
    1: '2',
    2: '3',
    3: '4',
    4: '5',
    5: '6',
    6: '7',
    7: '8',
    8: '9',
    9: '10',
}

week_list = {
    0: '日',
    1: '月',
    2: '火',
    3: '水',
    4: '木',
    5: '金',
    6: '土',
}

"""
起動イベント
"""
@client.event
async def on_ready():
    print('BOT起動')
    await client.change_presence(activity=discord.Game(name="/scheduler", type=1))

"""
テキストイベント
"""
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith('/scheduler'):
        title = message.content.split(None, 2)
        if len(title) < 3:
            await message.channel.send('Error: `/scheduler Title MMDDHHmm MMDDHHmm` と入力してください')
            return

        command = title[2].split()
        if len(command) > len(reaction_list):
            await message.channel.send('Error: 日時の引数は最大で{}個までです'.format(str(len(reaction_list))))
            return
        
        description = ''
        for i, x in enumerate(command):            
            try:
                now = datetime.datetime.now()
                date = pd.to_datetime(str(now.year) + str(x), format='%Y%m%d%H%M')
                if int(now.month) > int(x[0:2]):
                    date = pd.to_datetime(str(int(now.year) + 1) + str(x), format='%Y%m%d%H%M')
                description += '{} {}月{}日({}) {}:{}〜\n'.format(reaction_list[i], date.month, date.day, week_list[int(date.strftime('%w'))], date.hour, str(date.minute).zfill(2))

            except:
                await message.channel.send('Error: 日時は8桁の数字でフォーマットは `MMDDHHmm` です')
                return

        embed = discord.Embed(title=title[1], description=description, color=0xff0000)
        bot_message = await message.channel.send(embed=embed)
        for i, x in enumerate(command):
            await bot_message.add_reaction(reaction_list[i])
        
        return

    if message.reference:
        if message.content.startswith('/done'):
            content = message.content.split(None, 1)
            channel = client.get_channel(message.reference.channel_id)
            origin_message = await channel.fetch_message(message.reference.message_id)
            if client.user == origin_message.author:
                try:
                    mention = ''
                    reaction_num = [i for i, x in reaction_list_num.items() if x == content[1]][0]
                    reaction = origin_message.reactions[reaction_num]
                    users = await reaction.users().flatten()
                    for user in users:
                        if not user.bot:
                            mention += '<@!{}> '.format(user.id)
                    embed = origin_message.embeds[0].to_dict()
                    description = embed['description'].splitlines()[reaction_num]
                    plan = [i for i in re.split('\D', description[3:]) if i != '']
                    now = datetime.datetime.now()
                    date = pd.to_datetime(str(now.year) + str(plan[0]).zfill(2) + str(plan[1]).zfill(2) + str(plan[2]).zfill(2) + str(plan[3]).zfill(2), format='%Y%m%d%H%M')
                    if int(now.month) > int(plan[0]):
                        date = pd.to_datetime(str(int(now.year) + 1) + str(plan[0]).zfill(2) + str(plan[1]).zfill(2) + str(plan[2]).zfill(2) + str(plan[3]).zfill(2), format='%Y%m%d%H%M')
                    google = 'https://www.google.com/calendar/render?action=TEMPLATE&text={}&dates={}/{}'.format(embed['title'], date.strftime('%Y%m%dT%H%M%S'), (date + datetime.timedelta(hours=1)).strftime('%Y%m%dT%H%M%S'))
                    await message.channel.send('> {}\n{}\n{} **{}**に決定しました！\n\nGoogleカレンダーに追加する: {}'.format(origin_message.jump_url, mention, embed['title'], description, google))
                except:
                    await message.channel.send('Error: 決定した日付番号を `/done {}` と入力してください'.format(reaction_list_num[0]))
                    return

        return

client.run(TOKEN)