import ast
import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import wikipedia
from deep_translator import GoogleTranslator
import aiohttp
from datetime import datetime


# giveaway button
class giveawayButton(discord.ui.View):
    def __init__(self, *, timeout = None):
        super().__init__(timeout = timeout)
    @discord.ui.button(label = "Participate", style = discord.ButtonStyle.blurple, emoji = "🎉", custom_id="giveaway_button")
    async def giveaway_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiosqlite.connect("db/giveaways.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM giveaways WHERE give_id = ?", (interaction.message.id,))
                data = await cursor.fetchone()
                give_author = data[1]
                give_prize = data[2]
                give_timer = data[3]
                give_icon = data[4]
                give_clicked = ast.literal_eval(data[5])
                if interaction.user.mention in give_clicked:
                    give_clicked.remove(interaction.user.mention)
                    await interaction.response.send_message("You've left the giveaway.", ephemeral = True)
                else:
                    give_clicked.append(interaction.user.mention)
                    await interaction.response.send_message("You've Participated!", ephemeral = True)
                await cursor.execute("UPDATE giveaways SET give_clicked = ? WHERE give_id = ?", (str(give_clicked), interaction.message.id,))
                await db.commit()
        emb = discord.Embed(title = "__*🎉GIVEAWAY🎉*__",
                            description = f"Click 🎉 to enter!\nHosted by: {give_author}\nPrize: **{give_prize}**\nParticipators: **{len(give_clicked)}**\nEnds at: {give_timer}",
                            colour = 0xff0000)
        if give_icon != "no icon": emb.set_thumbnail(url = give_icon)
        view = giveawayButton()
        await interaction.message.edit(embed = emb, view = view)

# poll buttons
class pollButtons(discord.ui.View):
    def __init__(self, *, timeout = None):
        super().__init__(timeout = timeout)
    @discord.ui.button(label = "Yes", style = discord.ButtonStyle.blurple, emoji = "<:pepeyes:1070834912782987424>", custom_id = "poll_yes_button")
    async def poll_yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Fetching poll data...
        async with aiosqlite.connect("db/polls.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM polls WHERE poll_id = ?", (interaction.message.id,))
                data = await cursor.fetchone()
                poll_title = data[1]
                poll_description = data[2]
                poll_author = data[3]
                poll_avatar = data[4]
                upvotes = data[5]
                downvotes = data[6]
                upvote_users = ast.literal_eval(data[7])
                downvote_users = ast.literal_eval(data[8])

                if interaction.user.id in upvote_users:
                    upvotes = upvotes - 1
                    upvote_users.remove(interaction.user.id)
                    await cursor.execute("UPDATE polls SET upvotes = ?, upvote_users = ? WHERE poll_id = ?", (upvotes, str(upvote_users), interaction.message.id,))
                    await interaction.response.send_message("Vote removed.", ephemeral = True)
                elif interaction.user.id in downvote_users:
                    downvotes = downvotes - 1
                    downvote_users.remove(interaction.user.id)
                    upvotes = upvotes + 1
                    upvote_users.append(interaction.user.id)
                    await cursor.execute("UPDATE polls SET upvotes = ?, upvote_users = ?, downvotes = ?, downvote_users = ? WHERE poll_id = ?", (upvotes, str(upvote_users), downvotes, str(downvote_users), interaction.message.id,))
                    await interaction.response.send_message("Voted.", ephemeral = True)
                else:
                    upvotes = upvotes + 1
                    upvote_users.append(interaction.user.id)
                    await cursor.execute("UPDATE polls SET upvotes = ?, upvote_users = ? WHERE poll_id = ?", (upvotes, str(upvote_users), interaction.message.id,))
                    await interaction.response.send_message("Voted.", ephemeral = True)
                await db.commit()
        emb = discord.Embed(title = poll_title, description = poll_description)
        if poll_avatar != "no avatar": emb.set_author(name = f"Poll by {poll_author}", icon_url = poll_avatar)
        else: emb.set_author(name = f"Poll by {poll_author}")
        emb.set_footer(text = f"{upvotes} Yes | {downvotes} No")
        view = pollButtons()
        await interaction.message.edit(embed = emb, view = view)
    #no button
    @discord.ui.button(label = "No", style = discord.ButtonStyle.blurple, emoji = "<:pepeno:1070834894537773087>", custom_id = "poll_no_button")
    async def sugg_downvote(self, interaction: discord.Interaction, button: discord.ui.Button):
         # Fetching poll data...
        async with aiosqlite.connect("db/polls.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM polls WHERE poll_id = ?", (interaction.message.id,))
                data = await cursor.fetchone()
                poll_title = data[1]
                poll_description = data[2]
                poll_author = data[3]
                poll_avatar = data[4]
                upvotes = data[5]
                downvotes = data[6]
                upvote_users = ast.literal_eval(data[7])
                downvote_users = ast.literal_eval(data[8])

                if interaction.user.id in downvote_users:
                    downvotes = downvotes - 1
                    downvote_users.remove(interaction.user.id)
                    await cursor.execute("UPDATE polls SET downvotes = ?, downvote_users = ? WHERE poll_id = ?", (downvotes, str(downvote_users), interaction.message.id,))
                    await interaction.response.send_message("Vote removed.", ephemeral = True)
                elif interaction.user.id in upvote_users:
                    upvotes = upvotes - 1
                    upvote_users.remove(interaction.user.id)
                    downvotes = downvotes + 1
                    downvote_users.append(interaction.user.id)
                    await cursor.execute("UPDATE polls SET downvotes = ?, downvote_users = ?, upvotes = ?, upvote_users = ? WHERE poll_id = ?", (downvotes, str(downvote_users), upvotes, str(upvote_users), interaction.message.id,))
                    await interaction.response.send_message("Voted.", ephemeral = True)
                else:
                    downvotes = downvotes + 1
                    downvote_users.append(interaction.user.id)
                    await cursor.execute("UPDATE polls SET downvotes = ?, downvote_users = ? WHERE poll_id = ?", (downvotes, str(downvote_users), interaction.message.id,))
                    await interaction.response.send_message("Voted.", ephemeral = True)
                await db.commit()
        emb = discord.Embed(title = poll_title, description = poll_description)
        emb.set_author(name = f"Poll by {poll_author}", icon_url = poll_avatar)
        emb.set_footer(text = f"{upvotes} Yes | {downvotes} No")
        view = pollButtons()
        await interaction.message.edit(embed = emb, view = view)

# ui class for invite button
class Invite(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout = timeout)

# vote button class
class Vote(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout = timeout)

# Utility Class
class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #waking
    @commands.Cog.listener()
    async def on_ready(self):
        print("Utility is online.")

    #ping command
    @app_commands.command(name = "ping", description = "Checks Shinobi bot's response time.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f">>> _**Pong!**_\n{round(self.bot.latency * 1000)}ms")

    # advice
    @app_commands.command(name = "advice", description = "Get a random advice.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def advice(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
                async with session.get("https://api.adviceslip.com/advice") as response:
                    data = await response.json(content_type = "text/html")
                    advice = data["slip"]["advice"]
        await interaction.response.send_message(advice)

    # affirmation
    @app_commands.command(name = "affirmation", description = "Get a random affirmation.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def affirmation(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
                async with session.get("https://www.affirmations.dev/") as response:
                    data = await response.json()
                    affirmation = data["affirmation"]
        await interaction.response.send_message(affirmation)

    #wikipedia search
    @app_commands.command(name = "wikipedia", description = "A wikipedia scraper.")
    @app_commands.describe(search = "Whatever you want to search.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def search(self, interaction: discord.Interaction, search: str):
        #usually returns a list, so we turn it into a string, suggestion = true includes suggestions
        searchsearch = str(wikipedia.search(search, suggestion = True)).replace('(', '').replace(')', '').replace("'", "").replace('[', '').replace(']', '')
        try:
            #limits the summary to a maximum of 1950 characters, discord's limit is 2,000 per message
            thesummary = wikipedia.summary(search, chars = 1000)
            summ = thesummary
        except:
            #usually returns a list, so we turn it into a string, suggestion = true includes suggestions
            searchsummary = str(wikipedia.search(search, suggestion = True)).replace('(', '').replace(')', '').replace("'", "").replace('[', '').replace(']', '')
            summ = f"I can't seem to find a summary for that.. Did you mean: {searchsummary}"
        try:
            wikipedia.summary(search, auto_suggest = False) #i think auto suggest is on by default
            wiki_search = search.lower().replace(' ', '_').replace('  ', '_')
            url = f"[Click here to visit {search} wiki page](https://en.wikipedia.org/wiki/{wiki_search})"
        except:
            urlsearch = str(wikipedia.search(search, suggestion = True)).replace('(', '').replace(')', '').replace("'", "").replace('[', '').replace(']', '') 
            url = f"I can't find what you're talking about, did you mean: {urlsearch}"
        seach_embed = discord.Embed(title="Search", description=f"{url}", color = 0x2F3136)
        seach_embed.add_field(name = "**Definition**", value = f">>> {searchsearch}")
        seach_embed.add_field(name = "**Summery**", value = f">>> {summ}")
        await interaction.response.send_message(embed=seach_embed)

    #translate command
    @app_commands.command(name = "translate", description = "A translator.")
    @app_commands.describe(to_language = "The language you want to translate to.", to_translate = "Whatever you want to translate.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def translate(self, interaction: discord.Interaction, to_language: str, to_translate: str):
        translated = GoogleTranslator(source = 'auto', target = to_language).translate(to_translate)
        em = discord.Embed(title = "Translated", color = 0x2F3136)
        em.add_field(name="Original", value = f"> {to_translate}")
        em.add_field(name="Translation", value = f"> {translated}")
        await interaction.response.send_message(embed = em)

    #calculator command
    @app_commands.command(name = "calculator", description = "Makes calculations for you.")
    @app_commands.describe(first_number = "The first number.", operator = "The operator (+, -, ×, ÷).", second_number = "The second number.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def calculator(self, interaction: discord.Interaction, first_number: int, operator: str, second_number: int):
        if operator == "+":
            await interaction.response.send_message(f"Result: **{first_number+second_number}**")
        elif operator == "-":
            await interaction.response.send_message(f"Result: **{first_number-second_number}**")
        elif operator == "*" or operator == "×" or operator == "x":
            await interaction.response.send_message(f"Result: **{first_number*second_number}**")
        elif operator == "/" or operator == "÷":
            await interaction.response.send_message(f"Result: **{first_number/second_number}**")
        else:
            await interaction.response.send_message(f"> You entered a wrong operator.", ephemeral = True)

    #embed command
    @app_commands.command(name = "embed", description = "Change your text into an embed.")
    @app_commands.describe(title = "Title of the embed.", description = "Description of the embed.", footer = "Footer of the embed.", color = "Color of the embed. (default is black)")
    @app_commands.choices(color = [
        app_commands.Choice(name = "dark theme", value = "dark theme"),
        app_commands.Choice(name = "dark grey", value = "dark grey"),
        app_commands.Choice(name = "light grey", value = "light grey"),
        app_commands.Choice(name = "blue", value = "blue"),
        app_commands.Choice(name = "red", value = "red"),
        app_commands.Choice(name = "gold", value = "gold"),
        app_commands.Choice(name = "orange", value = "orange"),
        app_commands.Choice(name = "yellow", value = "yellow"),
        app_commands.Choice(name = "green", value = "green"),
        app_commands.Choice(name = "random", value = "random")
        ])
    @app_commands.choices(thumbnail = [app_commands.Choice(name = "enable", value = "enable")])
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def embed(self, interaction: discord.Interaction, title: str, description: str, footer: str = None, color: app_commands.Choice[str] = None, thumbnail: app_commands.Choice[str] = None):
        if footer == None and color == None and thumbnail == None:
            emb = discord.Embed(title = title, description = description, color = 0x000000)
            await interaction.response.send_message(embed = emb)
        elif footer != None and thumbnail == None and color == None:
            emb = discord.Embed(title = title, description = description, color = 0x000000)
            try: emb.set_footer(text = footer, icon_url = interaction.user.avatar.url)
            except: emb.set_footer(text = footer)
            await interaction.response.send_message(embed = emb)
        elif footer != None and thumbnail != None and color == None:
            emb = discord.Embed(title = title, description = description, color = 0x000000)
            try: emb.set_thumbnail(url = interaction.user.avatar.url)
            except: pass
            try: emb.set_footer(text = footer, icon_url = interaction.user.avatar.url)
            except: emb.set_footer(text = footer)
            await interaction.response.send_message(embed = emb)
        elif thumbnail != None and footer == None and color == None:
            emb = discord.Embed(title = title, description = description, color = 0x000000)
            try: emb.set_thumbnail(url = interaction.user.avatar.url)
            except: pass
            await interaction.response.send_message(embed = emb)
        elif color != None:
            if color.value == "dark theme": true_color = discord.Colour.dark_theme()
            elif color.value == "dark grey": true_color = discord.Colour.dark_grey()
            elif color.value == "light grey": true_color = discord.Colour.light_grey()
            elif color.value == "blue": true_color = discord.Colour.blue()
            elif color.value == "red": true_color = discord.Colour.red()
            elif color.value == "gold": true_color = discord.Colour.gold()
            elif color.value == "orange": true_color = discord.Colour.orange()
            elif color.value == "yellow": true_color = discord.Colour.yellow()
            elif color.value == "green": true_color = discord.Colour.green()
            elif color.value == "random": true_color = discord.Colour.random()
            if footer == None and thumbnail == None:
                emb = discord.Embed(title = title, description = description, color = true_color)
                await interaction.response.send_message(embed = emb)
            elif footer != None and thumbnail == None:
                emb = discord.Embed(title = title, description = description, color = true_color)
                try: emb.set_footer(text = footer, icon_url = interaction.user.avatar.url)
                except: emb.set_footer(text = footer)
                await interaction.response.send_message(embed = emb)
            elif thumbnail != None and footer == None:
                emb = discord.Embed(title = title, description = description, color = true_color)
                try: emb.set_thumbnail(url = interaction.user.avatar.url)
                except: pass
                await interaction.response.send_message(embed = emb)
            else:
                emb = discord.Embed(title = title, description = description, color = true_color)
                try: emb.set_footer(text = footer, icon_url = interaction.user.avatar.url)
                except: emb.set_footer(text = footer)
                try: emb.set_thumbnail(url = interaction.user.avatar.url)
                except: pass
                await interaction.response.send_message(embed = emb)

    #nick commands
    @app_commands.command(name = "nick", description = "Changes the nickname.")
    @app_commands.describe(member = "Member to change their nickname.", nick = "The new nickname.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_nicknames = True)
    async def nick(self, interaction: discord.Interaction, member: discord.Member, nick: str):
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message(f"> Your role must be higher than {member.mention}'s nickname!", ephemeral = True)
        elif interaction.guild.me.top_role <= member.top_role:
                return await interaction.response.send_message(f"> My role must be higher than {member.mention}!", ephemeral = True)
        if member.nick == None: oldn = member.name
        else: oldn = member.nick
        await member.edit(nick = nick)
        await interaction.response.send_message(f"> {member.mention}'s nickname has been changed from **{oldn}** to **{nick}**")

    #giveaway
    @app_commands.command(name = "giveaway", description = "Set a giveaway.")
    @app_commands.describe(time = "Giveaway's time.", prize = "Giveaway's prize.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def giveaway(self, interaction: discord.Interaction, time: str, prize: str):
        try: icon = str(interaction.guild.icon.url)
        except: icon = "no icon"
        if time:
            get_time = {
            "s": 1, "m": 60, "h": 3600, "d": 86400,
            "w": 604800, "mo": 2592000, "y": 31104000 }
            a = time[-1]
            b = get_time.get(a)
            c = time[:-1]
            try: int(c)
            except: return await interaction.response.send_message("> Type time and time unit [s,m,h,d,w,mo,y] correctly.", ephemeral = True)
            try: sleep = int(b) * int(c)
            except: return await interaction.response.send_message("> Type time and time unit [s,m,h,d,w,mo,y] correctly.", ephemeral = True)
        give_timer = f"<t:{int(datetime.timestamp(datetime.now())) + int(sleep)}:F>"
        emb = discord.Embed(title = "__*🎉GIVEAWAY🎉*__",
                            description = f"Click 🎉 to enter!\nHosted by: {interaction.user.mention}\nPrize: **{prize}**\nParticipators: **0**\nEnds at: {give_timer}",
                            colour = 0xff0000)
        if icon != "no icon": emb.set_thumbnail(url = icon)
        view = giveawayButton()
        await interaction.response.send_message("Giveaway Created!", ephemeral = True)
        msg = await interaction.channel.send(embed = emb, view = view)
        async with aiosqlite.connect("db/giveaways.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS giveaways (give_id INTEGER, give_author TEXT, give_prize TEXT, give_timer TEXT, give_icon TEXT, give_clicked TEXT)")
                await cursor.execute("INSERT INTO giveaways (give_id, give_author, give_prize, give_timer, give_icon, give_clicked) VALUES (?, ?, ?, ?, ?, ?)", (msg.id, interaction.user.mention, prize, give_timer, icon, "[]"))
                await db.commit()
        await asyncio.sleep(int(sleep))
        async with aiosqlite.connect("db/giveaways.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT * FROM giveaways WHERE give_id = ?", (msg.id,))
                data = await cursor.fetchone()
                give_clicked = ast.literal_eval(data[5])
        #Check if User list is not empty
        if len(give_clicked) <= 0:
            emptyEmbed = discord.Embed(title = "__*🎉GIVEAWAY🎉*__",
                                       description = f"No one participated in the giveaway\nHosted by: {interaction.user.mention}\nPrize: **{prize}**\nEnded at: {give_timer}")
            emptyEmbed.set_thumbnail(url = icon)
            await msg.edit(embed = emptyEmbed, view = None)
        else:
            winner = random.choice(give_clicked)
            emb = discord.Embed(title = "__*🎉GIVEAWAY🎉*__",
                            description = f"Click 🎉 to enter!\nHosted by: {interaction.user.mention}\nPrize: **{prize}**\nParticipators: **{len(give_clicked)}**\nEnded at: {give_timer}",
                            colour = 0xff0000)
            emb.set_thumbnail(url = icon)
            await msg.edit(content = f"__***🎉Giveway ended, {winner} won!🎉***__", view = None, embed = emb)
            await msg.reply(f"> **Congratulations {winner} On Winning {prize} 🎉🎉**")

    #tax
    @app_commands.command(name = "tax", description = "Calculates ProBot's taxes.")
    @app_commands.describe(amount = "The amount of credits.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def tax(self, interaction: discord.Interaction, amount: int):
        price = int(amount) / 0.95
        price2 = int(amount) * 0.95
        price3 = int(amount) - price2
        emb = discord.Embed(title = "__**Taxes**__ ",
                            description = f"How much ProBot will take: **{int(price3)}**\nHow much will be transfered: **{int(price2)}**\nHow much you should transfer: **{int(price+1)}**",
                            colour = discord.Colour.dark_theme())
        await interaction.response.send_message(embed = emb)

    #timer
    @app_commands.command(name = "timer", description = "A stopwatch for you.")
    @app_commands.describe(time = "The time you want to set.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def timer(self, interaction: discord.Interaction, time: str):
        get_time = {
        "s": 1, "m": 60, "h": 3600, "d": 86400,
        "w": 604800, "mo": 2592000, "y": 31104000 }
        timer = time
        a = time[-1]
        b = get_time.get(a)
        c = time[:-1]
        try: int(c)
        except: return await interaction.response.send_message("> Type time and time unit [s,m,h,d,w,mo,y] correctly.", ephemeral = True)
        try:
            sleep = int(b) * int(c)
            await interaction.response.send_message(f"> Timer set to {timer}.", ephemeral = True)
        except: return await interaction.response.send_message("> Type time and time unit [s,m,h,d,w,mo,y] correctly.", ephemeral = True)
        await asyncio.sleep(sleep)
        await interaction.response.send_message("**Time over**")
        member_dm = await interaction.user.create_dm()
        #await channel.send("**Time over**")
        emb = discord.Embed(title = "**Time over**", description = f"> Your Timer '{timer}' has been ended", color = discord.Colour.random())
        await member_dm.send(embed = emb)

    #server link
    @app_commands.command(name = "serverlink", description = "Gets an invite link for the server.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def serverlink(self, interaction: discord.Interaction):
        name = str(interaction.guild.name)
        link = await interaction.channel.create_invite(max_age = 300)
        embed = discord.Embed(title = name, color = 0x2F3136)
        try: embed.set_thumbnail(url = interaction.guild.icon.url)
        except: pass
        embed.add_field(name = "Invite Link", value = link, inline = True)
        await interaction.response.send_message(embed = embed)

    #bot invite link
    @app_commands.command(name = "invite", description = "Gets an invite link for the bot.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def invite(self, interaction: discord.Interaction):
        view=Invite()
        view.add_item(discord.ui.Button(label = "Invite", style = discord.ButtonStyle.link,
                                        url = "https://discord.com/api/oauth2/authorize?client_id=855437723166703616&permissions=8&scope=bot%20applications.commands"))
        view.add_item(discord.ui.Button(label = "Support Server", style = discord.ButtonStyle.link,
                                        url = "https://discord.gg/YScaCDY7PN"))
        emb = discord.Embed(title = "Bot's invite link",
                            description = "[Invite Link](https://discord.com/api/oauth2/authorize?client_id=855437723166703616&permissions=8&scope=bot%20applications.commands)",
                            colour = 0x2F3136)
        emb.add_field(name="Support Server", value="[Support Server](https://discord.gg/YScaCDY7PN)")
        await interaction.response.send_message(embed = emb, view = view)

    # vote command
    @app_commands.command(name = "vote", description = "Vote Shinobi Bot!")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    async def vote(self, interaction: discord.Interaction):
        view = Vote()
        view.add_item(discord.ui.Button(label = "top.gg", style = discord.ButtonStyle.link, url = "https://top.gg/bot/855437723166703616/vote"))
        view.add_item(discord.ui.Button(label = "discordbotlist", style = discord.ButtonStyle.link, url = "https://discordbotlist.com/bots/shinobi-bot/upvote"))
        emb = discord.Embed(title = "Shinobi Bot's Vote links", description = "https://top.gg/bot/855437723166703616/vote\nhttps://discordbotlist.com/bots/shinobi-bot/upvote")
        await interaction.response.send_message(embed = emb, view = view)

    #poll command
    @app_commands.command(name = "poll", description = "Make a poll.")
    @app_commands.describe(title = "The title of the poll.", description = "The description of the poll.")
    @app_commands.checks.cooldown(1, 10, key = lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_messages = True)
    async def poll(self, interaction: discord.Interaction, title: str, description: str):
        try: user_avatar = interaction.user.avatar.url
        except: user_avatar = "no avatar"
        view = pollButtons()
        emb = discord.Embed(title = title, description = description)
        if user_avatar != "no avatar": emb.set_author(name = f"Poll by {interaction.user.display_name}", icon_url = interaction.user.avatar.url)
        else: emb.set_author(name = f"Poll by {interaction.user.display_name}")
        emb.set_footer(text = f"0 Yes | 0 No")
        await interaction.response.send_message("Poll Created!", ephemeral=True)
        poll_msg = await interaction.channel.send(embed = emb, view = view)
        async with aiosqlite.connect("db/polls.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS polls (poll_id INTEGER, poll_title TEXT, poll_description TEXT, poll_author TEXT, poll_avatar TEXT, upvotes INTEGER, downvotes INTEGER, upvote_users TEXT, downvote_users TEXT)")
                await cursor.execute("INSERT INTO polls (poll_id, poll_title, poll_description, poll_author, poll_avatar, upvotes, downvotes, upvote_users, downvote_users) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (poll_msg.id, title, description, interaction.user.display_name, user_avatar, 0, 0, "[]", "[]"))
                await db.commit()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
