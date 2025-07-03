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
import threading
import datetime

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
        self.help = {"/set_channel":"設定 YOASOBI「アイドル」觀看次數 頻道", 
                     "/clean_channel":"清除 YOASOBI「アイドル」觀看次數 頻道", 
                     "/check":"確認 YOASOBI「アイドル」觀看次數", 
                     "/clock_start":"開始定時傳送「アイドル」觀看次數訊息", 
                     "/clock_end":"停止定時傳送「アイドル」觀看次數訊息", 
                     "/p":"@使用者以獲得頭貼", 
                     "/d":"指定數量，檢索當前訊息以前指定數量的訊息，刪除其中機器人指令或純數字訊息", 
                     "/set":"設置機器人對@someone回覆{設置內容}，設置內容 clear 即為刪除回覆訊息。", 
                     "/font":"更改$m的字型", 
                     "/隨機身分組抽籤":"標註身分組並指定數量，可以根據設定隨機抽籤", 
                     "/設定新人歡迎訊息":"可指定稱謂(預設成員)，並設置自訂新人歡迎訊息", 
                     "/查看新人歡迎訊息":"查看目前設定之新人歡迎訊息", 
                     "/隨機":"用空白隔開選項，可隨機獲得一個結果", 
                     "/設定身分組語音頻道":"標註若干身分組以設定語音頻道", 
                     "/查看月份帳單排名":"指定月份即可查看茜的帳單排行榜", 
                     "/設定圖片":"提供圖片名字並添加附件，以在發送訊息時添加關鍵字{圖片名字}", 
                     "/查詢圖片列表":"可查詢發送訊息會觸發的關鍵字圖片列表", 
                     "/刪除圖片":"可刪除發送訊息會觸發的關鍵字圖片", 
                     "/個人帳單":"@someone可查看茜的該成員之個人帳單", 
                     "/查詢伺服器個人卡片":"@someone即可查詢伺服器個人卡片", 
                     "/設定伺服器個人卡片暱稱":"@someone即可設定伺服器個人卡片暱稱", 
                     "/查詢伺服器個人卡片排行榜":"可查詢伺服器個人卡片排行榜",
                     "/查看個人運勢":"可查看今日運勢，一人一天最多只能使用3次。\n如果抽中大吉好像會發生什麼事...？", 
                     "/我喜歡妳":"勇敢跟小夕葉告白\n看看會不會被接受吧！", 
                     "/查詢我喜歡妳回答列表":"可查看小夕葉可能會有的答覆...？", 
                     "/設定系統身分組":"可設定/查看個人運勢抽中大吉添加之身分組", 
                     "/查看系統身分組":"可查看/查看個人運勢抽中大吉添加之身分組", 
                     }

    def create_embed(self, title=None, description=None, color=discord.Colour.nitro_pink()):
        embed = discord.Embed(
            title=title,
			description=description,
			colour=color
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    @discord.ui.select(
        placeholder = "請選擇想要查詢的指令",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="/set_channel",
                description="點擊以查看指令/set_channel內容!"
            ),
            discord.SelectOption(
                label="/clean_channel",
                description="點擊以查看指令/clean_channel內容!"
            ), 
            discord.SelectOption(
                label="/check",
                description="點擊以查看指令/check內容!"
            ), 
            discord.SelectOption(
                label="/clock_start",
                description="點擊以查看指令/clock_start內容!"
            ), 
            discord.SelectOption(
                label="/clock_end",
                description="點擊以查看指令/clock_end內容!"
            ), 
            discord.SelectOption(
                label="/p",
                description="點擊以查看指令/p內容!"
            ), 
            discord.SelectOption(
                label="/d",
                description="點擊以查看指令/d內容!"
            ), 
            discord.SelectOption(
                label="/set",
                description="點擊以查看指令/set內容!"
            ), 
            discord.SelectOption(
                label="/font",
                description="點擊以查看指令/font內容!"
            ), 
            discord.SelectOption(
                label="/隨機身分組抽籤",
                description="點擊以查看指令/隨機身分組抽籤內容!"
            ), 
            discord.SelectOption(
                label="/查看新人歡迎訊息",
                description="點擊以查看指令/查看新人歡迎訊息內容!"
            ), 
            discord.SelectOption(
                label="/隨機",
                description="點擊以查看指令/隨機內容!"
            ), 
            discord.SelectOption(
                label="/查看月份帳單排名",
                description="點擊以查看指令/查看月份帳單排名內容!"
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
                label="/個人帳單",
                description="點擊以查看指令/個人帳單內容!"
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
            )
        ])
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
        embed.set_footer(text="小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
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
#----------------------------------------------------------

class Commands(commands.Cog):
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
    
    def matchGuild(self, guild_id:int):
        _command = None
        for i in self.command_lst:
            if i.id == guild_id:
                _command = i
                break
        return _command

    @commands.command()
    async def 設定圖片(self, ctx:discord.Interaction, message=None):
        _command = self.matchGuild(ctx.guild.id)
        photo = ctx.message.attachments
        embed = self.create_embed(title="🔑 | 設定圖片", color=discord.Color.from_rgb(110, 245, 189))
        if photo != [] and message != None:
            att = photo[0]
            content_type = att.content_type[att.content_type.find("/")+1:]

            if content_type not in ["jpeg", "jpg", "png", "gif", "webp"] or att.size > 10000000:
                embed.description = "小夕葉不喜歡這個，哼！"
                # await ctx.respond(">>> 小夕葉不喜歡這個，哼！") 
            else:
                path = f"./photo/{_command.id}"
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
                full_path = f"{path}/{message}.{content_type}"
                await att.save(full_path)
                _command.photo[message] = content_type
                
                embed.description = f"關鍵字: __**{message}**__\n圖片已設置成功"
        else:
            embed.description = f"缺少圖片附件或圖片名字"

        await ctx.send(embed=embed)

    @commands.command()
    async def m(self, ctx, message=None):
        reference = ctx.message.reference
        msg = None
        if reference != None:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        else:
            embed = self.create_embed(description=f"使用指令: **$m**\n請回覆訊息")
            embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.display_avatar.url)
            await ctx.send(embed=embed)
            await ctx.message.delete()
            return
        
        checkValue = msg.content
        checkValue = re.sub("<.{10,50}>", "", checkValue)
        checkValue = re.sub("```[a-z]{1,5}", "", checkValue)
        lst = ["~", "#", "_", ">", "|", "*", "`", "　"]
        for i in lst:
            checkValue = checkValue.replace(i, " ")
        checkValue = re.sub(" +", " ", checkValue)

        if checkValue == "" or checkValue == " ":
            embed = self.create_embed(description=f"使用指令: **$m**\n訊息無內容")
            embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.display_avatar.url)
            await ctx.send(embed=embed)
            await ctx.message.delete()
            return

        text = checkValue.strip()
        url = msg.author.display_avatar.url
        response = requests.get(url)
        height, width = 500, 500
        img = Image.open(BytesIO(response.content)).resize((height, width), resample=Image.Resampling.NEAREST)
        height, width = img.size
        
        mask_im = Image.new("L", (height, width), 0)
        draw = ImageDraw.Draw(mask_im)
        draw.pieslice([(0, 0), (height, width)], 0, 360, fill = 255, outline = "white")

        # mask_im_blur = mask_im.filter(ImageFilter.GaussianBlur(10))
        pic = Image.new(mode="RGB", size=(1000, 400), color=(0, 0, 0, 100))
        pic.paste(img, (-100, -50), mask_im)

        draw = ImageDraw.Draw(pic)

        width_split = 13
        if len(text) >= width_split:
            l = text.split("\n")
            w = max([len(i.strip()) for i in l])
            if w > 22:
                width_split = 22
            else:
                width_split = w
        if len(text) < width_split:
            if len(text) < 4:
                width_split = 4
            else:
                width_split = len(text)

        try:
            wid = int(message)
            if wid > 22 or wid < 4:
                embed = self.create_embed(description=f"使用指令: **$m**\n設置長度 {wid} 不在 uniform[4, 22] 內")
                embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.display_avatar.url)
                await ctx.send(embed=embed)
                await ctx.message.delete()
                return
            width_split = wid
        except:
            pass

        lines = []
        cnt = 0
        string = ""
        for i, j in enumerate(text):
            if j == "\n":
                if string == "":
                    continue
                lines.append(string.strip())
                string = ""
                cnt = 0
                continue
            if string == "" and j == " ":
                cnt -= 1
            string += j
            cnt += 1
            if cnt == width_split or i == (len(text) - 1):
                lines.append(string.strip())
                string = ""
                cnt = 0

        _command = self.matchGuild(ctx.channel.guild.id)
        tf, tf2 = "HanyiSentyTang", ""
        if _command.font != None:
            tf = _command.font
        ratio = int(45 / (width_split / 13))
        font = ImageFont.truetype(f"./font/{tf}.ttf", ratio)
        font2 = ImageFont.truetype(f"./font/{tf}.ttf", 35)
        if len(lines) > 7:
            embed = self.create_embed(description=f"使用指令: **$m**\n訊息過長")
            embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.display_avatar.url)
            await ctx.send(embed=embed)
            return
        for i, line in enumerate(lines):
            if line == "":
                continue
            if len(lines) == 1:
                y = 210 / (width_split**(1/6) / 13**(1/6))
            else:
                form = (width_split**(1/3) / 13**(1/3))
                y = int((68 / form)) + (i+1) * 200 / len(lines)
            draw.text((700, y), line, font=font, fill=(255, 255, 255), anchor="mb")

        # draw.text((430, 130), text, (255,255,255), font=font, anchor="mb")
        # draw.text((450, 220), f"by {msg.author.name}", (255, 255, 255), font=font2, anchor="rs")
        display_name = msg.author.display_name
        for i, j in enumerate(display_name):
            if j == "(" or j == "（":
                display_name = display_name[:i]
                break
        draw.text((955, 370), f"by {display_name}", (255, 255, 255), font=font2, anchor="rs")
        display = f"{width_split} / {ratio}"
        if width_split == 13:
            display = "default"
        image_bytes = BytesIO()
        pic.save(image_bytes, format="PNG")
        png_data = image_bytes.getvalue()
        picture = discord.File(BytesIO(png_data), filename="file.png")
        embed = self.create_embed(description=f"使用指令: **$m**\n字型：**__{tf}__**\n(一行字數/字級: {display})")
        embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.display_avatar.url)
        embed.set_image(url=f"attachment://file.png")

        await ctx.send(embed=embed, file=picture)
        await ctx.message.delete()

    @commands.command()
    async def p(self, ctx, message=None):
        lst = ctx.message.mentions
        reference = ctx.message.reference
        author = None
        if lst == [] and reference == None:
            await ctx.send(">>> 請回覆訊息或@使用者")
            return
        if lst != []:
            author = lst[-1]
        if reference != None:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            author = msg.author
        display_name = ctx.message.author.display_name
        for i, j in enumerate(display_name):
            if j == "(" or j == "（":
                display_name = display_name[:i]
                break
        url = author.display_avatar.url
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.save("./tmp2.png")
        with open("./tmp2.png", 'rb') as f:
            picture = discord.File(f)
            await ctx.send(f">>> 由 **__{display_name}__** 產生", file=picture)
        await ctx.message.delete()

    @commands.command()
    async def set(self, ctx, message=None):
        lst = ctx.message.mentions
        if lst == []:
            await ctx.send(">>> 請@使用者")
            return
        process = re.sub(" +", " ", ctx.message.content)
        processLst = process.split(" ")
        content = None
        if len(processLst) >= 2:
            content = " ".join(processLst[2:])
        else:
            content = ""
        df = None
        display_name_author = ctx.message.author.display_name
        for i, j in enumerate(display_name_author):
            if j == "(" or j == "（":
                display_name_author = display_name_author[:i]
                break
        display_name = lst[0].display_name
        for i, j in enumerate(display_name):
            if j == "(" or j == "（":
                display_name = display_name[:i]
                break

        pathlib.Path("./response").mkdir(parents=True, exist_ok=True)
        try:
            df = pd.read_csv(f"./response/{ctx.channel.guild.id}.csv", index_col=None, encoding="cp950")
        except FileNotFoundError:
            df = pd.DataFrame(columns=["member", "word"])
            df.to_csv(f"./response/{ctx.channel.guild.id}.csv", index=False, encoding="cp950")
            df = pd.read_csv(f"./response/{ctx.channel.guild.id}.csv", index_col=None, encoding="cp950")

        if lst[0].name not in df.member.values:
            data = pd.DataFrame(data={"member":[lst[0].name], "word":[content]}, columns=["member", "word"])
            df = pd.concat([df, data], ignore_index=True)
            df.to_csv(f"./response/{ctx.channel.guild.id}.csv", index=False, encoding="cp950")
            await ctx.send(f">>> {display_name_author} 對 {display_name} \n設置 {content} 成功")
        else:
            data = {"member":lst[0].name, "word":content}
            val = df.index[df['member'] == lst[0].name].tolist()[0]
            df.loc[val] = data
            df.to_csv(f"./response/{ctx.channel.guild.id}.csv", index=False, encoding="cp950")
            await ctx.send(f">>> {display_name_author} 對 {display_name} \n設置 {content} 成功")

        await ctx.message.delete()

    @commands.command()
    async def bill(self, ctx, message=None):
        lst = ctx.message.mentions
        bill_df = None
        month = ctx.message.created_at.month
        try:
            bill_df = pd.read_csv(f"./bill/{ctx.channel.guild.id}_bill_{month}.csv", index_col=None, encoding="cp950")
        except FileNotFoundError:
            bill_df = pd.DataFrame(columns=["date", "name", "money"])
            bill_df.to_csv(f"./bill/{ctx.channel.guild.id}_bill_{month}.csv", index=False, encoding="cp950")
            bill_df = pd.read_csv(f"./bill/{ctx.channel.guild.id}_bill_{month}.csv", index_col=None, encoding="cp950")

        process = re.sub(" +", " ", ctx.message.content)
        processLst = process.split(" ")
        if lst != []:
            mention = lst[-1].name
            display_name = lst[-1].display_name
            for i, j in enumerate(display_name):
                if j == "(" or j == "（":
                    display_name = display_name[:i]
                    break
            df_cp = bill_df[bill_df["name"] == mention].copy()
            string = f">>> ## 茜的{month}月份帳單明細\nby __{display_name}__\n\n"
            string2 = f">>> ## 茜的{month}月份帳單明細\nby __{display_name}__\n\n"
            total = 0
            data_size = len(df_cp.index)
            df_cp.index = [i for i in range(data_size)]
            string2 += "...\n"
            for i in range(len(df_cp.index)):
                tmp = df_cp.loc[i].values
                if data_size > 10:
                    if i >= df_cp.index[-10]:
                        string2 += f"{tmp[0]:<30}{tmp[2]:>10}元\n"
                else:
                    string += f"{tmp[0]:<30}{tmp[2]:>10}元\n"

                total += tmp[2]

            avg = None
            if data_size == 0:
                avg = "0"
            else:
                avg = f"{total / data_size:.3f}"
            string += f"\n總共茜了 {data_size} 次車資\n共 {total} 元\n平均一次茜 {avg} 元"
            string2 += f"\n總共茜了 {data_size} 次車資\n共 {total} 元\n平均一次茜 {avg} 元"
            # string += f"\n次數： {}total: {total:>10}元"
            if data_size <= 10:
                await ctx.send(string)
            else:
                await ctx.send(string2)
        else:
            total = 0
            data_size = len(bill_df.index)
            for i in range(data_size):
                tmp = bill_df.loc[i].values
                total += tmp[2]
            await ctx.send(f">>> 茜總共茜了 {data_size} 次車資\n共 {total} 元")

    @commands.command()
    async def roles(self, ctx, message=None):
        roles = ctx.channel.guild.roles[1:]
        string = ""
        for i in roles:
            string += f"{i}: {i.id}\n"
        await ctx.send(f">>> {string.strip()}")

    @commands.command()
    async def count(self, ctx, message=None):
        roles = ctx.channel.guild.roles[1:]
        string = ""
        for i in roles:
            string += f"{i.name}: {len(i.members)}\n"
        await ctx.send(f">>> {string.strip()}")

    @commands.command()
    async def c(self, ctx, message=None):
        lst = ["eurico0929", "GoodTF_87", "sakanyan6776", "mikannyuuba"]
        limit = ["1105729753505341501", "1109939011298005164"]
        roles = ctx.channel.guild.roles[1:]
        for i in roles:
            if str(i.id) in limit:
                lst += [member.name for member in i.members]

        if ctx.message.author.name not in lst:
            await ctx.send(f">>> {ctx.message.author.name} 沒有更改權限")
            await ctx.message.delete()
            return

        _command = None
        for i in self.command_lst:
            if i.id == ctx.channel.guild.id:
                _command = i

        if _command != None:
            _command.command = not _command.command
        await ctx.send(f">>> $c目前狀態：{_command.command}")
        await ctx.message.delete()

    #待修改
    @commands.command()
    async def clear(self, ctx, message=None):
        lst = ["eurico0929", "sakanyan6776"]
        limit = ["1105729753505341501", "1109939011298005164"]
        roles = ctx.channel.guild.roles[1:]
        for i in roles:
            if str(i.id) in limit:
                lst += [member.name for member in i.members]

        if ctx.message.author.name not in lst:
            await ctx.send(f">>> {ctx.message.author.name} 沒有清除權限")
            return
        df = pd.DataFrame(columns=["member", "word"])
        df.to_csv(f"./{ctx.channel.guild.id}.csv", index=False, encoding="cp950")

    @commands.command()
    async def d(self, ctx, message=None):
        num = 30
        try:
            num_ = int(message)
            if num_ < 30 and num_ > 0:
                num = num_
        except:
            pass

        lst = [m async for m in ctx.channel.history(limit=num+1)]
        lst = list(lst)[1:]
        for i in lst:
            if i.author == self.client.user:
                await i.delete()
            if i.content.isdigit():
                await i.delete()
            if "$" in i.content:
                await i.delete()

        await asyncio.sleep(1)
        await ctx.message.delete()

    #待修改
    @commands.command()
    async def sudoDel(self, ctx, message=None):
        lst = ["eurico0929", "sakanyan6776"]
        limit = ["1105729753505341501", "1109939011298005164"]
        display_name_author = ctx.message.author.display_name
        for i, j in enumerate(display_name_author):
            if j == "(" or j == "（":
                display_name_author = display_name_author[:i]
                break
        roles = ctx.channel.guild.roles[1:]
        for i in roles:
            if str(i.id) in limit:
                lst += [member.name for member in i.members]

        if ctx.message.author.name not in lst:
            await ctx.send(f">>> {display_name_author} 沒有刪除權限")
            return

        reference = ctx.message.reference
        if reference != None:
            msg = ctx.channel.get_partial_message(ctx.message.reference.message_id)
            history = [m async for m in ctx.channel.history(after=msg.created_at)]
            history = list(history)
            if len(history) != 0:
                for i in history[:-1]:
                    if i.attachments != []:
                        continue
                    await i.delete()
                    
            # await ctx.send(ctx.message.reference.cached_message.created_at)
        else:
            await ctx.send("請回覆訊息再使用指令:sudoDel")

        await asyncio.sleep(1)
        await ctx.send(f">>> **__{display_name_author}__** 使用指令: sudoDel")
        await ctx.message.delete()

    @commands.command()
    async def cal(self, ctx, message=None):
        reference = ctx.message.reference
        if reference != None:
            await ctx.send(f">>> {ctx.message.author.name} 使用指令: $cal")
            t1 = time.time()
            msg = ctx.channel.get_partial_message(ctx.message.reference.message_id)
            history = [m async for m in ctx.channel.history(after=msg.created_at)]
            history = list(history)
            if len(history) != 0:
                messageHistory = []
                for i in history[:-1]:
                    if i.attachments == []:
                        continue

                    authorLst = []
                    react = i.reactions
                    total_cnt = 0
                    if react != []:
                        for j, k in enumerate(react):
                            total_cnt += k.count
                            async for user in k.users():
                                authorLst.append(user.name)

                    length = []
                    length_cnt = 0
                    for a in authorLst:
                        if a not in length:
                            length.append(a)
                            length_cnt += 1
                        else:
                            total_cnt -= 1

                    if length_cnt != 0:
                        messageHistory.append((i, total_cnt))
                        # await i.reply(f">>> 票數: {length_cnt}", mention_author=False)

                messageHistory.sort(key=lambda c:c[1], reverse=True)
                for i, j in messageHistory[:3]:
                    await i.reply(f">>> 票數: {j}", mention_author=False)
            
            t2 = time.time()

            await ctx.send(f">>> 計票結束\n共花費 {t2 - t1}s")
        else:
            await ctx.send("請回覆訊息再使用指令:cal")
        await ctx.message.delete()

    @commands.command()
    async def new1A2B(self, ctx, message=None):
        msg = message
        try:
            int(msg)
        except:
            await ctx.send(f">>> 輸入不是數字喔~")
            return
        guild_id = ctx.channel.guild.id

        global _1A2B_lst
        guild_game = None
        for i in _1A2B_lst:
            if guild_id == i.id:
                guild_game = i
                break
        
        if guild_game != None:
            if guild_game.status == None:
                play_1A2B_num = int(msg)
                if play_1A2B_num < 10:
                    while True:
                        string = "".join([str(i) for i in random.sample([i for i in range(10)], play_1A2B_num)])
                        if string[0] == "0":
                            string = "".join([str(i) for i in random.sample([i for i in range(10)], play_1A2B_num)])
                            continue
                        break
                    guild_game.update(string, play_1A2B_num, 0)
                    await ctx.send(f">>> 1A2B遊戲設置成功！\n設定位數: {msg}\n設定答案: ||{guild_game.string}||")
                else:
                    await ctx.send(f">>> 輸入數字請小於10喔~")
            else:
                await ctx.send(f"遊戲正在進行中~無法進行新設置~")

    @commands.command()
    async def h(self, ctx:discord.Interaction, message=None):
        _command = self.matchGuild(ctx.guild.id)
        view = selectView(self.client, _command)
        embed = self.create_embed(title="HELP", description="請選擇要查詢的指令類型", color=discord.Colour.nitro_pink())
        await ctx.send(embed=embed, view=view)














    @commands.command()
    async def h(self, ctx, message=None):
        string = ">>> "
        string += "## $new1A2B {數字}\n__說明__:\n開啟位數為{數字}的1A2B遊戲。\n"
        string += "## $cal\n__說明__:\n回覆特定訊息，自動計算該訊息以後的圖片所有表情貼的數量，並扣掉重複的人。\n"
        string += "## $d {數字(不填預設30)}\n__說明__:\n檢索當前訊息以前{數字}筆的訊息，並將其中是機器人的發言或是純數字訊息刪掉。\n"
        string += "## $sudoDel\n__說明__:\n回覆特定訊息，自動刪除該訊息以後的所有訊息，需具有特定權限。\n"
        string += "## $count\n__說明__:\n列出所有身分組與其人數。\n"
        string += "## $set @someone {設置內容}\n__說明__:\n設置機器人對@someone回覆{設置內容}，設置內容留空即為刪除回覆訊息。\n"
        string += "## $c\n__說明__:\n切換機器人設置訊息是否啟用的開關，需具有特定權限。\n"
        string += "## $bill @someone\n__說明__:\n會列出利用該用戶含有'茜'的對話產生的帳單，留空只有次數和總額。\n"
        string += "## $m {6-20任意整數(可不填)}\n__說明__:\n回覆任意訊息，並根據所填數字設定一行之字數及自動縮放字級，以產生該訊息內容的圖片。須注意貼圖和表情符號無法正常使用。\n(字型由魚大提供)\n"
        string += "## $p @someone\n__說明__:\n回覆訊息或@someone，可取得該使用者頭貼原圖。\n"

        await ctx.send(string)
        await ctx.message.delete()