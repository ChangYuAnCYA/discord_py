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
import sqlite3


class Event(commands.Cog):
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
        embed.set_footer(text="小小夕葉 ∙ 讓群聊機器人成為可能", icon_url=self.client.user.avatar.url)
        return embed

    def matchGuild(self, guild_id:int):
        _command = None
        for i in self.command_lst:
            if i.id == guild_id:
                _command = i
                break
        return _command

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # await ctx.send(error)
        with open("./error_log.txt", "a+") as f:
            print(error, file=f)

    @commands.Cog.listener()
    async def on_ready(self):
        print('bot 身份：', self.client.user)
        lst = list(self.client.guilds)
        pathlib.Path("./response").mkdir(parents=True, exist_ok=True)
        pathlib.Path("./id_card").mkdir(parents=True, exist_ok=True)
        setting = {"response":["member", "word"]}
        self.mutex.acquire()
        for i in lst:
            for folder in setting:
                try:
                    df = pd.read_csv(f"./{folder}/{i.id}.csv", index_col=None, encoding="cp950")

                except FileNotFoundError:
                    df = pd.DataFrame(columns=setting[folder])
                    df.to_csv(f"./{folder}/{i.id}.csv", index=False, encoding="cp950")
#-----------------------------------------------------------------------------------------
            conn = sqlite3.connect(f"./id_card/{i.id}.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data'")
            if cursor.fetchall() == []:
                cursor.execute("create table data (id int primary key, name varchar(30), \
                                nick varchar(30), msg_count int, emoji_count int, last_msg varchar(100), last_msg_time varchar(30))")
            cursor.close()
            conn.commit()
            conn.close()
#-----------------------------------------------------------------------------------------
            conn = sqlite3.connect(f"./guild_info.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guild_setting'")
            if cursor.fetchall() == []:
                cursor.execute("create table guild_setting (id int primary key, system_role int, call varchar(100), message varchar(2000), photoparameter varchar(1000), addrole varchar(2000), font varchar(100), deleteback int)")

            cursor.execute("select * from guild_setting where id=?", (i.id, ))
            val = cursor.fetchall()
            
            addrole = []
            font = None
            delete = False
            photoParameter = []

            if val == []:
                cursor.execute(f"insert into guild_setting (id, system_role, call, message, photoparameter, addrole, font, deleteback) values ({i.id}, 0, \'\', \'\', \'\', \'\', \'\', 0)")
            else:
                _, _, _, _, photoParameterData, addroleData, fontData, deleteData = val[0]
                if addroleData != "":
                    addroleData = [role_info.split("-") for role_info in addroleData.split(",")]
                    addrole = [(discord.utils.get(i.roles, id=int(role_info[0])), int(role_info[1])) for role_info in addroleData]
                if fontData != "":
                    font = fontData
                if deleteData:
                    delete = True
                if photoParameterData != "":
                    lst = photoParameterData.split(",")
                    photoParameter = [int(data) for data in lst]


            cursor.close()
            conn.commit()
            conn.close()
#-----------------------------------------------------------------------------------------
            path = f"./photo/{i.id}"
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)

            self._1A2B_lst.append(_1A2B(i.id))
            tmp = Command(i.id, message=addrole, font=font, delete=delete, photoparameter=photoParameter)

            file_lst = list(pathlib.Path(path).glob("*.*"))
            file_lst = [i for i in file_lst if ".txt" not in i.name]
            file_dict = {j.name[:j.name.find(".")]:j.name[j.name.find(".")+1:] for j in file_lst}
            tmp.photo = file_dict
            self.command_lst.append(tmp)
#-----------------------------------------------------------------------------------------
            path = "./property/"
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(f"./property/{i.id}.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='property'")
            if cursor.fetchall() == []:
                cursor.execute("create table property (id int primary key, name varchar(30), \
                                cash int, stock_info varchar(1000), stock_deposit varchar(1000), \
                                trading_volume int, trading_money int, work int)")
            cursor.close()
            conn.commit()
            conn.close()
#-----------------------------------------------------------------------------------------

        self.mutex.release()
        with open("./error_log.txt", "w") as f:
            pass
        #discord.Status.<狀態>，可以是online,offline,idle,dnd,invisible
        await self.client.change_presence(status=discord.Status.online)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.mutex.acquire()
        setting = {"response":["member", "word"]}
        
        for folder in setting:
            try:
                df = pd.read_csv(f"./{folder}/{guild.id}.csv", index_col=None, encoding="cp950")

            except FileNotFoundError:
                df = pd.DataFrame(columns=setting[folder])
                df.to_csv(f"./{folder}/{guild.id}.csv", index=False, encoding="cp950")

        conn = sqlite3.connect(f"./id_card/{guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data'")
        if cursor.fetchall() == []:
            cursor.execute("create table data (id int primary key, name varchar(30), \
                            nick varchar(30), msg_count int, emoji_count int, last_msg varchar(100), last_msg_time varchar(30))")
        cursor.close()
        conn.commit()
        conn.close()
#------------------------------------------------------------------------------------------------
        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guild_setting'")
        if cursor.fetchall() == []:
            cursor.execute("create table guild_setting (id int primary key, system_role int, call varchar(100), message varchar(2000), photoparameter varchar(1000), addrole varchar(2000), font varchar(100), deleteback int)")

        cursor.execute(f"insert into guild_setting (id, system_role, call, message, photoparameter, addrole, font, deleteback) values ({guild.id}, 0, \'\', \'\', \'\', \'\', 0)")     
        cursor.close()
        conn.commit()
        conn.close()
#------------------------------------------------------------------------------------------------
        path = f"./photo/{guild.id}"
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        self._1A2B_lst.append(_1A2B(guild.id))
        tmp = Command(guild.id)

        file_lst = list(pathlib.Path(path).glob("*.*"))
        file_dict = {i.name[:i.name.find(".")]:i.name[i.name.find(".")+1:] for i in file_lst}
        tmp.photo = file_dict
        self.command_lst.append(tmp)

        self.mutex.release()
        #print(f"{self.client.user} join {guild.name} now!")
#-----------------------------------------------------------------------------------------
        path = "./property/"
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(f"./property/{guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='property'")
        if cursor.fetchall() == []:
            cursor.execute("create table property (id int primary key, name varchar(30), \
                            cash int, stock_info varchar(1000), stock_deposit varchar(1000), \
                            trading_volume int, trading_money int, work int)")
        cursor.close()
        conn.commit()
        conn.close()
#-----------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message): #:discord.InteractionMessage
        #await self.client.wait_until_ready()
        if not self.client.is_ready():
            return
        if message.author == self.client.user:
            return
        if message.author.bot:
            return
        cmd =  re.search("[\$].{1,10} {0,1}", message.content)
        if cmd != None:
            cmd = cmd[0].replace("$", "")
            if cmd in self.client_cmd_lst:
                await self.client.process_commands(message)

        if message.content == "":
            return
        if message.content[0] == "$":
            return
    #------------------------------------------------------------------
        # if "茜" in message.content:
        #     bill_df = None
        #     month = message.created_at.month
        #     year = message.created_at.year
        #     try:
        #         bill_df = pd.read_csv(f"./bill/{message.channel.guild.id}_bill_{month}_{year}.csv", index_col=None, encoding="cp950")
        #     except FileNotFoundError:
        #         bill_df = pd.DataFrame(columns=["date", "name", "money"])
        #         bill_df.to_csv(f"./bill/{message.channel.guild.id}_bill_{month}_{year}.csv", index=False, encoding="cp950")
        #         bill_df = pd.read_csv(f"./bill/{message.channel.guild.id}_bill_{month}_{year}.csv", index_col=None, encoding="cp950")

        #     date = message.created_at + datetime.timedelta(hours=8)
        #     data = pd.DataFrame(data={"date":[date.strftime("%Y/%m/%d   %H:%M:%S")], 
        #                             "name":[message.author.name], 
        #                             "money":[random.randint(100, 500)]}, 
        #                             columns=["date", "name", "money"])
        #     bill_df = pd.concat([bill_df, data], ignore_index=True)
        #     bill_df.to_csv(f"./bill/{message.channel.guild.id}_bill_{month}_{year}.csv", index=False, encoding="cp950")
    #------------------------------------------------------------------
        _command = self.matchGuild(message.guild.id)
        if _command != None:
            if _command.command:
                df = pd.read_csv(f"./response/{message.channel.guild.id}.csv", index_col=None, encoding="cp950")
                val = df.index[df['member'] == message.author.name].tolist()
                if val != []:
                    _, word = df.loc[val[0]]
                    word = str(word)
                    if word != str("nan"):
                        await message.reply(f">>> {word}", mention_author=False)
    #------------------------------------------------------------------
        if message.content in _command.photo.keys():
            types = _command.photo.get(message.content)
            full_path = f"./photo/{message.guild.id}/{message.content}.{types}"
            reference = message.reference
            msg = None
            if reference != None:
                msg = message.channel.get_partial_message(message.reference.message_id)
            else:
                msg = message
            with open(full_path, "rb") as f:
                photo = discord.File(f, filename=f"file.{types}")
                embed = self.create_embed() #description=f"by __**{message.author.display_name}**__"
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                embed.set_image(url=f"attachment://file.{types}")
                await msg.reply(file=photo, embed=embed, mention_author=False)
                if msg.id != message.id:
                    await message.delete()
    #------------------------------------------------------------------
        guild_game = None
        for i in self._1A2B_lst:
            if message.channel.guild.id == i.id:
                guild_game = i
                break

        if guild_game != None:
            if guild_game.status:
                string = guild_game.call(message.content)
                if string != None:
                    await message.reply(string, mention_author=False)
    #------------------------------------------------------------------
        emoji_lst = re.findall("<:.{1,20}:[0-9]{15,25}>", message.content)
        date = message.created_at + datetime.timedelta(hours=8)
        str_date = date.strftime("%Y/%m/%d %H:%M:%S")
        rule = re.split("<:.{1,20}:[0-9]{15,25}>", message.content)
        rule_string = "".join(rule)
        save_msg = message.content
        if len(rule_string) > 20:
            save_msg = message.jump_url

        save_msg = save_msg.replace("\\", "")
#------------------------------------------------------------------
        self.mutex.acquire()

        conn = sqlite3.connect(f"./id_card/{message.guild.id}.db")
        cursor = conn.cursor()
        cursor.execute("select * from data where id=?", (message.author.id, ))
        val = cursor.fetchall()
        
        if val != []:
            _, _, _, msg_count, emoji_count, _, _ = val[0]
            sql = "update data SET msg_count=?, emoji_count=?, last_msg=?, last_msg_time=? WHERE id=?"
            cursor.execute(sql, (msg_count + 1, emoji_count + len(emoji_lst), save_msg, str_date, message.author.id))

        else:
            cursor.execute(f"insert into data (id, name, nick, msg_count, emoji_count, last_msg, last_msg_time) \
                            values ({message.author.id}, \'{message.author.name}\', \'{'無'}\', {1}, {len(emoji_lst)}, \'{save_msg}\', \'{str_date}\')")

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()
#------------------------------------------------------------------
        s = None
        if "/status/" in message.content:
            if "https://twitter.com/" in message.content:
                s = "https://twitter.com/"
            elif "https://x.com/" in message.content:
                s = "https://x.com/"

            if s != None:
                s = message.content.replace(s, "https://vxtwitter.com/")
                s = f"{s}\nby **__{message.author.display_name}__**\n"
                twitterMsg = await message.channel.send(s)
                # embed = twitterMsg.embeds[0]
                # await message.channel.send(embed=embed)

                await message.delete()
#------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        memberLength = len(member.guild.members)

        self.mutex.acquire()

        conn = sqlite3.connect(f"./guild_info.db")
        cursor = conn.cursor()
        cursor.execute("select * from guild_setting where id=?", (member.guild.id, ))
        val = cursor.fetchall()
        
        call, message = "成員", None
        if val != []:
            _, _, call_db, message, _, _, _, _ = val[0]
            if call_db != "":
                call = call_db

        cursor.close()
        conn.commit()
        conn.close()
        self.mutex.release()
#-----------------------------------------------------------------------------
        _command = self.matchGuild(member.guild.id)

        booling = False
        if os.path.exists(f"./welcomePhoto/{member.guild.id}.png"):
            booling = True

        background = None
        height, width = 500, 500
        embed = self.create_embed(color=discord.colour.Color.nitro_pink())
        embed.set_author(name=self.client.user.display_name, icon_url=self.client.user.display_avatar.url)
        if booling:
            background = Image.open(f"./welcomePhoto/{member.guild.id}.png")
            height, width = background.size
        else:
            background = Image.new("RGB", (height, height), color="gray")

        side, rorate, coordinateX, coordinateY, iconControl = 250, 0, 125, 125, 1
        if booling and len(_command.photoparameter) == 5:
            side, rorate, coordinateX, coordinateY, iconControl = _command.photoparameter
            
        if side > height or side > width or coordinateX > height or coordinateY > width:
            background = Image.new("RGB", (height, height), color="gray")
            side, rorate, coordinateX, coordinateY = 250, 0, 125, 125
        
        url = member.display_avatar.url
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
#-----------------------------------------------------------------------------
        string = f"歡迎 <@{member.id}>\n成為第 **__{memberLength}__** 位{call}"
        if message != None and message != "":
            string += "\n" + message
        embed.description = string

        await channel.send(embed=embed, file=picture)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message == None:
            return
        _command = self.matchGuild(message.guild.id)
        
        if not _command.delete:
            return

        embed = self.create_embed(title="有人無情偷刪訊息", description="")
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        if message.content == "" and message.attachments == []:
            return
        if message.author == self.client.user:
            return
        if message.author.name == "mikannyuuba":
            return
        if message.content != "":
            if message.content[0] == "$":
                return
            embed.description += message.content
        if message.attachments != []:
            # for i in message.attachments:
            #     embed.description += i.proxy_url + "\n"
            # embed.description = embed.description.strip("\n")
            await message.channel.send(embed=embed, files=[await i.to_file() for i in message.attachments])
            return
        
        await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, RawReactionActionEvent):
        _command = self.matchGuild(RawReactionActionEvent.guild_id)
        if _command.message == []:
            return
        
        id_lst = [i[1] for i in _command.message]
        msg_dict = {i[1]:i[0] for i in _command.message}
        role = None
        try:
            tmp = id_lst.index(RawReactionActionEvent.message_id)
            role = msg_dict[id_lst[tmp]]
        except:
            return
        
        if role != None:
            r = [i.id for i in role.members]
            if RawReactionActionEvent.member.id not in r:
                await RawReactionActionEvent.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, RawReactionActionEvent):
        _command = self.matchGuild(RawReactionActionEvent.guild_id)
        guild = self.client.get_guild(RawReactionActionEvent.guild_id)
        if _command.message == []:
            return
        
        id_lst = [i[1] for i in _command.message]
        msg_dict = {i[1]:i[0] for i in _command.message}
        role = None
        try:
            tmp = id_lst.index(RawReactionActionEvent.message_id)
            role = msg_dict[id_lst[tmp]]
        except:
            return
        
        if role != None:
            r = [i.id for i in role.members]
        member = guild.get_member(RawReactionActionEvent.user_id)
        if RawReactionActionEvent.user_id in r:
            await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_update(self, before:discord.Member, after:discord.Member):
        category = {i.name:i for i in before.guild.categories}
        cate = None
        if category.get("身分組數量") == None:
            return

        cate = category["身分組數量"]
        len_before = len(before.roles)
        len_after = len(after.roles)
        if len_before != len_after:
            before_roles = {i.name:i for i in before.roles}
            after_roles = {i.name:i for i in after.roles}
            role = None
            if len_before > len_after:
                for i in before_roles:
                    if i not in list(after_roles.keys()):
                        role = before_roles[i]
                        break
            else:
                for i in after_roles:
                    if i not in list(before_roles.keys()):
                        role = after_roles[i]
                        break
            overwrites = {
                before.guild.default_role: discord.PermissionOverwrite(connect=False),
            }
            voice_channel = cate.voice_channels
            for i, j in enumerate(voice_channel):
                name_ch = j.name[:j.name.find(":")]
                if name_ch == role.name:
                    name = f"{role.name}: {len(role.members)}"
                    await j.delete()
                    await asyncio.sleep(1)
                    ch = await cate.create_voice_channel(name=name, 
                                                    position=i, 
                                                    user_limit=0, 
                                                    overwrites=overwrites)
                    # await j.edit(name=name)
                    break