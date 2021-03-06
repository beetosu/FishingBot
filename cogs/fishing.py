import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time, math, random
import sqlite3
import asyncio
import data, playerdb
from numpy.random import choice

class Fishing(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('[SYSTEM] fishing is online')

    #the actual, like fishing
    @commands.command()
    async def fish(self, ctx):
        await ctx.send('reel casted!')
        conn_p = sqlite3.connect('databases/players.db')
        cur_p = conn_p.cursor()
        player = playerdb.get_player(ctx)
        #how long to wait before something bites
        for i in player:
            rod = i[1]
            reel = int(i[3]) - 1
            money = i[5]
            points = i[6]
        time.sleep(random.randint(int(10/data.rods[rod]["attraction"]), int(20/data.rods[rod]["attraction"])))
        await ctx.send(f'{ctx.author.mention}! something\'s on the line!\ntype "catch" to reel it in!')
        #what fish is caught, based on rarity
        catch = choice(data.fish_types[reel], 1, data.fish_odds[reel])[0]
        #the time something is caught
        baseTime = datetime.now()
        #makes sure the message is correct
        def catch_check(msg):
            return msg.content == "catch"
        try:
            #hold until catch is typed by the user or a minute passes
            #[does this take into account author??]
            resp = await self.client.wait_for('message', check=catch_check, timeout=60.0)
        except asyncio.TimeoutError:
            #if a minute passes, the fish leaves
            await ctx.send("oop it went away")
        else:
            #the odds of catching are calculated based on response time
            odds = math.exp(-(datetime.now() - baseTime).total_seconds()/25) * data.rods[rod]["catch"]
            if random.random() < odds:
                new_coins = str(money + catch["money"])
                new_points = str(points + catch["points"])
                cur_p.execute('UPDATE users SET money = ' + new_coins + ', points = ' + new_points + ' WHERE id ="' + str(ctx.author.id) + "_" + str(ctx.guild.id) + '"')
                conn_p.commit()
                conn_p.close()
                await ctx.send(f'{catch["emoji"]}')
                await ctx.send(f'you caught a {catch["name"]}!\n{catch["points"]} points earned\n{catch["money"]} money earned')
            else:
                await ctx.send(f'the fish has escaped <a:donkeysad:691789600540196914>')


def setup(client):
    client.add_cog(Fishing(client))
