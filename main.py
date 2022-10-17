import discord
from discord.ext import commands
import func
import os
from dotenv import load_dotenv
import datetime
import random
import time

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=['g!', 'G!'], help_command=None, intents=intents, case_insensitive=True, strip_after_prefix=True)

embed_colour = discord.Colour.from_rgb(255, 120, 30)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    channel_id = "1012447966612697188"

    if str(message.channel.id) == channel_id:

        count = message.content.split()[0]

        if func.isValidCount(count):

            db, cursor = func.connect()
            cursor.execute("SELECT current, `last counter id`, `high score`, `past high score` FROM server")
            current, last_counter_id, high_score, past_high_score = cursor.fetchone()

            if count == func.nextLetter(current) and str(message.author.id) != last_counter_id:

                if past_high_score == "false":
                    await message.add_reaction('✅')
                elif past_high_score == "true":
                    await message.add_reaction('☑️')
                    cursor.execute("UPDATE server SET `high score` = %s", (count,))        

                if func.containDeezNuts(message.content):
                    deez_nuts = True
                else:
                    deez_nuts = False  

                cursor.execute("UPDATE server SET current = %s, `last counter id` = %s", (count, message.author.id))

                if count == high_score:
                    cursor.execute("UPDATE server SET `past high score` = %s", ("true",))
                    
                db.commit()
                db.close()

                func.updateScore(message.author.id, "correct", deez_nuts)

            elif current == "":
                
                await message.add_reaction('⚠️')
                await message.channel.send("wrong")

            else:

                db, cursor = func.connect()
                cursor.execute("SELECT save FROM users WHERE id = %s", (str(message.author.id),))
                save = cursor.fetchone()[0]

                if save == 1:

                    await message.add_reaction('⚠️')
                    await message.channel.send("wrong dumbass your save has been used")
                    cursor.execute("UPDATE users SET save = 0 WHERE id = %s", (str(message.author.id),))
                    db.commit()
                    db.close()
                    
                else:

                    await message.add_reaction('❌')
                    cursor.execute("UPDATE server SET current = %s, `last counter id` = %s, `past high score` = %s", ("", "", "false"))
                    db.commit()
                    db.close()

                    if str(message.author.id) == last_counter_id:
                        await message.channel.send("<@{id}> RUINED IT at **{current}**!!!!! DONT COUNT TWICE IN A ROW".format(id=message.author.id, current=current))
                    elif count != func.nextLetter(current):
                        await message.channel.send("<@{id}> RUINED IT at **{current}**!!!!! WRONG LETTER!!!!! dumbass".format(id=message.author.id, current=current))

                func.updateScore(message.author.id, "incorrect", False)
            
    await bot.process_commands(message)


@bot.command()
async def help(ctx):

    commands = "**g!user [@user/userid]** - get user stats\n**g!server** - get server stats\n**g!lb [deez nuts]** - display leaderboard\n**g!ub** - math question to earn saves"

    help = discord.Embed(
        title = "glalphabet",
        description = "prefix is 'g!'\n\n" + commands,
        colour = embed_colour
    )

    help.set_footer(text="glamont")
    help.set_image(url="https://media.discordapp.net/attachments/922414067761709077/1027651348935753819/glamont_uwu.gif")

    await ctx.send(embed=help)


@bot.command()
async def user(ctx, *user):

    if len(user) > 0:
        id = user[0].strip('<@>')
    else:
        id = ctx.author.id

    db, cursor = func.connect()
    cursor.execute("SELECT correct, incorrect, `deez nuts`, save FROM users WHERE id = %s", (id,))
    correct, incorrect, deez_nuts, save = cursor.fetchone()
    db.close()

    correct_rate = func.truncate((correct / (correct + incorrect)) * 100)
    score = correct - incorrect

    leaderboard = func.sortUsers()
    index = [idx for idx, tup in enumerate(leaderboard) if (tup[0]) == str(id)][0] + 1

    if deez_nuts > 0:
        leaderboard_deez_nuts = func.sortUsersDeezNuts()
        index_deez_nuts = [idx for idx, tup in enumerate(leaderboard_deez_nuts) if (tup[0]) == str(id)][0] + 1
        description = "correct rate: **{correct_rate}%**\ntotal correct: **{correct}**\ntotal incorrect: **{incorrect}**\nscore: **{score} (#{index})**\ndeez nuts: **{deez_nuts} (#{index_deez_nuts})**\nsaves: **{save}/1**".format(
                        correct_rate=str(correct_rate), correct=str(correct), incorrect=str(incorrect), score=str(score), index=str(index), deez_nuts=str(deez_nuts), index_deez_nuts=str(index_deez_nuts), save=str(save).rstrip("0").rstrip("."))
    else:
        description = "correct rate: **{correct_rate}%**\ntotal correct: **{correct}**\ntotal incorrect: **{incorrect}**\nscore: **{score} (#{index})**\nsaves: **{save}/1**".format(
                        correct_rate=str(correct_rate), correct=str(correct), incorrect=str(incorrect), score=str(score), index=str(index), save=str(save).rstrip("0").rstrip("."))

    username = ctx.message.guild.get_member(int(id))
    user_colour = username.color
    user_pfp = username.avatar

    user = discord.Embed(
        title = username,
        colour = user_colour,
        description = description
    )

    user.set_thumbnail(url=user_pfp)

    await ctx.send(embed=user)


@bot.command()
async def server(ctx):

    db, cursor = func.connect()
    cursor.execute("SELECT current, `last counter id`, `high score` FROM server")
    current, last_counter_id, high_score = cursor.fetchone()
    db.close()

    server_icon = ctx.guild.icon

    if current == "":
        current = "none"
    
    if last_counter_id == "":
        last_counter = "none"
    else:
        last_counter = '<@'+last_counter_id+'>'

    server = discord.Embed(
        title = "glamont",
        colour = embed_colour,
        description = "current letter: **{current}**\n last counted by: **{last_counter}**\n high score: **{high_score}**".format(
                      current=current, last_counter=last_counter, high_score=high_score)
    )

    server.set_thumbnail(url=server_icon)

    await ctx.send(embed=server)


@bot.command()
async def lb(ctx, *nuts):

    if ''.join(nuts).lower() == "deeznuts":
        leaderboard = func.sortUsersDeezNuts()
        title = "deez nuts"

    else:
        leaderboard = func.sortUsers()
        title = "glamont leaderboard"

    description = ""

    for i in range(len(leaderboard)):
        user = leaderboard[i]
        username = await bot.fetch_user(user[0])
        description += '**#' + str(i+1) + '** ' + str(username) + ', **' + str(user[1]) + '**\n'

    leaderboard = discord.Embed(
        title = title,
        colour = embed_colour,
        description = description
    )

    await ctx.send(embed=leaderboard)


@bot.command()
async def ub(ctx):

    db, cursor = func.connect()
    cursor.execute("SELECT time, `in progress` FROM users WHERE id = %s", (str(ctx.message.author.id),))
    last_time, in_progress = cursor.fetchone()
    db.close()

    if in_progress != "true":
        db, cursor = func.connect()
        cursor.execute("UPDATE users SET `in progress` = %s WHERE id = %s", ("true", str(ctx.message.author.id)))
        db.commit()
        
        cursor.execute("SELECT save FROM users WHERE id = %s", (str(ctx.message.author.id),))
        save = cursor.fetchone()[0]
        db.close()

        if last_time == "":
            twelve_hours = True
        else:
            twelve_hours = (func.timeDifference(last_time, str(datetime.datetime.now())) / 60 >= 12)

        equation, answer = func.generateEquation()
        options = [str(answer)]

        for i in range(3):
            while(True):
                incorrect = random.randint(answer - 10, answer + 10)
                if str(incorrect) not in options:
                    options.append(str(incorrect))
                    break

        random.shuffle(options)

        class Menu(discord.ui.View):
            def __init__(self, ctx):
                super().__init__(timeout=None)
                self.ctx = ctx
                self.clicked = False
                self.interacted = False

            @discord.ui.button(label=options[0], style=discord.ButtonStyle.blurple)
            async def button_callback_1(self, interaction, button):
                self.clicked = True
                
                for option in self.children:
                    option.disabled = True

                    if option.label == str(answer):
                        option.style = discord.ButtonStyle.green

                if button.label != str(answer):
                    button.style = discord.ButtonStyle.red

                if interaction.user != self.ctx.message.author:
                    await interaction.response.send_message(content="fuck off this isn't for you", ephemeral=True)
                else:
                    await interaction.response.edit_message(view=self)

                    if button.label == str(answer):
                        
                        db, cursor = func.connect()
                        cursor.execute("UPDATE users SET math = math + 1 WHERE id = %s", (str(interaction.user.id),))

                        if twelve_hours and save != 1:
                            cursor.execute("UPDATE users SET save = save + 0.5, time = %s WHERE id = %s", (str(datetime.datetime.now()), str(interaction.user.id)))
                            message = "nice. 0.5 saves earned ({save}/1 in total)".format(save=str(save + 0.5).rstrip("0").rstrip("."))

                        else:
                            message = "nice yeah"

                        db.commit()
                        db.close()

                        await self.ctx.send(message)
                        
                    else:

                        if twelve_hours:
                            db, cursor = func.connect()
                            cursor.execute("UPDATE users SET time = %s WHERE id = %s", (str(datetime.datetime.now()), str(interaction.user.id)))
                            db.commit()
                            db.close()

                        await self.ctx.send("wrong lmfao everybody laugh at <@{id}> this fucking idiot".format(id=interaction.user.id))

                    self.interacted = True

            @discord.ui.button(label=options[1], style=discord.ButtonStyle.blurple)
            async def button_callback_2(self, interaction, button):
                self.clicked = True
                
                for option in self.children:
                    option.disabled = True

                    if option.label == str(answer):
                        option.style = discord.ButtonStyle.green

                if button.label != str(answer):
                    button.style = discord.ButtonStyle.red

                if interaction.user != self.ctx.message.author:
                    await interaction.response.send_message(content="fuck off this isn't for you", ephemeral=True)
                else:
                    await interaction.response.edit_message(view=self)

                    if button.label == str(answer):
                        
                        db, cursor = func.connect()
                        cursor.execute("UPDATE users SET math = math + 1 WHERE id = %s", (str(interaction.user.id),))

                        if twelve_hours and save != 1:
                            cursor.execute("UPDATE users SET save = save + 0.5, time = %s WHERE id = %s", (str(datetime.datetime.now()), str(interaction.user.id)))
                            message = "nice. 0.5 saves earned ({save}/1 in total)".format(save=str(save + 0.5).rstrip("0").rstrip("."))

                        else:
                            message = "nice yeah"

                        db.commit()
                        db.close()

                        await self.ctx.send(message)
                        
                    else:

                        if twelve_hours:
                            db, cursor = func.connect()
                            cursor.execute("UPDATE users SET time = %s WHERE id = %s", (str(datetime.datetime.now()), str(interaction.user.id)))
                            db.commit()
                            db.close()

                        await self.ctx.send("wrong lmfao everybody laugh at <@{id}> this fucking idiot".format(id=interaction.user.id))

                    self.interacted = True

            @discord.ui.button(label=options[2], style=discord.ButtonStyle.blurple)
            async def button_callback_3(self, interaction, button):
                self.clicked = True
                
                for option in self.children:
                    option.disabled = True

                    if option.label == str(answer):
                        option.style = discord.ButtonStyle.green

                if button.label != str(answer):
                    button.style = discord.ButtonStyle.red

                if interaction.user != self.ctx.message.author:
                    await interaction.response.send_message(content="fuck off this isn't for you", ephemeral=True)
                else:
                    await interaction.response.edit_message(view=self)

                    if button.label == str(answer):
                        
                        db, cursor = func.connect()
                        cursor.execute("UPDATE users SET math = math + 1 WHERE id = %s", (str(interaction.user.id),))

                        if twelve_hours and save != 1:
                            cursor.execute("UPDATE users SET save = save + 0.5, time = %s WHERE id = %s", (str(datetime.datetime.now()), str(interaction.user.id)))
                            message = "nice. 0.5 saves earned ({save}/1 in total)".format(save=str(save + 0.5).rstrip("0").rstrip("."))

                        else:
                            message = "nice yeah"

                        db.commit()
                        db.close()

                        await self.ctx.send(message)
                        
                    else:

                        if twelve_hours:
                            db, cursor = func.connect()
                            cursor.execute("UPDATE users SET time = %s WHERE id = %s", (str(datetime.datetime.now()), str(interaction.user.id)))
                            db.commit()
                            db.close()

                        await self.ctx.send("wrong lmfao everybody laugh at <@{id}> this fucking idiot".format(id=interaction.user.id))

                    self.interacted = True
                
            @discord.ui.button(label=options[3], style=discord.ButtonStyle.blurple)
            async def button_callback_4(self, interaction, button):
                self.clicked = True
                
                for option in self.children:
                    option.disabled = True

                    if option.label == str(answer):
                        option.style = discord.ButtonStyle.green

                if button.label != str(answer):
                    button.style = discord.ButtonStyle.red

                if interaction.user != self.ctx.message.author:
                    await interaction.response.send_message(content="fuck off this isn't for you", ephemeral=True)
                else:
                    await interaction.response.edit_message(view=self)

                    if button.label == str(answer):
                        
                        db, cursor = func.connect()
                        cursor.execute("UPDATE users SET math = math + 1 WHERE id = %s", (str(interaction.user.id),))

                        if twelve_hours and save != 1:
                            cursor.execute("UPDATE users SET save = save + 0.5, time = %s WHERE id = %s", (str(datetime.datetime.now()), str(interaction.user.id)))
                            message = "nice. 0.5 saves earned ({save}/1 in total)".format(save=str(save + 0.5).rstrip("0").rstrip("."))

                        else:
                            message = "nice yeah"

                        db.commit()
                        db.close()

                        await self.ctx.send(message)
                        
                    else:

                        if twelve_hours:
                            db, cursor = func.connect()
                            cursor.execute("UPDATE users SET time = %s WHERE id = %s", (str(datetime.datetime.now()), str(interaction.user.id)))
                            db.commit()
                            db.close()

                        await self.ctx.send("wrong lmfao everybody laugh at <@{id}> this fucking idiot".format(id=interaction.user.id))

                    self.interacted = True

        view = Menu(ctx)
        question = func.countdown(5, equation, twelve_hours, last_time, save)

        view.message = await ctx.send(embed=question, view=view)

        for i in range(5, 0, -1):

            time.sleep(1)
            await view.message.edit(embed=func.countdown(i-1, equation, twelve_hours, last_time, save))

            if view.clicked:
                break
            
            if i == 1 and view.clicked == False:

                    for option in view.children:
                        option.disabled = True

                        if option.label == str(answer):
                            option.style = discord.ButtonStyle.green

                    if view.clicked == False:
                        await view.message.edit(view=view)

        if view.clicked == False:

            if twelve_hours:
                db, cursor = func.connect()
                cursor.execute("UPDATE users SET time = %s WHERE id = %s", (str(datetime.datetime.now()), str(ctx.message.author.id)))
                db.commit()
                db.close()

            await view.ctx.send("too slow. answer was {answer}".format(answer=str(answer)))

        db, cursor = func.connect()
        cursor.execute("UPDATE users SET `in progress` = %s WHERE id = %s", ("false", str(ctx.message.author.id)))
        db.commit()
        db.close()

    else:

        await ctx.send("game in progress already shut the fuck up")


bot.run(TOKEN)