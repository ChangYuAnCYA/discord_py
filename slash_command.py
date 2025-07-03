import discord
from discord.ext import commands, tasks
from command import Command
from _1A2B import _1A2B
import pathlib
import random
import re
import os
import io
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from io import BytesIO
import pandas as pd
import time
import asyncio
import datetime
import sqlite3
import threading
import numpy as np
import cv2
from skimage.metrics import peak_signal_noise_ratio as compare_psnr
from skimage.metrics import mean_squared_error as compare_mse
from skimage.metrics import structural_similarity as compare_ssim

import discord_colorize

# import diffusion
# import anything
import stock

class btnManager:
    def __init__(self, name):
        self.name = name

    async def button_callback(self, ctx:discord.Interaction):
        await ctx.response.send_message(self.name, ephemeral=True)

class View(discord.ui.View):
    def __init__(self, client, _command):
        super().__init__()
        self.client = client
        self.command = _command

class helpView_command(discord.ui.View):
    def __init__(self, client, _command):
        super().__init__()
        self.client = client
        self.command = _command
        self.help = {"$new1A2B {數字}":"開啟位數為{數字}的1A2B遊戲", 
                     "$sudoDel":"回覆特定訊息，自動刪除該訊息以後的所有訊息，需具有特定權限。", 
                     "$count":"列出所有身分組與其人數。", 
                     "$c":"切換機器人設置訊息是否啟用的開關，需具有特定權限。", 
                     "$set @someone {設置內容}":"設置機器人對@someone回覆{設置內容}，設置內容留空即為刪除回覆訊息。", 
                     "$d {數字(可不填，預設30)}":"檢索當前訊息以前{數字}筆的訊息，並將其中是機器人的發言或是純數字訊息刪掉。", 
                     "$cal":"回覆特定訊息，自動計算該訊息以後的圖片所有表情貼的數量，並扣掉重複的人。", 
                     "$bill @someone":"會列出利用該用戶含有'茜'的對話產生的帳單，留空只有次數和總額。", 
                     "$m {4-22任意整數(可不填)}":"回覆任意訊息，並根據所填數字設定一行之字數及自動縮放字級，以產生該訊息內容的圖片。須注意貼圖和表情符號無法正常使用。(字型由魚大和夕葉提供)", 
                     "$p @someone":"回覆訊息或@someone，可取得該使用者頭貼原圖。", 
                     "設定圖片 {圖片名字} {附件(jpg, pnd, gif)}":"提供圖片名字並添加附件，以在發送訊息時添加關鍵字{圖片名字}", 
                    }

    def create_embed(self, title=None, description=None, color=discord.Colour.nitro_pink()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    @discord.ui.select(
        placeholder = "請選擇想要查詢的指令",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="$new1A2B {數字}",
                description="點擊以查看指令$new1A2B內容!"
            ),
            discord.SelectOption(
                label="$sudoDel",
                description="點擊以查看指令$sudoDel內容!"
            ), 
            discord.SelectOption(
                label="$count",
                description="點擊以查看指令$count內容!"
            ), 
            discord.SelectOption(
                label="$c",
                description="點擊以查看指令$c內容!"
            ), 
            discord.SelectOption(
                label="$set @someone {設置內容}",
                description="點擊以查看指令$set內容!"
            ), 
            discord.SelectOption(
                label="$d {數字(可不填，預設30)}",
                description="點擊以查看指令$d內容!"
            ), 
            discord.SelectOption(
                label="$cal",
                description="點擊以查看指令$cal內容!"
            ), 
            discord.SelectOption(
                label="$bill @someone",
                description="點擊以查看指令$bill內容!"
            ), 
            discord.SelectOption(
                label="$m {4-22任意整數(可不填)}",
                description="點擊以查看指令$m內容!"
            ), 
            discord.SelectOption(
                label="$p @someone",
                description="點擊以查看指令$p內容!"
            ), 
        ])
    async def select_callback(self, select, ctx:discord.Interaction):
        embed = self.create_embed(title=select.values[0], description=self.help[select.values[0]])
        await ctx.response.send_message(embed=embed, ephemeral=True)

class helpView_slash_command(discord.ui.View):
    def __init__(self, client, _command):
        super().__init__()
        self.client = client
        self.command = _command
        self.help = {
                     "/設定獲得身分組訊息":"設定可以獲得身分組的訊息", 
                     "/取得頭貼":"@使用者以獲得頭貼", 
                     "/刪除機器人指令":"指定數量，檢索當前訊息以前指定數量的訊息，刪除其中機器人指令", 
                     "/設置成員訊息":"設置機器人對@someone回覆{設置內容}，設置內容留空即為刪除回覆訊息。", 
                     "/更改字型":"更改$m的字型", 
                     "/隨機身分組抽籤":"標註身分組並指定數量，可以根據設定隨機抽籤", 
                     "/設定新成員歡迎訊息":"可指定稱謂(預設成員)，並設置自訂新成員歡迎訊息", 
                     "/查看新成員歡迎訊息":"查看目前設定之新成員歡迎訊息", 
                     "/設定圖片":"提供圖片名字並添加附件，以在發送訊息時添加關鍵字{圖片名字}", 
                     "/查詢圖片列表":"可查詢發送訊息會觸發的關鍵字圖片列表", 
                     "/刪除圖片":"可刪除發送訊息會觸發的關鍵字圖片", 
                     "/查詢伺服器個人卡片":"@someone即可查詢伺服器個人卡片", 
                     "/設定伺服器個人卡片暱稱":"@someone即可設定伺服器個人卡片暱稱", 
                     "/查詢伺服器個人卡片排行榜":"可查詢伺服器個人卡片排行榜",
                     "/查看個人運勢":"可查看今日運勢，一人一天最多只能使用3次。\n如果抽中大吉好像會發生什麼事...？", 
                     "/我喜歡妳":"勇敢跟小夕葉告白\n看看會不會被接受吧！", 
                     "/查詢我喜歡妳回答列表":"可查看小夕葉可能會有的答覆...？", 
                     "/設定系統身分組":"可設定/查看個人運勢抽中大吉添加之身分組", 
                     "/查看系統身分組":"可查看/查看個人運勢抽中大吉添加之身分組", 
                     "/切換刪除訊息狀態":"可以設定用戶刪除訊息時，是否由機器人重傳", 
                     "/設置新成員歡迎圖片":"可以設置新成員加入時顯示的圖片", 
                     "/刪除設置之新成員歡迎圖片":"可以刪除字型設置之新成員加入時顯示的圖片",
                     "/設置新成員歡迎圖片頭貼位置參數":"可以設置新成員加入時顯示的圖片中，新成員頭像的位置參數",
                     "/查詢新成員歡迎圖片頭貼位置參數":"可以查詢新成員加入時顯示的圖片中，新成員頭像的位置參數",
                     "/測試新成員歡迎圖片效果":"可以預覽新成員加入時顯示的圖片"
                    }
        # "/set_channel":"設定 YOASOBI「アイドル」觀看次數 頻道", 
        # "/clean_channel":"清除 YOASOBI「アイドル」觀看次數 頻道", 
        # "/check":"確認 YOASOBI「アイドル」觀看次數", 
        # "/clock_start":"開始定時傳送「アイドル」觀看次數訊息", 
        # "/clock_end":"停止定時傳送「アイドル」觀看次數訊息", 

    def create_embed(self, title=None, description=None, color=discord.Colour.nitro_pink()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    @discord.ui.select(
        placeholder = "請選擇想要查詢的指令",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="/取得頭貼",
                description="點擊以查看指令/取得頭貼內容!"
            ), 
            discord.SelectOption(
                label="/刪除機器人指令",
                description="點擊以查看指令/刪除機器人指令內容!"
            ), 
            discord.SelectOption(
                label="/設置成員訊息",
                description="點擊以查看指令/設置成員訊息內容!"
            ), 
            discord.SelectOption(
                label="/更改字型",
                description="點擊以查看指令/更改字型內容!"
            ), 
            discord.SelectOption(
                label="/隨機身分組抽籤",
                description="點擊以查看指令/隨機身分組抽籤內容!"
            ), 
            discord.SelectOption(
                label="/查看新成員歡迎訊息",
                description="點擊以查看指令/查看新成員歡迎訊息內容!"
            ), 
            discord.SelectOption(
                label="/設定圖片",
                description="點擊以查看指令/設定圖片內容!"
            ), 
            discord.SelectOption(
                label="/查詢圖片列表",
                description="點擊以查看指令/查詢圖片列表內容!"
            ), 
            discord.SelectOption(
                label="/刪除圖片",
                description="點擊以查看指令/刪除圖片內容!"
            ), 
            discord.SelectOption(
                label="/查詢伺服器個人卡片",
                description="點擊以查看指令/查詢伺服器個人卡片內容!"
            ), 
            discord.SelectOption(
                label="/設定伺服器個人卡片暱稱",
                description="點擊以查看指令/設定伺服器個人卡片暱稱內容!"
            ), 
            discord.SelectOption(
                label="/查詢伺服器個人卡片排行榜",
                description="點擊以查看指令/查詢伺服器個人卡片排行榜內容!"
            ), 
            discord.SelectOption(
                label="/查看個人運勢",
                description="點擊以查看指令/查看個人運勢內容!"
            ), 
            discord.SelectOption(
                label="/我喜歡妳",
                description="點擊以查看指令/我喜歡妳內容!"
            ), 
            discord.SelectOption(
                label="/查詢我喜歡妳回答列表",
                description="點擊以查看指令/查詢我喜歡妳回答列表內容!"
            ), 
            discord.SelectOption(
                label="/設定系統身分組",
                description="點擊以查看指令/設定系統身分組內容!"
            ), 
            discord.SelectOption(
                label="/查看系統身分組",
                description="點擊以查看指令/查看系統身分組內容!"
            ),
            discord.SelectOption(
                label="/切換刪除訊息狀態",
                description="點擊以查看指令/切換刪除訊息狀態!"
            ), 
            discord.SelectOption(
                label="/設置新成員歡迎圖片",
                description="點擊以查看指令/設置新成員歡迎圖片!"
            ), 
            discord.SelectOption(
                label="/刪除設置之新成員歡迎圖片",
                description="點擊以查看指令/刪除設置之新成員歡迎圖片!"
            ), 
            discord.SelectOption(
                label="/設置新成員歡迎圖片頭貼位置參數",
                description="點擊以查看指令/設置新成員歡迎圖片頭貼位置參數!"
            ), 
            discord.SelectOption(
                label="/查詢新成員歡迎圖片頭貼位置參數",
                description="點擊以查看指令/查詢新成員歡迎圖片頭貼位置參數!"
            ), 
            discord.SelectOption(
                label="/測試新成員歡迎圖片效果",
                description="點擊以查看指令/測試新成員歡迎圖片效果!"
            )
        ])
            # discord.SelectOption(
            #     label="/set_channel",
            #     description="點擊以查看指令/set_channel內容!"
            # ),
            # discord.SelectOption(
            #     label="/clean_channel",
            #     description="點擊以查看指令/clean_channel內容!"
            # ), 
            # discord.SelectOption(
            #     label="/check",
            #     description="點擊以查看指令/check內容!"
            # ), 
            # discord.SelectOption(
            #     label="/clock_start",
            #     description="點擊以查看指令/clock_start內容!"
            # ), 
            # discord.SelectOption(
            #     label="/clock_end",
            #     description="點擊以查看指令/clock_end內容!"
            # ), 
    async def select_callback(self, select, ctx:discord.Interaction):
        embed = self.create_embed(title=select.values[0], description=self.help[select.values[0]])
        await ctx.response.send_message(embed=embed, ephemeral=True)

class selectView(discord.ui.View):
    def __init__(self, client, _command):
        super().__init__()
        self.client = client
        self.command = _command

    def create_embed(self, title=None, description=None, color=discord.Colour.blue()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    @discord.ui.select(
        placeholder = "--------------------",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="$指令",
                description="點擊以查看$指令內容！"
            ),
            discord.SelectOption(
                label="/指令",
                description="點擊以查看/指令內容！"
            )
        ])
    async def select_callback(self, select, ctx:discord.Interaction):
        embed = self.create_embed(title=select.values[0], description=f"使用選單以查詢 {select.values[0]}", color=discord.Colour.nitro_pink())
        if select.values[0] == "$指令":
            await ctx.response.send_message(embed=embed, view=helpView_command(self.client, self.command), ephemeral=True)
        else:
            await ctx.response.send_message(embed=embed, view=helpView_slash_command(self.client, self.command), ephemeral=True)
#------------------------------------------------------------------
class BtnView(discord.ui.View):
    def __init__(self, client, _command, author_name, embedName):
        super().__init__()
        self.client = client
        self.command = _command
        self.name = author_name
        self.embedName = embedName

    @discord.ui.button(label="上一頁", style=discord.ButtonStyle.secondary, emoji="◀", custom_id="previous", disabled=True)
    async def button_callback(self, button, ctx:discord.Interaction):
        if self.name != ctx.user.name:
            return
        num = self.command.btn_msg[1]
        embed = discord.Embed(
            title=self.embedName,
			description=self.command.btn_msg[0][num-1],
			colour=discord.Color.from_rgb(110, 245, 189)
        )
        embed.timestamp = datetime.datetime.now()
        # embed.description = "123456789"
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)

        # await ctx.message.edit(embed=embed)
        self.command.btn_msg[1] = num - 1
        if num - 1 == 0:
            self.get_item("previous").disabled = True
            # button.disable = True
            # await ctx.response.edit_message(embed=embed, view=self)
        if self.get_item("latter").disabled:
            self.get_item("latter").disabled = False
        self.get_item("page").label = f"Page {self.command.btn_msg[1]+1} / {len(self.command.btn_msg[0])}"
        await ctx.response.edit_message(embed=embed, view=self)
        # await ctx.response.autocomplete()
        
    @discord.ui.button(label="Page 1", style=discord.ButtonStyle.secondary, custom_id="page", disabled=True)
    async def button_callback2(self, button, ctx:discord.Interaction):
        pass


    @discord.ui.button(label="下一頁", style=discord.ButtonStyle.secondary, emoji="▶", custom_id="latter")
    async def button_callback3(self, button, ctx:discord.Interaction):
        if self.name != ctx.user.name:
            return
        num = self.command.btn_msg[1]
        embed = discord.Embed(
            title=self.embedName,
			description="",
			colour=discord.Color.from_rgb(110, 245, 189)
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        self.command.btn_msg[1] = num + 1
        self.get_item("page").label = f"Page {self.command.btn_msg[1]+1} / {len(self.command.btn_msg[0])}"

        if len(self.command.btn_msg[0]) > 1:
            embed.description = self.command.btn_msg[0][num+1]
        else:
            if len(self.command.btn_msg[0]) == 0:
                pass
            else:
                embed.description = self.command.btn_msg[0][0]
            self.get_item("page").label = f"Page {self.command.btn_msg[1]} / {len(self.command.btn_msg[0])}"

        if self.command.btn_msg[1] >= len(self.command.btn_msg[0]) - 1:
            embed.description += f"\n\n小小夕葉已經沒有東西要給你看了，變態！"
            self.get_item("latter").disabled = True
        if self.get_item("previous").disabled and len(self.command.btn_msg[0]) > 1:
            self.get_item("previous").disabled = False
        await ctx.response.edit_message(embed=embed, view=self)

class Slash_command(commands.Cog):
    def __init__(self, client, _1A2B_lst, command_lst, client_cmd_lst, mutex:threading.Lock):
        self.client = client
        self._1A2B_lst = _1A2B_lst
        self.command_lst = command_lst
        self.client_cmd_lst = client_cmd_lst
        self.mutex = mutex
        # self.diffusion = diffusion.Diffusion()
        # self.anything = anything.Anything()
        #self.stock = stock.TaiwanStock()
        self.reset.start()

    def create_embed(self, title=None, description=None, color=discord.Colour.blue()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed
    
    def nameClip(self, name:str):
        s = name
        for i, j in enumerate(s):
            if j == "(" or j == "（":
                s = s[:i]
                break
        return s
    
    def matchGuild(self, guild_id:int):
        _command = None
        for i in self.command_lst:
            if i.id == guild_id:
                _command = i
                break
        return _command

    #@tasks.loop(seconds=86400)
    @tasks.loop(hours=None, minutes=None, time=datetime.time(hour=23, minute=59, second=59, microsecond=999999, tzinfo=datetime.timezone(datetime.timedelta(hours=8))))
    async def reset(self):
        await self.client.wait_until_ready()
        guild = self.client.guilds
        conn = sqlite3.connect(f"./guild_info.db")
        for i in guild:
            cursor = conn.cursor()
            cursor.execute("select * from guild_setting where id=?", (i.id, ))
            val = cursor.fetchall()
            if val != []:
                if val[0][1]:
                    role = i.get_role(val[0][1])
                    members = role.members
                    for i in members[::-1]:
                        await i.remove_roles(role)

            cursor.close()
        conn.close()

    async def idolLoop(self, ctx):
        url = "https://www.youtube.com/watch?v=ZRtdQ81jPUQ"
        num, previous_num = 0, 0
        cnt = 0
        distance = 0
        rlt = None
        t1, t2 = 0, 0
        embed = self.create_embed(title="YOASOBI「アイドル」 Official Music Video", color=discord.Color.gold())
        while True:
            t1 = time.time()
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            html = str(soup)
            try:
                rlt = re.search(r"觀看次數：.{1,30}次", html)[0]
                num = rlt[rlt.index("：")+1:-1].replace(",", "").strip()
            except TypeError:
                t2 = time.time()
                await asyncio.sleep(300 - (t2-t1))
                continue
            cnt += 1
            try:
                num = int(num)
                distance = num - previous_num
                previous_num = num
            except:
                pass

            embed.description = rlt
            if cnt == 1:
                embed.timestamp = datetime.datetime.now()
                await ctx.send(embed=embed)
                t2 = time.time()
                await asyncio.sleep(300 - (t2-t1))
                continue
            rlt = rlt + f"\n增加次數：{distance}次"
            embed.description = rlt
            embed.timestamp = datetime.datetime.now()
            await ctx.send(embed=embed)
            t2 = time.time()
            await asyncio.sleep(300 - (t2-t1))

    @commands.slash_command(name="set_channel", description = "設定 YOASOBI「アイドル」觀看次數 頻道")
    async def set_channel(self, ctx:discord.Interaction, 頻道:discord.TextChannel):
        channel = 頻道
        _command = self.matchGuild(ctx.channel.guild.id)
        embed = self.create_embed(title="設定 YOASOBI「アイドル」觀看次數 頻道")
        if _command.channel == None:
            _command.channel = channel.id
            embed.description = f"設置 **__{channel.name}__** 頻道成功"
            
        else:
            ch = self.client.get_channel(_command.channel)
            embed.description = f"已經在 **__{ch.name}__**\n設置頻道"
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="clean_channel", description = "清除 YOASOBI「アイドル」觀看次數 頻道")
    async def clean_channel(self, ctx:discord.Interaction):
        _command = self.matchGuild(ctx.channel.guild.id)
        embed = self.create_embed(title="清除 YOASOBI「アイドル」觀看次數 頻道")
        if _command.channel == None:
            embed.description = "目前沒有需要清除的頻道"

        else:
            ch = self.client.get_channel(_command.channel)
            _command.channel = None
            embed.description = f"已經清除 **__{ch}__** 頻道"
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="clock_start", description = "開始定時傳送「アイドル」觀看次數訊息")
    async def clock_start(self, ctx:discord.Interaction):
        _command = self.matchGuild(ctx.channel.guild.id)
        embed = self.create_embed(title="開始定時傳送「アイドル」觀看次數訊息")
        if _command.channel == None:
            embed.description = "尚未設置頻道"
        else:
            ch = self.client.get_channel(_command.channel)
            if _command.task == None:
                embed.description = f"已開始在 **__{ch.name}__** 定時傳送\nYOASOBI「アイドル」觀看次數 訊息"
                _command.task = self.client.loop.create_task(self.idolLoop(ch))
            else:
                embed.description = f"目前已在 **__{ch.name}__** \n設置定時傳送"

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="clock_end", description = "停止定時傳送「アイドル」觀看次數訊息")
    async def clock_end(self, ctx:discord.Interaction):
        lst = ["eurico0929", "sakanyan6776", "mikannyuuba"]
        limit = ["1105729753505341501", "1109939011298005164"]
        roles = ctx.channel.guild.roles[1:]
        for i in roles:
            if str(i.id) in limit:
                lst += [member.name for member in i.members]

        embed = self.create_embed(title="停止定時傳送「アイドル」觀看次數訊息")
        if ctx.user.name not in lst:
            embed.description = f"{ctx.user.name} 沒有更改權限"

        else:
            _command = self.matchGuild(ctx.channel.guild.id)
            if _command.channel == None:
                embed.description = "尚未設置頻道"
            else:
                if _command.task != None:
                    ch = self.client.get_channel(_command.channel)
                    _command.task = _command.task.cancel()
                    _command.task = None
                    embed.description = f"已停止在 **__{ch.name}__** 定時傳送\nYOASOBI「アイドル」觀看次數 訊息"
                else:
                    embed.description = "目前沒有需要終止的定時器"

        await ctx.response.send_message(embed=embed)

#待修改成btn形式----------------------------------------------------------------------------------------

    @commands.slash_command(name="設定獲得身分組訊息", description = "設定獲得身分組的訊息")
    async def 設定獲得身分組訊息(self, ctx:discord.Interaction, 設置訊息:str, 身分組:discord.Role):
        _command = self.matchGuild(ctx.channel.guild.id)
        content = 設置訊息
        role = 身分組
        embed = self.create_embed(title="設定獲得身分組訊息", description="已設置完成", color=discord.Color.nitro_pink())
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        embed2 = self.create_embed(title=f"**__{role}__**", description=content)
        embed2.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        msg = await ctx.send(embed=embed2)
        _command.message.append((role, msg.id))

        self.mutex.acquire()

        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from guild_setting where id=?", (msg.guild.id, ))
        val = cursor.fetchall()
        if val != []:
            _, _, _, _, _, addrole, _, _ = val[0]
            sql = "update guild_setting SET addrole=? WHERE id=?"
            cursor.execute(sql, (f"{addrole},{role.id}-{msg.id}".strip(","), ctx.guild.id))

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        await ctx.response.send_message(embed=embed, delete_after=10)
#----------------------------------------------------------------------------------------
    @commands.slash_command(name="隨機身分組抽籤", description = "隨機抽籤")
    async def 隨機身分組抽籤(self, ctx:discord.Interaction, 抽選身分組:discord.Role, 抽選成員數量:int):
        role = 抽選身分組
        num = 抽選成員數量
        lst = discord.utils.get(ctx.guild.roles, id=role.id).members
        embed = self.create_embed(title="🎟️ | 隨機身分組抽籤之抽選結果")
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        if len(lst) < num or num <= 0:
            embed.description = f"身分組: **__{role.name}__**，人數: {len(lst)}\n無法抽取數量為 {num} 的人"
            # await ctx.respond(f"身分組: **__{role.name}__**，人數: {len(lst)}\n無法抽取數量為 {num} 的人")
        else:
            lst = [i.display_name for i in lst]
            for idx, member_name in enumerate(lst):
                for i, j in enumerate(member_name):
                    if j == "(" or j == "（":
                        lst[idx] = member_name[:i]
                        break
            rlt = random.sample(lst, num)
            string = ""
            for i, j in enumerate(rlt):
                string += f"{i}. *{j}*\n"

            string += f"身分組：**__{role.name}__**\n指定抽選數量：{num}"
            embed.description = string.strip("\n")
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="設定新成員歡迎訊息", description = "設定新成員歡迎訊息")
    async def 設定新成員歡迎訊息(self, ctx:discord.Interaction, 設置成員稱謂:str, 設置內容:str):
        call = 設置成員稱謂
        content = 設置內容
        _command = self.matchGuild(ctx.channel.guild.id)
        if content == "clean":
            content = None
        _command.welcome = content
#--------------------------------------------------------------------------------------------
        self.mutex.acquire()

        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from guild_setting where id=?", (ctx.guild.id, ))
        val = cursor.fetchall()
        
        embed = self.create_embed(title="👏 | 設置之新成員歡迎訊息", color=discord.Color.nitro_pink())
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        if val != []:
            sql = "update guild_setting SET call=?, message=? WHERE id=?"
            cursor.execute(sql, (call, content, ctx.guild.id))
            string = f"歡迎 @someone\n成為第 **__{len(ctx.guild.members)}__** 位{call}"
            embed.description = f"{string}\n{content}"
        else:
            embed.description = "未設置成功，請聯絡開發者"

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()
#--------------------------------------------------------------------------------------------
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="查看新成員歡迎訊息", description = "查看目前設定之新成員歡迎訊息")
    async def 查看新成員歡迎訊息(self, ctx:discord.Interaction):
        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from guild_setting where id=?", (ctx.guild.id, ))
        val = cursor.fetchall()
        
        call, message = "成員", None
        if val != []:
            _, _, call_db, message, _, _, _, _ = val[0]
            if call_db != "":
                call = call_db

        cursor.close()
        conn.commit()
        conn.close()

        string = f"歡迎 @someone\n成為第 **__{len(ctx.guild.members)}__** 位{call}"
        if message != "" and message != None:
            string += "\n" + message

        embed = self.create_embed(title="👏 | 設置之新成員歡迎訊息", description=string, color=discord.Color.nitro_pink())
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="隨機", description = "用空白隔開選項，隨機獲得一個結果")
    async def 隨機(self, ctx:discord.Interaction, 設置訊息:str):
        content = 設置訊息.strip()
        content = re.sub(" +", " ", content)
        lst = content.split(" ")
        rlt = random.sample(lst, 1)
        embed = self.create_embed(title="🎰 | 隨機抽籤", description=f"抽選內容：[{content}]\n結果：**__{rlt[0]}__**")
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="設定身分組語音頻道", description = "標註若干身分組以設定語音頻道")
    async def 設定身分組(self, ctx:discord.Interaction, 標註若干身分組:str):
        lst = re.findall("<@&[0-9]{10,25}>", 標註若干身分組)
        lst = [int(re.search("\d+", i)[0]) for i in lst]
        lst = [ctx.guild.get_role(i) for i in lst]

        category = {i.name:i for i in ctx.guild.categories}
        cate = None
        if category.get("身分組數量") == None:
            cate = await ctx.guild.create_category(name="身分組數量", position=len(category)-1)
        else:
            cate = category["身分組數量"]

        embed = self.create_embed(description="")
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        non_overlap_lst = []
        l = [i.name[:i.name.find(":")] for i in ctx.guild.voice_channels]
        for i in lst:
            if i.name not in l:
                non_overlap_lst.append(i)
            else:
                embed.description += f"語音頻道 **__{i.name}__** 已經存在\n"
                # await ctx.send(f">>> 語音頻道 {i.name} 已經存在")

        name = None
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
        }
        for i in non_overlap_lst:
            name = f"{i.name}: {len(i.members)}"
            await ctx.guild.create_voice_channel(name=name, 
                                                category=cate, 
                                                user_limit=0, 
                                                overwrites=overwrites)
        
        embed.description += "\n身分組語音頻道設定完成"
        embed.description = embed.description.strip()
        await ctx.respond(embed=embed)

    @commands.slash_command(name="check", description = "確認 YOASOBI「アイドル」觀看次數")
    async def check(self, ctx:discord.Interaction):
        url = "https://www.youtube.com/watch?v=ZRtdQ81jPUQ"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        html = str(soup)
        rlt = re.search(r"觀看次數：.{1,30}次", html)[0]
        embed = self.create_embed(title="YOASOBI「アイドル」 Official Music Video", description=rlt, color=discord.Color.gold())
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="取得頭貼", description = "@使用者以獲得頭貼")
    async def p(self, ctx:discord.Interaction, 標註成員:discord.Member):
        await ctx.response.defer()
        member = 標註成員
        url = member.display_avatar.url
        embed = self.create_embed(title=f"📸 | 取得 **{member.display_name}** 的頭貼")
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        f = url.find("?")
        if f != -1:
            url_withoutParameter = url[:f]
        # if f != -1:
        #     requestURL = url[:f] + "?quality=lossless" #"?size=2048&quality=lossless"
        dtype = url_withoutParameter[url_withoutParameter.rfind(".")+1:]
        discord_file = await member.display_avatar.read()
        picture = discord.File(BytesIO(discord_file), filename=f"file.{dtype}")
        embed.set_image(url=f"attachment://file.{dtype}")
        await ctx.followup.send(embed=embed, file=picture)

    @commands.slash_command(name="刪除機器人指令", description = "瀏覽頻道歷史訊息數量並刪除其中含有的機器人指令 uniform[1,30]")
    async def d(self, ctx:discord.Interaction, 瀏覽頻道歷史訊息數量:discord.Option(int, description = "瀏覽頻道歷史訊息數量", min_value=1, max_value=20, default=10)):
        await ctx.response.defer()
        num = 瀏覽頻道歷史訊息數量
        lst = [m async for m in ctx.channel.history(limit=num+1)]
        lst = list(lst)[1:]
        cnt = 0
        for i in lst:
            if i.author.id == self.client.user.id or i.content.isdigit() or "$" in i.content:
                await i.delete()
                cnt += 1

        display_name = self.nameClip(ctx.user.display_name)
        embed = self.create_embed(description=f"瀏覽頻道歷史訊息數量： **{num}**\n已刪除數量： **{cnt}**")
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        await asyncio.sleep(10)
        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="設置成員訊息", description = "設置成員訊息")
    async def set(self, ctx:discord.Interaction, 標註成員:discord.Member, 設置內容=None):
        member = 標註成員
        content = 設置內容

        if content == None:
            content = ""

        display_name_author = self.nameClip(ctx.user.display_name)
        display_name = self.nameClip(member.display_name)
        df = pd.read_csv(f"./response/{ctx.channel.guild.id}.csv", index_col=None, encoding="cp950")
        embed = self.create_embed(title="📩 | 設置訊息")
        if member.name not in df.member.values:
            data = pd.DataFrame(data={"member":[member.name], "word":[content]}, columns=["member", "word"])
            df = pd.concat([df, data], ignore_index=True)
            df.to_csv(f"./response/{ctx.channel.guild.id}.csv", index=False, encoding="cp950")
        else:
            data = {"member":member.name, "word":content}
            val = df.index[df['member'] == member.name].tolist()[0]
            df.loc[val] = data
            df.to_csv(f"./response/{ctx.channel.guild.id}.csv", index=False, encoding="cp950")
        
        embed.description = f"**__{display_name_author}__** 對 **__{display_name}__** \n設置 {content} 成功"
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="更改字型", description = "更改$m使用的字型")
    async def font(self, ctx:discord.Interaction, 
                   menu:discord.Option(str, "請選擇要更改的字型(HanyiSentyTang為預設字型)", 
                    choices=[discord.OptionChoice(name="HanyiSentyTang", value="HanyiSentyTang"),
                            discord.OptionChoice(name="辰宇落雁體", value="辰宇落雁體"),
                            discord.OptionChoice(name="NaikaiFont-ExtraLight", value="NaikaiFont-ExtraLight"),
                            discord.OptionChoice(name="Silver", value="Silver"),
                            discord.OptionChoice(name="王漢宗中行書繁", value="王漢宗中行書繁"),
                            discord.OptionChoice(name="SentyGoldenBell_2", value="SentyGoldenBell_2"),
                            discord.OptionChoice(name="華康少女文字W5", value="華康少女文字W5"),
                            discord.OptionChoice(name="setofont", value="setofont"),
                            discord.OptionChoice(name="芫荽Iansui", value="芫荽Iansui"),
                            discord.OptionChoice(name="清松手寫體2", value="清松手寫體2"),
                            discord.OptionChoice(name="清松手寫體5-草寫", value="清松手寫體5-草寫"),
                            discord.OptionChoice(name="マメロン Hi-Regular", value="マメロン Hi-Regular"),
                            discord.OptionChoice(name="CheekFont-Regular", value="CheekFont-Regular"),
                            discord.OptionChoice(name="Consolas", value="Consolas"),
                            discord.OptionChoice(name="電影字幕體", value="電影字幕體"),
                            discord.OptionChoice(name="莫大毛筆字體-Regular", value="莫大毛筆字體-Regular")]
                            )):
        
        _command = self.matchGuild(ctx.channel.guild.id)
        _command.font = menu

        self.mutex.acquire()

        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from guild_setting where id=?", (ctx.guild.id, ))
        val = cursor.fetchall()
        if val != []:
            _, _, _, _, _, _, fontData, _ = val[0]
            sql = "update guild_setting SET font=? WHERE id=?"
            cursor.execute(sql, (menu, ctx.guild.id))

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        embed = self.create_embed(title="⌨️ | 設定字型", description=f"已設定字型：\n **__{menu}__**")
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=embed)
        # await ctx.respond(f">>> 已設定字型：\n **__{menu}__**")

    @commands.slash_command(name="設定圖片", description = "設定圖片名字並上傳圖片")
    async def 設定圖片(self, ctx:discord.Interaction, 圖片名字:str, 圖片:discord.Attachment):
        await ctx.response.defer()
        _command = self.matchGuild(ctx.guild.id)
        name = 圖片名字
        att = 圖片
        content_type = att.content_type[att.content_type.find("/")+1:]

        embed = self.create_embed(title="🔑 | 設定圖片", color=discord.Color.from_rgb(110, 245, 189))
        if content_type not in ["jpeg", "jpg", "png", "gif", "webp"] or att.size > 10000000:
            embed.description = "小夕葉不喜歡這個，哼！"
            # await ctx.respond(">>> 小夕葉不喜歡這個，哼！") 
        else:
            path = f"./photo/{_command.id}"
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            full_path = f"{path}/{name}.{content_type}"
            await att.save(full_path)
            _command.photo[name] = content_type
            
            embed.description = f"關鍵字: __**{name}**__\n圖片已設置成功"
        # await ctx.response.send_message(embed=embed)
        await asyncio.sleep(3)
        await ctx.followup.send(embed=embed)
        # await ctx.respond(f">>> 關鍵字: __**{name}**__\n圖片已設置成功")

    @commands.slash_command(name="查詢圖片列表", description="查詢圖片列表")
    async def 查詢圖片列表(self, ctx:discord.Interaction):
        _command = self.matchGuild(ctx.guild.id)

        string = "目前有的圖片:\n------------------------------------\n"
        lst = [i for i in _command.photo.keys()]
        for i in lst:
            string += f"{i}.{_command.photo[i]}\n"

        with open(f"./photo/{_command.id}/check.txt", "w") as check:
            print(string.strip(), file=check)
#--------------------------------------------------------------------------
        string_lst = [f"{i+1}. **{j}**.{_command.photo[j]}" for i, j in enumerate(lst)]
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
        embed = self.create_embed(title="🌠 | 圖片列表", color=discord.Color.from_rgb(110, 245, 189))
        if len(page_lst) != 0:
            embed.description = page_lst[0]
        else:
            embed.description = "小夕葉沒有東西要給你看，變態！"
#--------------------------------------------------------------------------
        with open(f"./photo/{_command.id}/check.txt", "rb") as check:
            f = discord.File(check, filename="all_photo_name.txt")
            # await ctx.respond(file=f)
            await ctx.response.send_message(embed=embed, view=BtnView(self.client, _command, ctx.user.name, "🌠 | 圖片列表"), file=f)

    @commands.slash_command(name="刪除圖片", description = "刪除圖片")
    async def 刪除圖片(self, ctx:discord.Interaction, 刪除圖片名稱:str):
        _command = self.matchGuild(ctx.guild.id)
        name = 刪除圖片名稱
        embed = self.create_embed(color=discord.Color.from_rgb(110, 245, 189))
        if name in _command.photo.keys():
            path = f"./photo/{ctx.guild.id}/{name}.{_command.photo[name]}"
            os.remove(path)
            _command.photo.pop(name)
            embed.description = f"已刪除圖片: __**{name}**__"
        else:
            embed.description = "小夕葉才沒有這種東西呢，哼！"

        await ctx.response.send_message(embed=embed)

    # @commands.slash_command(name="個人帳單", description = "茜的個人帳單")
    # async def 個人帳單(self, ctx:discord.Interaction, 標註成員:discord.Member):
    #     member = 標註成員
    #     bill_df = None
    #     month = datetime.datetime.now().month
    #     year = datetime.datetime.now().year
    #     try:
    #         bill_df = pd.read_csv(f"./bill/{ctx.channel.guild.id}_bill_{month}_{year}.csv", index_col=None, encoding="cp950")
    #     except FileNotFoundError:
    #         bill_df = pd.DataFrame(columns=["date", "name", "money"])
    #         bill_df.to_csv(f"./bill/{ctx.channel.guild.id}_bill_{month}_year.csv", index=False, encoding="cp950")
    #         bill_df = pd.read_csv(f"./bill/{ctx.channel.guild.id}_bill_{month}_{year}.csv", index_col=None, encoding="cp950")

    #     mention = member.name
    #     display_name = self.nameClip(member.display_name)
    #     df_cp = bill_df[bill_df["name"] == mention].copy()
    #     string = f"{month}月份帳單明細\nby __{display_name}__\n\n"
    #     string2 = f"{month}月份帳單明細\nby __{display_name}__\n\n"
    #     total = 0
    #     data_size = len(df_cp.index)
    #     df_cp.index = [i for i in range(data_size)]
    #     string2 += "...\n"
    #     for i in range(len(df_cp.index)):
    #         tmp = df_cp.loc[i].values
    #         if data_size > 10:
    #             if i >= df_cp.index[-10]:
    #                 string2 += f"{tmp[0]:<30}{tmp[2]:>10}元\n"
    #         else:
    #             string += f"{tmp[0]:<30}{tmp[2]:>10}元\n"

    #         total += tmp[2]

    #     avg = None
    #     if data_size == 0:
    #         avg = "0"
    #     else:
    #         avg = f"{total / data_size:.3f}"
    #     string += f"\n總共茜了 {data_size} 次車資\n共 {total} 元\n平均一次茜 {avg} 元"
    #     string2 += f"\n總共茜了 {data_size} 次車資\n共 {total} 元\n平均一次茜 {avg} 元"
    #     # string += f"\n次數： {}total: {total:>10}元"
    #     embed = self.create_embed(title="🧾 | 茜的個人帳單")
    #     if data_size <= 10:
    #         embed.description = string
    #     else:
    #         embed.description = string2
    #     await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="查詢伺服器個人卡片", description = "標註成員即可查詢伺服器個人卡片")
    async def 查詢伺服器個人卡片(self, ctx:discord.Interaction, 標註成員:discord.Member):
        mention = 標註成員

        conn = sqlite3.connect(f"./id_card/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from data where id=?", (mention.id, ))
        val = cursor.fetchall()
        cursor.close()
        conn.close()

        embed = self.create_embed(title=f"{self.nameClip(mention.display_name)} / 伺服器個人卡片", description="")
        if val != []:
            _, _, nickname, msg_count, emoji_count, last_msg, last_msg_time = val[0]
            identity = "幼兒"
            rank_dict = {"幼兒":discord.Color.from_rgb(204, 0, 128), 
                         "幼稚園生":discord.Color.from_rgb(127, 255, 212), 
                         "小學生":discord.Color.from_rgb(209, 222, 189), 
                         "國中生":discord.Color.yellow(), 
                         "高中生":discord.Color.brand_red(), 
                         "大學生":discord.Color.brand_green(), 
                         "碩士生":discord.Color.orange(), 
                         "博士生":discord.Color.gold(), 
                         "社會人":discord.Color.nitro_pink()}
            rank = list(rank_dict.keys())
            range_lst = [4**i for i in range(9)]

            lvlup = "Max"
            for i, j in enumerate(range_lst):
                if msg_count >= j:
                    identity = rank[i]
                else:
                    lvlup = j - msg_count
                    break

            embed.colour = rank_dict[identity]
            join_time = mention.joined_at + datetime.timedelta(hours=8)
            join_time = join_time.replace(tzinfo=None)
            now = datetime.datetime.now()
            difference = now - join_time

            #embed.set_author(name=mention.display_name, icon_url=mention.display_avatar.url)
            embed.description += f"💳 ID: **__{mention.id}__**\n暱稱: **__{nickname}__**\n伺服器名稱: **__{ctx.guild.name}__**\n{'-'*30}"
            
            embed.add_field(name="下次升級經驗", value=f"{lvlup}")
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
            embed.add_field(name="最後活躍時間", value=last_msg_time, inline=False)
        else:
            embed.description = "目前無本人相關資訊"

        # print(mention.display_avatar.url)
        embed.set_thumbnail(url=mention.display_avatar.url)
            
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="設定伺服器個人卡片暱稱", description = "標註成員即可設定伺服器個人卡片暱稱")
    async def 設定伺服器個人卡片暱稱(self, ctx:discord.Interaction, 標註成員:discord.Member, 設定暱稱:str):
        mention = 標註成員
        content = 設定暱稱
        content = content.replace("\\", "")
        self.mutex.acquire()

        conn = sqlite3.connect(f"./id_card/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from data where id=?", (mention.id, ))
        val = cursor.fetchall()

        embed = self.create_embed(title="設定伺服器個人卡片暱稱", color=discord.Color.brand_red())
        if val != []:
            if len(content) < 30:
                sql = "update data SET nick=? WHERE id=?"
                cursor.execute(sql, (content, mention.id))
                embed.description = f"已對 __{self.nameClip(mention.display_name)}__ 設定暱稱:\n**__{content}__**"
            else:
                embed.description = f"未對 __{self.nameClip(mention.display_name)}__ 設定暱稱:\n**__{content}__**\n(超過上限30字)"
        else:
            embed.description = f"目前無 {self.nameClip(mention.display_name)} 的資料喔~"

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="查看個人運勢", description = "喵！測個運氣吧！")
    async def 查看個人運勢(self, ctx:discord.Interaction):
        '''
        conn = sqlite3.connect(f"./id_card/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from data")
        val = cursor.fetchall()
        val.sort(key=lambda x:x[3], reverse=True)
        cursor.close()
        conn.close()
        print(val[11])
        '''
        _command = self.matchGuild(ctx.guild.id)
        today = datetime.datetime.now().day
        if today != _command.luck_cnt.get("date"):
            _command.luck_cnt = {}
            _command.luck_cnt["date"] = today
        cnt = _command.luck_cnt.get(ctx.user.id)
        if cnt == None:
            _command.luck_cnt[ctx.user.id] = 0

        if _command.luck_cnt[ctx.user.id] <= 3:
            _command.luck_cnt[ctx.user.id] += 1
        lst = ["大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"]
        response_dict = {1:"", 2:"嗯？怎麼好像今天見過你...算了", 3:"絕對是你吧變態٩(๑`^´๑)۶\n再來的話小夕葉要生氣了喔！", 4:"我生氣不理你了，哼！"}
        rlt = np.random.choice(lst, p=[0.08, 0.134, 0.178, 0.231, 0.211, 0.146, 0.02])

        # elif ctx.user.id == 498817981497999360:
        #     rlt = "大吉"
        # rlt = random.sample(lst, 1)[0]
        path = f"./lucky/{rlt}.png"
        file = None
        filename = "image.png"

        embed = self.create_embed(title="🍀 | 喵！測個運氣吧！", color=discord.Color.random(), description=response_dict[_command.luck_cnt[ctx.user.id]])
        if _command.luck_cnt[ctx.user.id] <= 3:
            embed.description += f"\n\n**__{self.nameClip(ctx.user.display_name)}__**！\n今天的運勢是: **__{rlt}__**"
            file = discord.File(path, filename=filename)

            if rlt == "大吉":
                conn = sqlite3.connect(f"./guild_info.db")
                cursor = conn.cursor()
                cursor.execute("select * from guild_setting where id=?", (ctx.guild.id, ))
                val = cursor.fetchall()
                if val != []:
                    role = ctx.guild.get_role(val[0][1])
                    if role != None:
                        roles = [i.id for i in ctx.user.roles]
                        if role.id not in roles:
                            await ctx.user.add_roles(role)
                        #if _command.reset == None:
                        #    asyncio.create_task(self.reset(ctx.guild.id, val[0][1]))
                        #    _command.reset = True
                    else:
                        pass

                cursor.close()
                conn.close()

        else:
            path = f"./lucky/ruby_cry.gif"
            file=discord.File(path, filename="DONTLIKEYOU.gif")
            filename = "DONTLIKEYOU.gif"
        
        embed.set_image(url=f"attachment://{filename}")

        await ctx.response.send_message(file=file, embed=embed)
    """ db有重寫過，要重改
    @commands.slash_command(name="個人運勢系統重設", description = "個人運勢系統重設")
    async def 個人運勢系統重設(self, ctx:discord.Interaction):
        _command = self.matchGuild(ctx.guild.id)
        embed = self.create_embed(title="個人運勢系統重設")

        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from welcome_msg where id=?", (ctx.guild.id, ))
        val = cursor.fetchall()
        if val != []:
            role = ctx.guild.get_role(val[0][1])
            if role != None:
                if _command.reset == None:
                    asyncio.create_task(self.reset(ctx.guild.id, val[0][1]))
                    embed.description = "已重新設置自動刷新時間"
                    _command.reset = True
                else:
                    embed.description = "目前無須重設"
            else:
                embed.description = "身分組已刪除\n請使用 /設定系統身分組 設定"
        else:
            embed.description = "未設置系統身分組"

        await ctx.response.send_message(embed=embed)
    """

    @commands.slash_command(name="查詢伺服器個人卡片排行榜", description = "使用指令即可查詢伺服器個人卡片排行榜")
    async def 查詢伺服器個人卡片排行榜(self, ctx:discord.Interaction):
        _command = self.matchGuild(ctx.guild.id)
        conn = sqlite3.connect(f"./id_card/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from data")
        val = cursor.fetchall()
        val.sort(key=lambda x:x[3], reverse=True)
        cursor.close()
        conn.close()
        string_lst = []
        # string_lst = [f"{i+1}. __{self.nameClip(ctx.guild.get_member(j[0]).display_name)}__, {j[3]} 則" for i, j in enumerate(val)]
        for i, j in enumerate(val):
            member = ctx.guild.get_member(j[0])
            if member == None:
                continue
            display_name = self.nameClip(member.display_name)
            string_lst.append(f"{i+1}. __{display_name}__, {j[3]} 則")

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
        embed = self.create_embed(title="🏅 | 伺服器個人卡片排行榜", color=discord.Color.from_rgb(110, 245, 189))
        if len(page_lst) != 0:
            embed.description = page_lst[0]
        else:
            embed.description = "小夕葉沒有東西要給你看，變態！"
        
        await ctx.response.send_message(embed=embed, view=BtnView(self.client, _command, ctx.user.name, "⭐ | 伺服器個人卡片排行榜"))


    @commands.slash_command(name="我喜歡妳", description = "試試看跟小夕葉告白吧！")
    async def 我喜歡妳(self, ctx:discord.Interaction):
        lst = []
        with open("./love.txt", "r", encoding="utf8") as f:
            lst = f.readlines()


        lst = [i.replace("$", "\n").strip() for i in lst]
        rlt = random.sample(lst, 1)[0]
        embed = self.create_embed(description=rlt, color=discord.Color.random())
        if ctx.user.name == "mikannyuuba":
            embed.description = "我也喜歡夕葉麻麻~"
            embed.colour = discord.Color.nitro_pink()
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="查詢我喜歡妳回答列表", description = "使用指令即可查詢我喜歡妳回答列表")
    async def 查詢我喜歡妳回答列表(self, ctx:discord.Interaction):
        lst = []
        with open("./love.txt", "r", encoding="utf8") as f:
            lst = f.readlines()

        val = [i.replace("$", "，").strip() for i in lst]

        string_lst = [f"{i+1}. {j}" for i, j in enumerate(val)]

        page_lst = []
        _command = self.matchGuild(ctx.guild.id)
        _command.btn_msg = [page_lst, 0]
        s = ""
        for i, j in enumerate(string_lst):
            s += j + "\n"
            if i == len(string_lst) - 1 and s != "":
                page_lst.append(s.strip())
            elif (i + 1) % 10 == 0:
                page_lst.append(s.strip())
                s = ""
        embed = self.create_embed(title="💫 | 「我喜歡妳」回答列表", color=discord.Color.from_rgb(110, 245, 189))
        if len(page_lst) != 0:
            embed.description = page_lst[0]
        else:
            embed.description = "小夕葉沒有東西要給你看，變態！"
        
        await ctx.response.send_message(embed=embed, view=BtnView(self.client, _command, ctx.user.name, "⭐ | 我喜歡妳回答列表"))

    # db有重寫過，要重改
    # @commands.slash_command(name="設定系統身分組", description = "使用指令即可設定系統身分組")
    # async def 設定系統身分組(self, ctx:discord.Interaction, 設定之身分組:discord.Role):
    #     role = 設定之身分組
    #     self.mutex.acquire()

    #     conn = sqlite3.connect(f"./guild_info.db")
    #     cursor = conn.cursor()
    #     cursor.execute("select * from welcome_msg where id=?", (ctx.guild.id, ))
    #     val = cursor.fetchall()
        
    #     embed = self.create_embed(title="👏 | 設置之系統身分組", color=discord.Color.nitro_pink())
    #     if val != []:
    #         sql = "update welcome_msg SET system_role=? WHERE id=?"
    #         cursor.execute(sql, (role.id, ctx.guild.id))
    #         embed.description = f"**__{role.name}__**"
    #     else:
    #         embed.description = "未設置成功，請聯絡開發者"

    #     cursor.close()
    #     conn.commit()
    #     conn.close()
    #     self.mutex.release()
    #     await ctx.response.send_message(embed=embed)

    # db有重寫過，要重改
    # @commands.slash_command(name="查看系統身分組", description = "使用指令即可查看系統身分組")
    # async def 查看系統身分組(self, ctx:discord.Interaction):
    #     self.mutex.acquire()

    #     conn = sqlite3.connect(f"./guild_info.db")
    #     cursor = conn.cursor()
    #     cursor.execute("select * from welcome_msg where id=?", (ctx.guild.id, ))
    #     val = cursor.fetchall()
        
    #     embed = self.create_embed(title="👏 | 查看設置之系統身分組", color=discord.Color.nitro_pink())
    #     if val != []:
    #         if val[0][1] != 0:
    #             role = ctx.guild.get_role(val[0][1])
    #             if role != None:
    #                 embed.description = f"**__{role.name}__**"
    #             else:
    #                 embed.description = "該身分組已失效"
    #         else:
    #             embed.description = "目前尚未設置"
    #     else:
    #         embed.description = "未設置成功，請聯絡開發者"

    #     cursor.close()
    #     conn.commit()
    #     conn.close()
    #     self.mutex.release()
    #     await ctx.response.send_message(embed=embed)

    # db有重寫過，要重改
    # @commands.slash_command(name="清除系統身分組成員", description = "使用指令即可清除系統身分組成員")
    # async def 清除身分組成員(self, ctx:discord.Interaction):
    #     self.mutex.acquire()

    #     conn = sqlite3.connect(f"./guild_info.db")
    #     cursor = conn.cursor()
    #     cursor.execute("select * from welcome_msg where id=?", (ctx.guild.id, ))
    #     val = cursor.fetchall()
        
    #     embed = self.create_embed(title="👏 | 清除設置之系統身分組成員", color=discord.Color.nitro_pink())
    #     if val != []:
    #         if val[0][1] != 0:
    #             role = ctx.guild.get_role(val[0][1])
    #             if role != None:
    #                 members = role.members
    #                 for i in members[::-1]:
    #                     await i.remove_roles(role)

    #                 _command = self.matchGuild(ctx.guild.id)
    #                 _command.reset = None
    #                 embed.description = "已成功清除系統身分組成員"
    #             else:
    #                 embed.description = "該身分組已失效"
    #         else:
    #             embed.description = "目前尚未設置系統身分組"
    #     else:
    #         embed.description = "未設置成功，請聯絡開發者"

    #     cursor.close()
    #     conn.commit()
    #     conn.close()
    #     self.mutex.release()
    #     await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="help", description = "查詢指令列表")
    async def help(self, ctx:discord.Interaction):
        _command = self.matchGuild(ctx.guild.id)
        view = selectView(self.client, _command)
        embed = self.create_embed(title="HELP", description="請選擇要查詢的指令類型", color=discord.Colour.nitro_pink())
        await ctx.response.send_message(embed=embed, view=view)

    @commands.slash_command(name="metrics", description = "測2張圖的各項指標")
    async def metrics(self, ctx:discord.Interaction, 圖片:discord.Attachment, 圖片2:discord.Attachment):
        att = 圖片
        content_type = att.content_type[att.content_type.find("/")+1:]
        att2 = 圖片2
        content_type2 = att2.content_type[att2.content_type.find("/")+1:]
        embed = self.create_embed(title="metrics", color=discord.Color.random())

        path = f"./psnr/"
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        await att.save(f"{path}/1.{content_type}")
        await att2.save(f"{path}/2.{content_type2}")

        img1 = cv2.imread(f"{path}/1.{content_type}")
        img2 = cv2.imread(f"{path}/2.{content_type2}")

        # diff = img1 - img2 #(batch, channel, size, size)
        # diff = np.moveaxis(diff, -1, 0).astype(np.float32)
        # mse = np.mean(np.square(diff), axis=(1, 2)) #(batch, 3)
        # mse_avg = np.sum(mse) / 3.
        # psnr = 10 * np.log10(255 * 255 / mse_avg)
        psnr = compare_psnr(img1, img2)
        mse = compare_mse(img1, img2)
        # ssim = compare_ssim(img1, img2, multichannel=True)
        embed.add_field(name="PSNR", value=psnr, inline=False)
        embed.add_field(name="", value="", inline=False)
        # embed.add_field(name="SSIM", value=ssim, inline=False)
        # embed.add_field(name="", value="", inline=False)
        embed.add_field(name="MSE", value=mse, inline=False)

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="貼圖添加身分組檢查測試用", description = "檢查測試用")
    async def check(self, ctx:discord.Interaction):
        _command = self.matchGuild(ctx.guild.id)
        await ctx.response.send_message(_command.message)

    @commands.slash_command(name="embed", description = "輸入標題和內文以取得embed")
    async def embed(self, ctx:discord.Interaction, 標題:str, 內文:str, 複製:discord.Option(int, description="是否開啟內文複製", default=1, 
                          choices=[discord.OptionChoice(name="開啟", value=1), 
                                   discord.OptionChoice(name="關閉", value=0)])):
        title = 標題
        content = 內文
        default = 複製
        if default:
            content = f"```{content}```"
        embed = self.create_embed(title=title, description=content, color=discord.Color.random())
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="bluearchive", description = "塔羅牌顏色")
    async def bluearchive(self, ctx:discord.Interaction):
        lst = ["紅", "綠", "黃", "藍"]
        dicts = {"紅":discord.Color.red(), 
                 "綠":discord.Color.green(),
                 "黃":discord.Color.gold(), 
                 "藍":discord.Color.blue()}
        
        rlt = random.sample(lst, 1)[0]
        embed = self.create_embed(title="塔羅牌顏色", description=f"結果: {rlt}", color=dicts[rlt])
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="道具扭蛋", description = "來抽2穿看看手氣吧!!!")
    async def itemGacha(self, ctx:discord.Interaction, menu:discord.Option(str, "請選擇要抽的種類", 
                    choices=[discord.OptionChoice(name="傳說中的縫衣針", value="傳說中的縫衣針"),
                             discord.OptionChoice(name="傳說中的裝飾品", value="傳說中的裝飾品"),
                             discord.OptionChoice(name="傳說中的絲線", value="傳說中的絲線")])):
        lst = ["**穿孔錘[單手劍]**", "**穿孔錘[雙手劍]**", "**穿孔錘[弓]**", "**穿孔錘[連弩]**", "**穿孔錘[法杖]**", 
               "**穿孔錘[魔導具]**", "**穿孔錘[拳套]**", f"**{menu}**", "**榮耀晶石**", "**穿孔錘[旋風槍]**", "**穿孔錘[拔刀劍]**", 
               "鍛鍊的禁書", "沉思的手鏡", "亞倫之書", "索羅羅之書", "托利葉之書", "約克之書", "佩魯魯之書", 
               "皮諾之書", "里貝拉之書II", "畢戈之書II", "泰納之書II", "里貝拉之書III", "畢戈之書III", "泰納之書III", 
               "里貝拉之書IV", "畢戈之書IV", "泰納之書IV", "鍛鍊之書", "鍛鍊的密書", "天地開元之書", "抽取鍛晶", "泰納之書", 
               "蒙丹之書", "莉路露之書", "巴夫特之書", "生命藥x3", "魔力劑x3", "復活之露x3", "里貝拉之書", "畢戈之書", 
               "力量晶石DX x3", "智慧晶石DX x3", "生命晶石DX x3", "敏捷晶石DX x3", "靈巧晶石DX x3", "魔力晶石DX x3", "防禦晶石DX x3", "閃躲晶石DX x3"]
        p = [0.00151, 0.00151, 0.00151, 0.00151, 0.00151, 0.00151, 0.00151, 0.003, 0.00151, 0.00151, 0.00151, 
             0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 0.0189, 
             0.0387, 0.0387, 0.0387, 0.0387, 0.0387, 0.0387, 0.0387, 0.0387,
             0.027, 0.027, 0.027, 0.027, 0.027, 0.027, 0.027, 0.027, 0.027, 0.027, 0.027, 0.027, 0.027]
        rlt = np.random.choice(lst, p=p, size=11)
        cnt = 0
        for i in rlt:
            if "**" in i:
                cnt += 1
        string = ""
        for i, j in enumerate(rlt):
            string += f"{i+1}. {j}\n"
        string += f"\n11抽共含有 **{cnt}** 個四星道具"
        embed = self.create_embed(title=f"👑 | 道具扭蛋({menu})", description=string, color=discord.Color.random())
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="水底的寶物", description = "來抽水底的寶物看看手氣吧!!!")
    async def treasureUnderWater(self, ctx:discord.Interaction):
        lst = ["[拔刀劍] **村雨**", "[旋風槍] **滅火纏**", "[弩] **擬態斧**", 
               "[弓] **竹弓**", "[魔導具] **佩司博拉多**", "[杖] **商神杖**",
               "[拳套] **木巨人拳套**", "[雙手劍] **木巨人的大槌**", "[單手劍] **折斷的大劍**"]
        p = [1/len(lst) for i in range(len(lst))]
        rlt = np.random.choice(lst, p=p)

        embed = self.create_embed(title=f"👑 | 水底的寶物", description=rlt, color=discord.Color.random())
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="切換刪除訊息狀態", description = "刪除的訊息是否要重傳")
    async def switch(self, ctx:discord.Interaction, state:discord.Option(str, "開啟或關閉刪除訊息重傳", 
                                                                         choices=[discord.OptionChoice(name="開啟", value="開啟"),
                                                                                  discord.OptionChoice(name="關閉", value="關閉")])):
        data = 0
        stateRlt = False
        if state == "開啟":
            stateRlt = True
        _command = self.matchGuild(ctx.channel.guild.id)
        if _command != None:
            _command.delete = stateRlt
            if _command.delete:
                data = 1

        self.mutex.acquire()

        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from guild_setting where id=?", (ctx.guild.id, ))
        val = cursor.fetchall()
        if val != []:
            _, _, _, _, _, _, _, deleteData = val[0]
            sql = "update guild_setting SET deleteback=? WHERE id=?"
            cursor.execute(sql, (data, ctx.guild.id))

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        embed = self.create_embed(title="切換刪除訊息狀態", description=f"當前狀態已重設為: **{_command.delete}**")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="設置新成員歡迎圖片", description = "請注意只接受png、jpeg、jpg、webp,推薦使用PNG")
    async def welcomePhotoSetting(self, ctx:discord.Interaction, 圖片:discord.Attachment):
        await ctx.response.defer()
        att = 圖片
        content_type = att.content_type[att.content_type.find("/")+1:]
        embed = self.create_embed(color=discord.colour.Color.nitro_pink())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        if content_type.lower() not in ["jpeg", "jpg", "png", "webp"]:
            embed.title = "設定新成員歡迎圖片失敗"
            embed.description = "請使用png、jpeg、jpg、webp等格式檔案"
            await ctx.followup.send(embed=embed)
            return

        await att.save(f"./welcomePhoto/{ctx.guild.id}.png")
        embed.title = "新成員歡迎圖片已設置"
        embed.description = f"圖片大小: **{att.width}**x**{att.height}**\n使用 **/設定新成員歡迎圖頭貼位置參數**\n以進行新成員歡迎圖片後續設定"

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="刪除設置之新成員歡迎圖片", description = "刪除後將使用預設模式傳送新成員歡迎圖片")
    async def welcomePhotoDelete(self, ctx:discord.Interaction):
        embed = self.create_embed(color=discord.colour.Color.nitro_pink())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        booling = False
        if os.path.exists(f"./welcomePhoto/{ctx.guild.id}.png"):
            booling = True
            os.remove(f"./welcomePhoto/{ctx.guild.id}.png")
            embed.title = "刪除設置之新成員歡迎圖片成功"
            embed.description = "將使用預設模式傳送新成員歡迎圖片"
        else:
            embed.title = "刪除設置之新成員歡迎圖片失敗"
            embed.description = "目前未設置新成員歡迎圖片\n已套用預設模式傳送新成員歡迎圖片"
        
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="設置新成員歡迎圖片頭貼位置參數", description = "設定新成員歡迎圖參數")
    async def welcomePhotoParameterSetting(self, ctx:discord.Interaction, 頭貼長寬:discord.Option(int, "設定頭貼的長度與寬度", min_value=100),
                                                                          頭貼旋轉角度:discord.Option(int, "設定頭貼的旋轉角度(+為逆時針,-為順時針)", mix_value=-360, max_value=360),
                                                                          頭貼x座標:discord.Option(int, "設定頭貼於歡迎圖片的X座標", min_value=0),
                                                                          頭貼y座標:discord.Option(int, "設定頭貼於歡迎圖片的Y座標", min_value=0),
                                                                          頭貼是否顯示:discord.Option(str, "新成員頭貼是否顯示在設置之新成員歡迎圖片", 
                                                                                                     choices=[discord.OptionChoice(name="開啟", value="開啟"),
                                                                                                              discord.OptionChoice(name="關閉", value="關閉")])):
        iconDisplay = 頭貼是否顯示
        iconBooling = 1
        if iconDisplay == "關閉":
            iconBooling = 0
        booling = False
        width, height = 0, 0
        side, rorate, coordinateX, coordinateY = 頭貼長寬, 頭貼旋轉角度, 頭貼x座標, 頭貼y座標
        if os.path.exists(f"./welcomePhoto/{ctx.guild.id}.png"):
            booling = True
            img = Image.open(f"./welcomePhoto/{ctx.guild.id}.png")
            width, height = img.size

        embed = self.create_embed(color=discord.colour.Color.nitro_pink())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        if not booling:
            embed.title = "新成員歡迎圖片參數未設置"
            embed.description = "請先使用 **/設置新成員歡迎圖片** 再使用本功能"
            await ctx.response.send_message(embed=embed)
            return
        _command = self.matchGuild(ctx.guild_id)
        _command.photoparameter = [side, rorate, coordinateX, coordinateY, iconBooling]

        self.mutex.acquire()

        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from guild_setting where id=?", (ctx.guild.id, ))
        val = cursor.fetchall()
        if val != []:
            _, _, _, _, photoparameter, _, _, _ = val[0]
            photoparameter = f"{side},{rorate},{coordinateX},{coordinateY},{iconBooling}"
            sql = "update guild_setting SET photoparameter=? WHERE id=?"
            cursor.execute(sql, (photoparameter, ctx.guild.id))

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        embed.title = "新成員歡迎圖片參數已重設"
        string = f"頭貼長寬: **{side}**\n頭貼旋轉角度: **{rorate}**\n頭貼X座標: **{coordinateX}**\n頭貼Y座標: **{coordinateY}**\n頭貼是否顯示: **{iconDisplay}**"
        embed.description = f"設置之圖片長寬: **{width}**x**{height}**\n" + string

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="查詢新成員歡迎圖片頭貼位置參數", description = "設定新成員歡迎圖片參數")
    async def welcomePhotoParameterSearch(self, ctx:discord.Interaction):
        booling = False
        iconBoolingText = "關閉"
        width, height = 0, 0
        if os.path.exists(f"./welcomePhoto/{ctx.guild.id}.png"):
            booling = True
            img = Image.open(f"./welcomePhoto/{ctx.guild.id}.png")
            width, height = img.size

        embed = self.create_embed(color=discord.colour.Color.nitro_pink())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        if not booling:
            embed.title = "新成員歡迎圖片未設置"
            embed.description = "請先使用\n1. **/設置新成員歡迎圖片**\n2. **/設置新成員歡迎圖片頭貼位置參數**"
            await ctx.response.send_message(embed=embed)
            return
        _command = self.matchGuild(ctx.guild_id)
        side, rorate, coordinateX, coordinateY = 0, 0, 0, 0
        if len(_command.photoparameter) == 5:
            side, rorate, coordinateX, coordinateY, iconBooling =  _command.photoparameter
            if iconBooling:
                iconBoolingText = "開啟"
        else:
            embed.title = "未設置新成員歡迎圖片頭貼位置參數"
            embed.description = "請先使用 **/設置新成員歡迎圖片頭貼位置參數**"
            await ctx.response.send_message(embed=embed)
            return
        
        embed.title = "查詢新成員歡迎圖片頭貼位置參數"
        string = f"頭貼長寬: **{side}**\n頭貼旋轉角度: **{rorate}**\n頭貼X座標: **{coordinateX}**\n頭貼Y座標: **{coordinateY}**\n頭貼是否顯示: **{iconBoolingText}**"
        embed.description = f"設置之圖片長寬: **{width}**x**{height}**\n" + string

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="清除新成員歡迎圖片頭貼位置參數", description = "清除新成員歡迎圖片參數")
    async def welcomePhotoParameterDelete(self, ctx:discord.Interaction):
        _command = self.matchGuild(ctx.guild_id)
        embed = self.create_embed(title="清除新成員歡迎圖片頭貼位置參數", description="成功", color=discord.colour.Color.nitro_pink())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        _command.photoparameter = []

        self.mutex.acquire()

        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from guild_setting where id=?", (ctx.guild.id, ))
        val = cursor.fetchall()
        if val != []:
            _, _, _, _, photoparameter, _, _, _ = val[0]
            photoparameter = ""
            sql = "update guild_setting SET photoparameter=? WHERE id=?"
            cursor.execute(sql, (photoparameter, ctx.guild.id))

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="切換新成員歡迎圖片頭貼顯示", description = "切換新成員歡迎圖片頭貼是否顯示於新成員歡迎圖片上")
    async def welcomePhotoParameterIconSwitch(self, ctx:discord.Interaction, 頭貼是否顯示:discord.Option(str, "新成員頭貼是否顯示在設置之新成員歡迎圖片", 
                                                                                                        choices=[discord.OptionChoice(name="開啟", value="開啟"),
                                                                                                                 discord.OptionChoice(name="關閉", value="關閉")])):
        iconDisplayText = 頭貼是否顯示
        iconDisplay = 0
        if iconDisplayText == "開啟":
            iconDisplay = 1
        _command = self.matchGuild(ctx.guild_id)
        embed = self.create_embed(color=discord.colour.Color.nitro_pink())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        if len(_command.photoparameter) == 5:
            side, rorate, coordinateX, coordinateY, iconBooling = _command.photoparameter
            _command.photoparameter[4] = iconDisplay
            iconBooling = iconDisplay

            self.mutex.acquire()

            conn = sqlite3.connect(f"./guild_info.db")
            cursor = conn.cursor()
            cursor.execute("select * from guild_setting where id=?", (ctx.guild.id, ))
            val = cursor.fetchall()
            if val != []:
                _, _, _, _, photoparameter, _, _, _ = val[0]
                photoparameter = f"{side},{rorate},{coordinateX},{coordinateY},{iconBooling}"
                sql = "update guild_setting SET photoparameter=? WHERE id=?"
                cursor.execute(sql, (photoparameter, ctx.guild.id))

            cursor.close()
            conn.commit()
            conn.close()
            self.mutex.release()
            embed.title = "切換新成員歡迎圖片頭貼顯示成功"
            embed.description = f"目前狀態: **{iconDisplayText}**"
        else:
            embed.title = "未切換新成員歡迎圖片頭貼顯示"
            embed.description = "未設定新成員歡迎圖片頭貼位置參數\n無法切換設定"

        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="測試新成員歡迎圖片效果", description = "測試新成員歡迎圖片效果")
    async def welcomePhoto(self, ctx:discord.Interaction):
        await ctx.response.defer()
        _command = self.matchGuild(ctx.guild_id)

        booling = False
        if os.path.exists(f"./welcomePhoto/{ctx.guild.id}.png"):
            booling = True

        background = None
        height, width = 500, 500
        embed = self.create_embed(color=discord.colour.Color.nitro_pink())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        if booling:
            background = Image.open(f"./welcomePhoto/{ctx.guild.id}.png")
            height, width = background.size
        else:
            background = Image.new("RGB", (height, height), color="gray")
            embed.title = "未設置新成員歡迎圖，將使用預設模式"
            embed.description = "如需使用自訂之新成員歡迎圖，請先使用\n1. **/設置新成員歡迎圖片**\n2. **/設置新成員歡迎圖頭貼位置參數**"

        side, rorate, coordinateX, coordinateY, iconControl = 250, 0, 125, 125, 1
        if booling and len(_command.photoparameter) == 5:
            side, rorate, coordinateX, coordinateY, iconControl = _command.photoparameter
            
        if side > height or side > width:
            embed.title = "參數設置有誤"
            embed.description = "頭貼長寬大於設定圖片之長度或寬度\n使用 **/查詢新成員歡迎圖頭貼位置參數**\n可查詢當前設定之參數"
            await ctx.followup.send(embed=embed)
            return
        if coordinateX > height or coordinateY > width:
            embed.title = "參數設置有誤"
            embed.description = "X座標或Y座標大於設定圖片之長寬\n使用 **/查詢新成員歡迎圖頭貼位置參數**\n可查詢當前設定之參數"
            await ctx.followup.send(embed=embed)
            return
        

        url = ctx.author.display_avatar.url
        response = requests.get(url)
        height, width = side, side #250
        img = Image.open(BytesIO(response.content)).resize((height, width), resample=Image.Resampling.NEAREST)
        img = img.rotate(rorate) #-5
        
        mask_im = Image.new("L", (height, width), 0)
        draw = ImageDraw.Draw(mask_im)
        draw.pieslice([(0, 0), (height, width)], 0, 360, fill=255, outline="white")

        if not iconControl and booling:
            pass
        else:
            background.paste(img, (coordinateX, coordinateY), mask_im) #(3090, 828)

        image_bytes = BytesIO()
        background.save(image_bytes, format="PNG")
        png_data = image_bytes.getvalue()
        picture = discord.File(BytesIO(png_data), filename="file.png")

        embed.set_image(url=f"attachment://file.png")

        await ctx.followup.send(embed=embed, file=picture)

'''
    @commands.slash_command(name="生成圖片", description = "生成圖片")
    async def 生成圖片(self, ctx:discord.Interaction, 
                      prompt:str, 
                      negative_prompt: discord.Option(str, "負面提示詞", default=""), 
                      step:discord.Option(int, "num_inference_steps :[10, 30], default:20", default=20, min_value=10, max_value=30), 
                      scale:discord.Option(int, "guidance_scale: [3, 8], default:7", default=7, min_value=3, max_value=8), 
                      height:discord.Option(int, "長度, default:512", default=512, min_value=300, max_value=1500), 
                      width:discord.Option(int, "寬度, default:512", default=512, min_value=300, max_value=1500), 
                      spoiler:discord.Option(int, "是否設置為暴雷內容", default=1, 
                                             choices=[discord.OptionChoice(name="是", value=1),
                                                      discord.OptionChoice(name="否", value=0)])):
        await ctx.response.defer()
        height = height //8 * 8
        width = width // 8 * 8
        img = self.anything.run(p=prompt, np=negative_prompt, step=step, scale=scale, height=height, width=width)
        negative_prompt_embed_print = negative_prompt
        if negative_prompt == "":
            negative_prompt_embed_print = "default"
        embed = self.create_embed(description=f"prompt: {prompt}\n\nnegative_prompt: {negative_prompt_embed_print}")
        embed.set_footer(text="小夕葉 ∙ SD model based on Anything V5", icon_url=self.client.user.avatar.url)
        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            filename = "image.png"
            if spoiler:
                filename = "SPOILER_image.png"
            await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename=filename))
 '''