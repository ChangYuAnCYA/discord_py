import discord
from discord.ext import commands, tasks
from command import Command
from _1A2B import _1A2B
import pathlib
import random
import re
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import io
from io import BytesIO
import pandas as pd
import time
import asyncio
import datetime
import threading
# from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


class TestView(discord.ui.View):
    def __init__(self, client, _command):
        super().__init__()
        self.client = client
        self.command = _command

    @discord.ui.button(label="上一頁", style=discord.ButtonStyle.primary, emoji="◀", custom_id="previous")
    async def button_callback(self, button, ctx:discord.Interaction):
        num = self.command.btn_msg[1]
        # if num == 0:
        #     return
        embed = discord.Embed(
            title="圖片列表",
			description=self.command.btn_msg[0][num-1],
			colour=discord.Colour.blue()
        )
        embed.timestamp = datetime.datetime.now()
        # embed.description = "123456789"
        embed.set_footer(text="小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)

        # await ctx.message.edit(embed=embed)
        self.command.btn_msg[1] = num - 1
        if num - 1 == 0:
            button.disable = False
            await ctx.response.edit_message(embed=embed, view=self)
        else:
            if num != len(self.command.btn_msg[0])-1 and self.get_item("latter").disabled:
                self.get_item("latter").disabled = False
            await ctx.response.edit_message(embed=embed, view=self)
        # await ctx.response.autocomplete()
        
    @discord.ui.button(label="下一頁", style=discord.ButtonStyle.primary, emoji="▶", custom_id="latter")
    async def button_callback2(self, button, ctx:discord.Interaction):
        num = self.command.btn_msg[1]
        # if num == len(self.command.btn_msg[0])-1:
        #     return
        embed = discord.Embed(
            title="圖片列表",
			description=self.command.btn_msg[0][num+1],
			colour=discord.Colour.blue()
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        await ctx.message.edit(embed=embed)
        self.command.btn_msg[1] = num + 1
        # await ctx.response.autocomplete()
        if num + 1 == len(self.command.btn_msg[0])-1:
            button.disable = False
            await ctx.response.edit_message(embed=embed, view=self)
        else:
            if num != 0 and self.get_item("previous").disabled:
                self.get_item("previous").disabled = False
            await ctx.response.edit_message(embed=embed, view=self)
        # await ctx.response.edit_message(embed=embed)
        # await ctx.response.send_message(button.label, delete_after=0.1)

class Test(commands.Cog):
    def __init__(self, client, _1A2B_lst, command_lst, client_cmd_lst, mutex:threading.Lock):
        self.client = client
        self._1A2B_lst = _1A2B_lst
        self.command_lst = command_lst
        self.client_cmd_lst = client_cmd_lst
        self.mutex = mutex

    def create_embed(self, title=None, description=None, color=discord.Colour.blue()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed
    
    def nameClip(self, name:str):
        s = name
        for i, j in enumerate(s):
            if j == "(" or j == "（":
                s = s[:i]
                break
        return s

    @commands.command()
    async def 測試(self, ctx:discord.Interaction, message=None):
        _command = None
        for i in self.command_lst:
            if i.id == ctx.guild.id:
                _command = i

        lst = [i for i in _command.photo.keys()]
        string_lst = [f"{i}.{_command.photo[i]}" for i in lst]
        page_lst = []
        _command.btn_msg = [page_lst, 0]
        s = ""
        for i, j in enumerate(string_lst):
            s += j + "\n"
            if i == len(string_lst) - 1 and s != "":
                page_lst.append(s.strip())
            elif (i + 1) % 10 == 0:
                page_lst.append(s.strip())
                s = ""

        embed = discord.Embed(
            title="圖片列表",
			description=page_lst[0],
			colour=discord.Colour.blue()
        )
        embed.timestamp = datetime.datetime.now()
        # embed.description = "123456789"
        embed.set_footer(text="小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        await ctx.send(embed=embed, view=TestView(self.client, _command))

    @commands.command(name="查看", description = "確認 YOASOBI「アイドル」觀看次數")
    async def 查看(self, ctx:discord.Interaction):
        url = "https://www.youtube.com/watch?v=ZRtdQ81jPUQ"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        html = str(soup)
        rlt = re.search(r"觀看次數：.{1,30}次", html)[0]
        
        file = discord.File("./idol2.png", filename="image.png")
        embed = self.create_embed(title="YOASOBI「アイドル」 Official Music Video", description=rlt, color=discord.Color.gold())
        embed.set_image(url="attachment://image.png")
        print(embed.image.url)
        await ctx.send(embed=embed, file=file)

    @commands.command()
    async def test(self, ctx:discord.Interaction, message=None):
        mention = ctx.message.mentions[0]
        id_df = pd.read_csv(f"./id_card/{ctx.guild.id}.csv", index_col=None, encoding="cp950")
        val = id_df.index[id_df['member'] == mention.name].tolist()

        embed = self.create_embed(title=f"{self.nameClip(mention.display_name)} / 伺服器個人卡片", description="")
        if val != []:
            member, nickname, msg_count, emoji_count, last_msg, last_msg_time = id_df.loc[val[0]]
            identity = "幼兒"
            rank = ["幼兒", "幼稚園生", "小學生", "國中生", "高中生", "大學生", "碩士生", "博士生", "社會人"]
            range_lst = [1, 5, 10, 20, 50, 100, 200, 500, 100]
            lvlup = "Max"
            for i, j in enumerate(range_lst):
                if msg_count >= j:
                    identity = rank[i]
                else:
                    lvlup = j - msg_count
                    break

            join_time = mention.joined_at + datetime.timedelta(hours=8)
            join_time = join_time.replace(tzinfo=None)
            now = datetime.datetime.now()
            difference = now - join_time

            embed.set_author(name=mention.display_name, icon_url=mention.avatar.url)
            embed.description += f"ID: **__{mention.id}__**\n暱稱: **__{nickname}__**\n{'-'*10}個人資訊{'-'*10}"

            embed.add_field(name="下次升級", value=f"{lvlup}")
            embed.insert_field_at(0, name="身分", value=f"__{identity}__")
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="加入伺服器時間", value=join_time.strftime("%Y/%m/%d %H:%M:%S"), inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="待在伺服器的天數", value=f"{difference.days} 天", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="表情貼數量", value=emoji_count)
            embed.insert_field_at(10, name="訊息數量", value=msg_count)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="最新一則發的訊息", value=last_msg, inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="最後活躍時間", value=last_msg_time[:last_msg_time.find(".")], inline=False)
        else:
            embed.description = "目前無本人相關資訊"
        await ctx.send(embed=embed)