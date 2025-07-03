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
from io import BytesIO
import pandas as pd
import time
import math
import asyncio
import datetime
import sqlite3
import threading
import numpy as np
import stock
import discord_colorize

class Modal(discord.ui.Modal):
    def __init__(self, client, stock, embedName, embedDescription, mode, mutex:threading.Lock):
        super().__init__(title=embedName)
        self.client = client
        self.stock = stock
        self.embedName = embedName
        self.embedDescription = embedDescription
        self.mode = mode
        self.mutex = mutex
        self.question = discord.ui.InputText(label="請輸入股票代號")
        self.add_item(self.question)
        # self.title = "股票系統"

    def create_embed(self, title=None, description=None, color=discord.Colour.nitro_pink()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    async def callback(self, ctx:discord.Interaction):
        embed = self.create_embed(title=self.embedName, description=self.embedDescription)
        modalView = ModalView(self.client, ctx.user.id, "個人股票設定", self.embedDescription, self.stock, self.mutex)
        if self.stock.stock_info.get(self.question.value) != None:
            if self.mode == "add_stock" and self.question.value not in self.embedDescription:
                embed.description = f"{self.embedDescription}\n{self.question.value}  {self.stock.stock_info.get(self.question.value)}".strip()
            elif self.mode == "del_stock" and self.question.value in self.embedDescription:
                embed.description = self.embedDescription.replace(f"{self.question.value}  {self.stock.stock_info.get(self.question.value)}", "").strip()

            modalView.embedDescription = embed.description
            #self.embedDescription += self.stock.stock_info.get(self.question.value)

        if embed.description != "":
            modalView.get_item("save").disabled = False
        
        await ctx.response.edit_message(embed=embed, view=modalView)

class ModalView(discord.ui.View):
    def __init__(self, client, author_id, embedName, embedDescription, stock, mutex:threading.Lock):
        super().__init__()
        self.client = client
        self.id = author_id
        self.embedName = embedName
        self.embedDescription = embedDescription
        self.stock = stock
        self.mutex = mutex

    def create_embed(self, title=None, description=None, color=discord.Colour.nitro_pink()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    @discord.ui.button(label="追加新股票", style=discord.ButtonStyle.secondary, emoji="📈", custom_id="add_stock")
    async def button_callback(self, button, ctx:discord.Interaction):
        if self.id != ctx.user.id:
            return
        await ctx.response.send_modal(Modal(self.client, self.stock, self.embedName, self.embedDescription, "add_stock", self.mutex))

    @discord.ui.button(label="刪除股票", style=discord.ButtonStyle.danger, emoji="❌", custom_id="del_stock")
    async def button_callback2(self, button, ctx:discord.Interaction):
        if self.id != ctx.user.id:
            return
        if self.embedDescription == "":
            return
        await ctx.response.send_modal(Modal(self.client, self.stock, self.embedName, self.embedDescription, "del_stock", self.mutex))

    @discord.ui.button(label="存檔", style=discord.ButtonStyle.primary, emoji="✔️", custom_id="save", disabled=True)
    async def button_callback3(self, button, ctx:discord.Interaction):
        if self.id != ctx.user.id:
            return

        self.disable_all_items()
        embed = self.create_embed(title="存檔成功", description="5秒後將自動刪除本訊息")
        embedOrg = self.create_embed(title=self.embedName, description=self.embedDescription)

        lst = re.findall("\d+ {2,2}", self.embedDescription)
        lst = [i.strip() for i in lst]

        self.mutex.acquire()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        val = cursor.fetchall()

        lstString = ",".join(lst)
        if val != []:
            sql = "update property SET stock_info=? WHERE id=?"
            cursor.execute(sql, (lstString, ctx.user.id))

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        await ctx.channel.send(embed=embed, delete_after=5)
        await ctx.response.edit_message(embed=embedOrg, view=self)

class StockModal(discord.ui.Modal):
    def __init__(self, client, stock:stock.TaiwanStock, embed:discord.Embed, stockList:list, mode, stockToday, buy_or_sell, mutex:threading.Lock):
        super().__init__(title=embed.title)
        self.client = client
        self.stock = stock
        self.embed = embed
        self.stockList = stockList
        self.mode = mode
        self.stockToday = stockToday
        self.buy_or_sell = buy_or_sell
        self.mutex = mutex
        self.question = discord.ui.InputText(label="請輸入股票代號")
        self.add_item(self.question)
        self.piece = discord.ui.InputText(label="股數")
        self.add_item(self.piece)
        # self.title = "股票系統"

    def create_embed(self, title=None, description=None, color=discord.Colour.nitro_pink()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    async def callback(self, ctx:discord.Interaction):
        await ctx.response.defer()
        stockView = StockView(self.client, ctx.user.id, self.embed, self.stock, self.stockList, self.stockToday, self.buy_or_sell, self.mutex)
        if self.buy_or_sell == "buy":
            if self.stock.stock_info.get(self.question.value) != None:
                if self.mode == "buy_stock":
                    if self.piece.value.isnumeric():
                        if self.question.value not in self.stockList:
                            now = datetime.datetime.now()
                            t = now - datetime.timedelta(days=7)
                            strToday = now.strftime("%Y-%m-%d")
                            t_strToday = t.strftime("%Y-%m-%d")
                            df = self.stock.get_stock(stock_id=self.question.value, start_date=t_strToday, end_date=strToday)
                            if not df.empty:
                                date_stock_name = self.stock.stock_info[self.question.value]
                                yesterday_close, close = df["close"].tolist()[-2], df["close"].tolist()[-1]
                                num = round(100*((close/yesterday_close)-1), 3)
                                self.stockToday[self.question.value] = [date_stock_name, close, yesterday_close, num]

                                self.stockList.append(self.question.value)
                                self.embed.description = f"{self.embed.description}\n{self.question.value}  {self.stock.stock_info.get(self.question.value)}    {close} / {self.piece.value}".strip()
                        else:
                            string = re.search(f"{self.question.value}  {self.stock.stock_info.get(self.question.value)}    \d+\.\d+ / \d+", self.embed.description)[0]
                            lst = re.split(" +", string.replace("/", ""))
                            # s = re.search(f"{self.question.value}  {self.stock.stock_info.get(self.question.value)} / {lst[2]} / \d+", self.embed.description)[0]
                            self.embed.description = self.embed.description.replace(string, f"{self.question.value}  {self.stock.stock_info.get(self.question.value)}    {lst[2]} / {self.piece.value}")

                elif self.mode == "del_stock" and self.question.value in self.stockList:
                    self.stockList.remove(self.question.value)
                    string = re.search(f"{self.question.value}  {self.stock.stock_info.get(self.question.value)}    \d+\.\d+ / \d+", self.embed.description)[0]
                    lst = re.split(" +", string.replace("/", ""))
                    #s = re.search(f"{self.question.value}  {self.stock.stock_info.get(self.question.value)} / {s} / \d+", self.embed.description)[0]
                    self.embed.description = self.embed.description.replace(string, "").strip().replace("\n\n", "\n")

            if self.embed.description.replace(f"股票代號 公司名稱    股價 / 股數\n{30*'-'}", "").strip() != "":
                stockView.get_item("save").disabled = False
            else:
                stockView.get_item("save").disabled = True

        else:
            if self.mode == "sell_stock":
                if self.piece.value.isnumeric():
                    if self.question.value in self.stockList:
                        #f"欄位: 股票ID(公司)  收盤 / 損益率 | 持有 / 賣出\n{30*'-'}\n"
                        string = re.search(f"{self.question.value}\({self.stock.stock_info.get(self.question.value)}\)  \d+\.\d+ / -?\d+\.\d+% \| \d+ / \d+", self.embed.description)[0]
                        lst = re.split(" +", string.replace("/", "").replace("|", "").replace("%", ""))
                        value = 0
                        if int(self.piece.value) <= int(lst[3]):
                            value = int(self.piece.value)
                        new = f"{lst[0]}  {lst[1]} / {lst[2]}% | {lst[3]} / {value}"
                        self.embed.description = self.embed.description.replace(string, new)

            if self.embed.description.replace(f"欄位: 股票ID(公司)  收盤 / 損益率 | 持有 / 賣出\n{30*'-'}\n", "").strip() != "":
                stockView.get_item("sell_save").disabled = False
            else:
                stockView.get_item("sell_save").disabled = True
        
        await ctx.followup.edit_message(ctx.message.id, embed=self.embed, view=stockView)
        # await ctx.response.edit_message(embed=self.embed, view=stockView)

class StockView(discord.ui.View):
    def __init__(self, client, author_id, embed:discord.Embed, stock, stockList, stockToday, buy_or_sell, mutex:threading.Lock):
        super().__init__(timeout=600)
        self.client = client
        self.id = author_id
        self.embed = embed
        self.stock = stock
        self.stockList = stockList
        self.stockToday = stockToday
        self.buy_or_sell = buy_or_sell
        self.mutex = mutex

        if self.buy_or_sell == "sell":
            self.remove_item(self.get_item("buy_stock"))
            self.remove_item(self.get_item("del_stock"))
            self.remove_item(self.get_item("save"))
        else:
            self.remove_item(self.get_item("sell_stock"))
            self.remove_item(self.get_item("sell_save"))

    def numberFormat(self, numberString):
        string = numberString
        if "-" in numberString:
            string = string[1:]
        s = ""
        for i, j in enumerate(string[::-1]):
            s += j
            if (i + 1) % 3 == 0:
                s += " ,"
        s = s[::-1].strip(", ")

        if "-" in numberString:
            s = "-" + s

        return s

    def create_embed(self, title=None, description=None, color=discord.Colour.nitro_pink()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    @discord.ui.button(label="購買或更新股票張數", style=discord.ButtonStyle.secondary, emoji="📈", custom_id="buy_stock")
    async def button_callback(self, button, ctx:discord.Interaction):
        if self.id != ctx.user.id:
            return
        await ctx.response.send_modal(StockModal(self.client, self.stock, self.embed, self.stockList, "buy_stock", self.stockToday, self.buy_or_sell, self.mutex))

    @discord.ui.button(label="賣出股票股數", style=discord.ButtonStyle.secondary, emoji="📈", custom_id="sell_stock")
    async def button_callback_(self, button, ctx:discord.Interaction):
        if self.id != ctx.user.id:
            return
        await ctx.response.send_modal(StockModal(self.client, self.stock, self.embed, self.stockList, "sell_stock", self.stockToday, self.buy_or_sell, self.mutex))

    @discord.ui.button(label="刪除股票", style=discord.ButtonStyle.danger, emoji="❌", custom_id="del_stock")
    async def button_callback2(self, button, ctx:discord.Interaction):
        if self.id != ctx.user.id:
            return
        if self.embed.description == "":
            return
        
        modal = StockModal(self.client, self.stock, self.embed, self.stockList, "del_stock", self.stockToday, self.buy_or_sell, self.mutex)
        modal.remove_item(modal.piece)

        await ctx.response.send_modal(modal=modal)

    @discord.ui.button(label="確定購買", style=discord.ButtonStyle.success, emoji="✔️", custom_id="save", disabled=True)
    async def button_callback3(self, button, ctx:discord.Interaction):
        await ctx.response.defer()
        if self.id != ctx.user.id:
            return

        self.disable_all_items()
        embed = self.create_embed(title=self.embed.title, description=self.embed.description)
        # embedOrg = self.create_embed(title=self.embed.title, description=self.embed.description)

        stockLst = None
        stockDict = None
        lst = re.findall("\d+ {2,2}.{1,50} {2,2}\d+\.\d+ / \d+", self.embed.description)
        stockLst = [re.split(" +", i.strip().replace("/", "")) for i in lst]
        stockDict = {i[0]:(float(i[2]), int(i[3])) for i in stockLst}
        total = sum([int(stockDict[i][0] * stockDict[i][1]) for i in stockDict.keys()])
        
        self.mutex.acquire()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        val = cursor.fetchall()
        if val != []:
            _, _, cash, _, stockProperty, _, _, _ = val[0]
            if cash >= total:
                oldLst = stockProperty.split(";")
                oldLstAll = [i.split(",") for i in oldLst]
                oldDict = {i[0]:int(i[1]) for i in oldLstAll if len(i) == 2 and self.stock.stock_info.get(i[0]) != None}
                for i in stockDict.keys():
                    if oldDict.get(i) == None:
                        oldDict[i] = stockDict[i][1]
                    else:
                        oldDict[i] = oldDict[i] + stockDict[i][1]

                sqlLst = [f"{i},{oldDict[i]}" for i in oldDict.keys()]
                sqlString = ";".join(sqlLst)               
                sql = "update property SET cash=?,stock_deposit=? WHERE id=?"
                cursor.execute(sql, (cash - int(1.01*total), sqlString, ctx.user.id))
                embed.description += f"\n\n已購買成功，共花費```{int(1.01*total)} 元(含手續費)```"
            else:
                self.enable_all_items()
                embed.description += f"\n\n購買失敗，餘額不足"
            
        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        await ctx.followup.edit_message(ctx.message.id, embed=embed, view=self)

    @discord.ui.button(label="確定賣出", style=discord.ButtonStyle.danger, emoji="✔️", custom_id="sell_save", disabled=True)
    async def button_callback3_(self, button, ctx:discord.Interaction):
        await ctx.response.defer()
        if self.id != ctx.user.id:
            return

        self.disable_all_items()
        embed = self.create_embed(title=self.embed.title, description=self.embed.description)
        lst = re.findall("\d+[^\d]{3,20}\d+\.\d+ / -?\d+\.\d+% \| \d+ / \d+", self.embed.description)
        stockLst = [re.split(" +", i.strip().replace("/", "").replace("|", "").replace("%", "")) for i in lst]
        stockDict = {re.search("\d+", i[0])[0]:(float(i[1]), int(i[4])) for i in stockLst if int(i[4]) != 0}
        total = sum([int(stockDict[i][0] * stockDict[i][1]) for i in stockDict.keys()])

        self.mutex.acquire()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        val = cursor.fetchall()
        if val != []:
            _, _, cash, _, stockProperty, _, _, _ = val[0]

            oldLst = stockProperty.split(";")
            oldLstAll = [i.split(",") for i in oldLst]
            oldDict = {i[0]:int(i[1]) for i in oldLstAll if len(i) == 2 and self.stock.stock_info.get(i[0]) != None}

            for i in stockDict.keys():
                if oldDict.get(i) != None:
                    oldDict[i] = oldDict[i] - stockDict[i][1]

            sqlLst = [f"{i},{oldDict[i]}" for i in oldDict.keys() if oldDict[i] > 0]
            sqlString = ";".join(sqlLst)               
            sql = "update property SET cash=?,stock_deposit=? WHERE id=?"
            cursor.execute(sql, (cash + int(0.99*total), sqlString, ctx.user.id))
            embed.description += f"\n\n已賣出成功，共```{self.numberFormat(str(int(0.99*total)))} 元(含手續費)```存款: {self.numberFormat(str(cash + int(0.99*total)))} 元"

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        await ctx.followup.edit_message(ctx.message.id, embed=embed, view=self)

    @discord.ui.button(label="取消交易", style=discord.ButtonStyle.primary, emoji="🌸", custom_id="cancel")
    async def button_callback4(self, button, ctx:discord.Interaction):
        
        self.disable_all_items()
        self.embed.description = "使用者已取消交易"

        await ctx.response.edit_message(embed=self.embed, view=self, delete_after=5)

class gambleView(discord.ui.View):
    def __init__(self, client, author_id, embed:discord.Embed, cash:int, money:int, prob:int, mutex:threading.Lock):
        super().__init__()
        self.client = client
        self.id = author_id
        self.embed = embed
        self.cash = cash
        self.money = money
        self.orgMoney = money
        self.time = 1
        self.p = prob
        self.mutex = mutex

    def numberFormat(self, numberString):
        string = numberString
        if "-" in string:
            string = string[1:]
        s = ""
        for i, j in enumerate(string[::-1]):
            s += j
            if (i + 1) % 3 == 0:
                s += " ,"
        s = s[::-1].strip(", ")

        if "-" in numberString:
            s = "-" + s

        return s

    def updateSql(self, ctx, money):
        self.mutex.acquire()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        valStock = cursor.fetchall()

        if valStock != []:
            _, _, cash, _, _, _, _, _ = valStock[0]
            if self.cash != cash:
                self.embed.description = self.embed.description.replace(f"所持存款: {self.numberFormat(str(self.cash))}", f"所持存款: {self.numberFormat(str(cash))}")
                self.cash = cash
            sql = "update property SET cash=? WHERE id=?"
            cursor.execute(sql, (cash - money, ctx.user.id))
        else:
            print("please check sql")
            
        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

    def create_embed(self, title=None, description=None, color=discord.Colour.nitro_pink()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    @discord.ui.button(label="加注", style=discord.ButtonStyle.secondary, emoji="💰", custom_id="加注")
    async def button_callback(self, button, ctx:discord.Interaction):
        if self.id != ctx.user.id:
            return
        
        p = self.p - 10 * (self.time - 1)
        NextP = self.p - 10 * (self.time)
        if p < 10:
            p = 10
        if NextP < 10:
            NextP = 10

        p = p / 100
        rlt = np.random.choice([0, 1], p=[1-p, p])
        if rlt:
            self.money = int(self.orgMoney * (1.2 + (self.time - 1) * 0.3))
            NextMoneyRatio = round(1.2 + self.time * 0.3, 1)
            self.time += 1
            self.embed.set_field_at(0, name=self.embed.fields[0].name, value=self.numberFormat(str(self.money)))
            self.embed.set_field_at(1, name=self.embed.fields[1].name, value=NextMoneyRatio)
            self.embed.set_field_at(2, name=self.embed.fields[2].name, value=f"{NextP} %")
            self.embed.set_field_at(5, name=self.embed.fields[5].name, value=f"{self.orgMoney} x {NextMoneyRatio} = {self.numberFormat(str(int(self.orgMoney * NextMoneyRatio)))}")
            await ctx.response.edit_message(embed=self.embed, view=self)
        else:
            self.updateSql(ctx, self.orgMoney)
            self.disable_all_items()
            embed = self.create_embed(title=self.embed.title, description=self.embed.description, color=discord.Color.nitro_pink())
            embed.description += f"\n成功次數: {self.time-1}次\n已失去賭下資金共 {self.numberFormat(str(self.orgMoney))} 元，請再接再厲...\n剩餘存款: {self.cash} - {self.orgMoney} = ```{self.numberFormat(str(self.cash-self.orgMoney))} 元```"
            embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
            await ctx.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="放棄", style=discord.ButtonStyle.danger, emoji="❌", custom_id="放棄")
    async def button_callback2(self, button, ctx:discord.Interaction):
        if self.id != ctx.user.id:
            return
        
        self.updateSql(ctx, -(self.money - self.orgMoney))
        self.disable_all_items()
        embed = self.create_embed(title=self.embed.title, description=self.embed.description, color=discord.Color.nitro_pink())
        embed.description += f"\n成功次數: {self.time-1}次\n最終獲得資金共 {self.numberFormat(str(self.money))} 元\n存款: {self.cash} + {self.money - self.orgMoney} = ```{self.numberFormat(str(self.cash + self.money - self.orgMoney))} 元```"
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        await ctx.response.edit_message(embed=embed, view=self)

class Stock_command(commands.Cog):
    def __init__(self, client, _1A2B_lst, command_lst, client_cmd_lst, mutex:threading.Lock):
        self.client = client
        self._1A2B_lst = _1A2B_lst
        self.command_lst = command_lst
        self.client_cmd_lst = client_cmd_lst
        self.mutex = mutex
        self.stock = stock.TaiwanStock()
        self.stockToday = {}
        self.reset.start()
        
    @tasks.loop(time=datetime.time(hour=23, minute=59, second=59, microsecond=999999, tzinfo=datetime.timezone(datetime.timedelta(hours=8))))
    async def reset(self):
        await self.client.wait_until_ready()
        lst = list(self.client.guilds)
        for i in lst:
            self.mutex.acquire()
            conn = sqlite3.connect(f"./property/{i.id}.db")
            cursor = conn.cursor()
            cursor.execute("update property SET work=0")
            cursor.close()
            conn.commit()
            conn.close()
            self.mutex.release()

    def numberFormat(self, numberString):
        string = numberString
        if "-" in numberString:
            string = string[1:]
        s = ""
        for i, j in enumerate(string[::-1]):
            s += j
            if (i + 1) % 3 == 0:
                s += " ,"
        s = s[::-1].strip(", ")

        if "-" in numberString:
            s = "-" + s

        return s

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

    @commands.slash_command(name="當天股價查詢", description = "輸入股票代碼以查詢當天股價")
    async def stockSearch(self, ctx:discord.Interaction, stock_id:str):
        await ctx.response.defer()
        now = datetime.datetime.now()
        t = now - datetime.timedelta(days=7)
        strToday = now.strftime("%Y-%m-%d")
        t_strToday = t.strftime("%Y-%m-%d")
        df = self.stock.get_stock(stock_id=stock_id, start_date=t_strToday, end_date=strToday)
        embed = None
        if not df.empty:
            embed = self.create_embed(title=f"stock ID: **__{stock_id}__**", color=discord.Color.nitro_pink())
            date_stock_name = self.stock.stock_info[stock_id]
            date = df["date"].tolist()[-1]
            trading_volume = df["Trading_Volume"].tolist()[-1]
            trading_money = df["Trading_money"]
            _open = df["open"].tolist()[-1]
            _max = df["max"].tolist()[-1]
            _min = df["min"].tolist()[-1]
            yesterday_close, close = df["close"].tolist()[-2], df["close"].tolist()[-1]
            spread = df["spread"]
            trading_turnover = df["Trading_turnover"]

            s = ""
            for i, j in enumerate(str(trading_volume)[::-1]):
                s += j
                if (i + 1) % 3 == 0:
                    s += " ,"
            s = s[::-1].strip(", ")

            colors = discord_colorize.Colors()
            num = round(100*((close/yesterday_close)-1), 3)
            f = f"{num} %"
            rate = None
            if num < 0:
                rate = f"""```ansi
                {colors.colorize(f, fg="green")}```"""
            elif num > 0:
                rate = f"""```ansi
                {colors.colorize(f, fg="red")}```"""
            
            if abs(num - 0) < 0.00001:
                rate = f"""```ansi
                {colors.colorize(f, fg="yellow")}```"""

            embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
            embed.description = f"公司名稱: **__{date_stock_name}__**\n時間: **__{date}__**\n{'-'*30}"
            
            embed.add_field(name="---收盤---", value=f"{close}")
            embed.insert_field_at(0, name="---開盤---", value=f"{_open}")
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="---最低點---", value=f"{_min}")
            embed.insert_field_at(4, name="---最高點---", value=f"{_max}")
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="---當日交易量---", value=f"{s}", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="---漲跌幅---", value=rate)
            embed.insert_field_at(11, name="---昨日收盤---", value=f"{yesterday_close}")
        
        else:
            embed = self.create_embed(title=f"stock ID: **__{stock_id}__**", color=discord.Color.nitro_pink(), description="沒有對應公司")
            embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        await ctx.followup.send(embed=embed)
    @commands.slash_command(name="個人股票設定", description = "輸入股票代碼以設定個人股票")
    async def stock_setting(self, ctx:discord.Interaction):
        await ctx.response.defer()
        embed = self.create_embed(title="個人股票設定", color=discord.Color.nitro_pink(), description="")

        self.mutex.acquire()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        val = cursor.fetchall()

        if val != []:
            _, _, _, stock_info, _, _, _, _ = val[0]
            lst = stock_info.split(",")
            lst = [f"{i}  {self.stock.stock_info.get(i)}" for i in lst if self.stock.stock_info.get(i) != None]
            embed.description = "\n".join(lst).strip()
        else:
            cursor.execute(f"insert into property (id, name, cash, stock_info, stock_deposit, trading_volume, trading_money, work) \
                            values ({ctx.user.id}, \'{ctx.user.name}\', {100000}, \'\', \'\', 0, 0, 0)")
            
        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        await ctx.followup.send(embed=embed, view=ModalView(self.client, ctx.user.id, "個人股票設定", embed.description, self.stock, self.mutex))

    @commands.slash_command(name="個人股票查詢", description = "輸入股票代碼以查詢個人股票")
    async def stockSearchPersonal(self, ctx:discord.Interaction):
        await ctx.response.defer()

        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        val = cursor.fetchall()
        cursor.close()
        conn.close()

        embed = self.create_embed(title=f"{self.nameClip(ctx.user.display_name)} / 個人股票查詢", 
                                  description=f"欄位: 股票ID/公司/收盤/昨日收盤/損益率\n{30*'-'}\n", 
                                  color=discord.Color.nitro_pink())
        if val != []:
            _, _, cash, stock_info, _, _, _, _ = val[0]
            embed.description = f"目前存款: {cash} 元\n" + embed.description
            lst = stock_info.split(",")
            for i in lst:
                if self.stockToday.get(i) == None:
                    now = datetime.datetime.now()
                    t = now - datetime.timedelta(days=7)
                    strToday = now.strftime("%Y-%m-%d")
                    t_strToday = t.strftime("%Y-%m-%d")
                    df = self.stock.get_stock(stock_id=i, start_date=t_strToday, end_date=strToday)
                    if not df.empty:
                        date_stock_name = self.stock.stock_info[i]
                        yesterday_close, close = df["close"].tolist()[-2], df["close"].tolist()[-1]
                        num = round(100*((close/yesterday_close)-1), 3)
                        embed.description += f"{i} {date_stock_name} {close} / {yesterday_close} /```{num}```\n"
                        self.stockToday[i] = [date_stock_name, close, yesterday_close, num]
                else:
                    lst = self.stockToday.get(i)
                    embed.description += f"{i} / {lst[0]} / {lst[1]} / {lst[2]} /```{lst[3]}```\n"
                    
            embed.description = embed.description.strip()
        else:
            embed.description = "可使用```/個人股票設定```進行設置"
        
        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="工作", description = "辛勤工作以獲得金錢吧！")
    async def work(self, ctx:discord.Interaction):
        await ctx.response.defer()

        conn = sqlite3.connect(f"./id_card/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from data where id=?", (ctx.user.id, ))
        val = cursor.fetchall()
        cursor.close()
        conn.close()

        embed = self.create_embed(title=f"{self.nameClip(ctx.user.display_name)} / 工作", description="")
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
            ratio = 1
            for i, j in enumerate(range_lst):
                if msg_count >= j:
                    identity = rank[i]
                    ratio += 0.5
                else:
                    lvlup = j - msg_count
                    break

            embed.colour = rank_dict[identity]
            embed.description = f"職稱: {identity}```今日薪資 = 基本薪資 x 職等獎勵```{30*'-'}\n"

            self.mutex.acquire()
            conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
            cursor = conn.cursor()
            cursor.execute("select * from property where id=?", (ctx.user.id, ))
            valStock = cursor.fetchall()

            cash = 100000
            salary = int(1000 * ratio)
            work = None
            if valStock != []:
                _, _, cash, _, _, _, _, work = valStock[0]
                total_money = cash + salary
                if not work:
                    sql = "update property SET cash=?, work=? WHERE id=?"
                    cursor.execute(sql, (total_money, 1, ctx.user.id))
            else:
                total_money = cash + salary
                cursor.execute(f"insert into property (id, name, cash, stock_info, stock_deposit, trading_volume, trading_money, work) \
                                values ({ctx.user.id}, \'{ctx.user.name}\', {total_money}, \'\', \'\', 0, 0, 1)")
                
            cursor.close()
            conn.commit()
            conn.close()
            self.mutex.release()

            if work != 1:
                embed.description += f"1000 x {ratio} = {salary} 元\n存款: {cash} --> {total_money} 元"
            else:
                embed.description = "今天已經工作過囉！"
            
        await ctx.followup.send(embed=embed)
        
    @commands.slash_command(name="查看存款", description = "使用指令即可查看存款")
    async def deposit(self, ctx:discord.Interaction, 標註成員:discord.Member):
        await ctx.response.defer()

        member = 標註成員
        embed = self.create_embed(title=f"{self.nameClip(member.display_name)} / 查看存款", description="")

        self.mutex.acquire()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (member.id, ))
        valStock = cursor.fetchall()
        cash = 100000
        if valStock != []:
            _, _, cash, _, _, _, _, work = valStock[0]
        else:
           cursor.execute(f"insert into property (id, name, cash, stock_info, stock_deposit, trading_volume, trading_money, work) \
                                values ({member.id}, \'{member.name}\', {100000}, \'\', \'\', 0, 0, 1)")
        
        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()
        embed.description = f"{self.numberFormat(str(cash))} 元"

        await ctx.followup.send(embed=embed)
        
    @commands.slash_command(name="央行匯款", description = "使用指令即可匯款(僅夕葉)")
    async def Cremit(self, ctx:discord.Interaction, 標註成員:discord.Member, 匯款金額:discord.Option(int, description = "匯款金額 [-10^11, 10_11]", min_value=-int(math.pow(10, 11))+1, max_value=int(math.pow(10, 11))+1)):
        await ctx.response.defer()
        if ctx.user.name != "mikannyuuba":
            return
        
        member = 標註成員
        remit = 匯款金額
        embed = self.create_embed(title=f"{self.nameClip(ctx.user.display_name)} / 匯款", color=discord.Color.nitro_pink())

        self.mutex.acquire()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (member.id, ))
        valStock = cursor.fetchall()
        cash = 100000
        m = None
        if valStock != []:
            _, _, cash, _, _, _, _, _ = valStock[0]
            sql = "update property SET cash=? WHERE id=?"
            m = cash + remit
            if m < 0:
                m = 0
            cursor.execute(sql, (m, member.id))
        else:
            m = cash + remit
            if m < 0:
                m = 0
            cursor.execute(f"insert into property (id, name, cash, stock_info, stock_deposit, trading_volume, trading_money, work) \
                                values ({member.id}, \'{member.name}\', {m}, \'\', \'\', 0, 0, 1)")
        
        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        embed.description = f"{self.nameClip(ctx.user.display_name)} --> {self.nameClip(member.display_name)}\n存款: {cash} + {remit} = {m}"

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="匯款", description = "使用指令即可匯款")
    async def remit(self, ctx:discord.Interaction, 標註成員:discord.Member, 匯款金額:discord.Option(int, description = "匯款金額 [1, 10_11]", min_value=1, max_value=int(math.pow(10, 11))+1)):
        await ctx.response.defer()
        
        member = 標註成員
        remit = 匯款金額
        embed = self.create_embed(title=f"{self.nameClip(ctx.user.display_name)} / 匯款", color=discord.Color.nitro_pink())
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        valStockSelf = cursor.fetchall()

        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (member.id, ))
        valStockMember = cursor.fetchall()

        cursor.close()
        conn.close()
        m = 0
        if valStockSelf != [] and valStockMember != []:
            if ctx.user.id == member.id:
                embed.description = "匯款雙方不得一樣"
            else:
                _, _, cashSelf, _, _, _, _, _ = valStockSelf[0]
                _, _, cashMember, _, _, _, _, _ = valStockMember[0]

                if cashSelf < 0:
                    if 1.01*cashSelf < remit:
                        m = cashSelf
                    else:
                        m = remit

                    self.mutex.acquire()
                    conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
                    cursor = conn.cursor()
                    sql = "update property SET cash=? WHERE id=?"
                    cursor.execute(sql, (cashSelf - int(1.01* m), ctx.user.id))
                    sql = "update property SET cash=? WHERE id=?"
                    cursor.execute(sql, (cashMember + m, member.id))
                    cursor.close()
                    conn.commit()
                    conn.close()
                    self.mutex.release()

                    embed.description = f"__{self.nameClip(ctx.user.display_name)}__ --> __{self.nameClip(member.display_name)}__\n存款: {cashSelf} - {int(1.01* m)} = {cashSelf - int(1.01* m)}\n手續費: 1%"
                else:
                    embed.description = "匯款失敗，帳戶餘額為負"
        else:
            embed.description = "匯款失敗，其中一方未擁有帳戶"

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="slot", description = "賭上一切！翻倍或0！")
    async def slot(self, ctx:discord.Interaction, 賭資:discord.Option(int, description="資金 >= 1", min_value=1)):
        await ctx.response.defer()
        c = 賭資
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        valStock = cursor.fetchall()
        cursor.close()
        conn.close()
        p = 70

        embed = self.create_embed(title="SLOT", color=discord.Color.nitro_pink())
        view = None
        if valStock != []:
            _, _, cash, _, _, _, _, _ = valStock[0]
            if cash < c:
                embed.description = "所持存款不足"
            else:
                embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
                embed.description = f"所持存款: {self.numberFormat(str(cash))}\n資金: {self.numberFormat(str(c))}\n{30*'-'}"
                embed.add_field(name="資金", value=self.numberFormat(str(c)), inline=False)
                embed.add_field(name="成功機率", value=f"{p} %")
                embed.insert_field_at(1, name="倍率", value=1.2)
                embed.add_field(name="", value="", inline=False)
                embed.add_field(name="", value="", inline=False)
                embed.add_field(name="資金x倍率預覽", value=f"{c} x 1.2 = {self.numberFormat(str(int(c*1.2)))}")
                view = gambleView(self.client, ctx.user.id, embed, cash, c, p, self.mutex)
                pass
        else:
            embed.description = "未進行基礎設置，請使用 /建立帳戶"

        if view:
            await ctx.followup.send(embed=embed, view=view)
        else:
            await ctx.followup.send(embed=embed)
            
    @commands.slash_command(name="建立帳戶", description = "輸入指令即可建立帳戶")
    async def account(self, ctx:discord.Interaction):
        await ctx.response.defer()
        embed = self.create_embed(title=f"{self.nameClip(ctx.user.display_name)} / 建立帳戶", color=discord.Color.nitro_pink())
        self.mutex.acquire()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        valStock = cursor.fetchall()
        if valStock != []:
            _ = valStock[0]
            embed.description = "已經創建過帳戶囉~"
        else:
           cursor.execute(f"insert into property (id, name, cash, stock_info, stock_deposit, trading_volume, trading_money, work) \
                                values ({ctx.user.id}, \'{ctx.user.name}\', {100000}, \'\', \'\', 0, 0, 1)")
           embed.description = "帳戶創建成功\n存款: 100000 元"
        
        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="購買股票", description = "輸入指令即可購買股票")
    async def buyStock(self, ctx:discord.Interaction):
        await ctx.response.defer()
        embed = self.create_embed(title=f"{self.nameClip(ctx.user.display_name)} / 購買股票", color=discord.Color.nitro_pink(), description="")
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)
        embed.description = f"股票代號 公司名稱    股價 / 股數\n{30*'-'}"

        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        val = cursor.fetchall()
        cursor.close()
        conn.close()

        view = StockView(self.client, ctx.user.id, embed, self.stock, [], self.stockToday, "buy", self.mutex)
        if val != []:
            pass
        else:
            embed.description = "請先使用 /建立帳戶"
            view.disable_all_items()

        await ctx.followup.send(embed=embed, view=view)

    @commands.slash_command(name="查看個人持有股票", description = "輸入指令即可查看個人持有股票")
    async def checkStock(self, ctx:discord.Interaction):
        await ctx.response.defer()
        embed = self.create_embed(title=f"{self.nameClip(ctx.user.display_name)} / 查看個人持有股票", color=discord.Color.nitro_pink(), description="")
        embed.description = f"股票代號 / 公司名稱 / 股數\n{30*'-'}\n"
        embed.set_author(name=ctx.user.display_name, icon_url=ctx.user.display_avatar.url)

        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        val = cursor.fetchall()
        cursor.close()
        conn.close()

        if val != []:
            _, _, _, _, stock_property, _, _, _ = val[0]
            lst = stock_property.split(";")
            lstAll = [i.split(",") for i in lst]
            stockLst = [f"{i[0]}  {self.stock.stock_info.get(i[0])} / {i[1]}" for i in lstAll if len(i) == 2 and self.stock.stock_info.get(i[0]) != None]
            embed.description += "\n".join(stockLst)
        else:
            embed.description = "請先使用 /建立帳戶"

        await ctx.followup.send(embed=embed)

    @commands.slash_command(name="賣出股票", description = "輸入指令即可賣出股票")
    async def sellStock(self, ctx:discord.Interaction):
        await ctx.response.defer()

        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where id=?", (ctx.user.id, ))
        val = cursor.fetchall()
        cursor.close()
        conn.close()

        embed = self.create_embed(title=f"{self.nameClip(ctx.user.display_name)} / 賣出股票", 
                                  description=f"欄位: 股票ID(公司)  收盤 / 損益率 | 持有 / 賣出\n{30*'-'}\n", 
                                  color=discord.Color.nitro_pink())
        
        view = StockView(self.client, ctx.user.id, embed, self.stock, [], self.stockToday, "sell", self.mutex)
        if val != []:
            _, _, cash, _, stock_property, _, _, _ = val[0]
            embed.description = f"目前存款: {self.numberFormat(str(cash))} 元\n" + embed.description
            lst = stock_property.split(";")
            lstAll = [i.split(",") for i in lst]
            stockDict = {i[0]:i[1] for i in lstAll if len(i) == 2 and self.stock.stock_info.get(i[0]) != None}
            view.stockList = stockDict.keys()

            now = datetime.datetime.now()
            t = now - datetime.timedelta(days=7)
            strToday = now.strftime("%Y-%m-%d")
            t_strToday = t.strftime("%Y-%m-%d")
            for i in stockDict.keys():
                if self.stockToday.get(i) == None:
                    df = self.stock.get_stock(stock_id=i, start_date=t_strToday, end_date=strToday)
                    if not df.empty:
                        date_stock_name = self.stock.stock_info[i]
                        yesterday_close, close = df["close"].tolist()[-2], df["close"].tolist()[-1]
                        num = round(100*((close/yesterday_close)-1), 3)
                        self.stockToday[i] = [date_stock_name, close, yesterday_close, num]
                        embed.description += f"{i}({date_stock_name})  {close} / {num}% | {stockDict[i]} / 0\n"
                else: 
                    lst = self.stockToday.get(i)       
                    embed.description += f"{i}({lst[0]})  {lst[1]} / {lst[3]}% | {stockDict[i]} / 0\n"
                    
            embed.description = embed.description.strip()
        else:
            view.disable_all_items()
            embed.description = "請先使用 /建立帳戶"          

        await ctx.followup.send(embed=embed, view=view)

    @commands.slash_command(name="抓貪污", description = "輸入指令即可抓貪污")
    async def sellStock111(self, ctx:discord.Interaction):
        await ctx.response.defer()
        conn = sqlite3.connect(f"./property/{ctx.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from property where cash>?", (1000000000, ))
        val = cursor.fetchall()
        cursor.close()
        conn.close()
        money = [f"{i[1]}, {i[2]}" for i in val]
        money.sort(key=lambda x:x[1], reverse=True)
        embed = self.create_embed(description="\n".join(money))

        await ctx.followup.send(embed=embed)