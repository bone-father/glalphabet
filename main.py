import discord
from discord.ext import commands
import func
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='g!', help_command=None, intents=intents)

embed_colour = discord.Colour.from_rgb(255, 120, 30)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    db, mycursor = func.connect()
    mycursor.execute("SELECT `channel id` FROM server")
    channel_id = str(mycursor.fetchone())[2:-3]

    count = message.content.split()[0]

    if func.isValidCount(count) and str(message.channel.id) == channel_id:

        db, mycursor = func.connect()
        mycursor.execute("SELECT current, `last counter id`, `high score`, `past high score` FROM server")
        current, last_counter_id, high_score, past_high_score = mycursor.fetchone()

        if count == func.nextLetter(current) and str(message.author.id) != last_counter_id:

            if past_high_score == "false":
                await message.add_reaction('✅')
            elif past_high_score == "true":
                await message.add_reaction('☑️')
                mycursor.execute("UPDATE server SET `high score` = %s", (count,))
                db.commit()          

            mycursor.execute("UPDATE server SET current = %s, `last counter id` = %s", (count, message.author.id))
            db.commit()

            if count == high_score:
                mycursor.execute("UPDATE server SET `past high score` = %s", ("true",))
                db.commit()        

            try:
                mycursor.execute("SELECT * FROM users WHERE id = %s", (message.author.id,))
                len(mycursor.fetchone())

                mycursor.execute("UPDATE users SET `correct` = `correct` + 1 WHERE id = %s", (message.author.id,))
                db.commit()
            except:
                mycursor.execute("INSERT INTO users (id, correct, incorrect) VALUES (%s, %s, %s)", (message.author.id, 1, 0))
                db.commit()

        elif (current == ""):
            await message.add_reaction('⚠️')
            await message.channel.send("wrong")

        else:

            await message.add_reaction('❌')
            mycursor.execute("UPDATE server SET current = %s, `last counter id` = %s, `past high score` = %s", ("", "", "false"))
            db.commit()

            if str(message.author.id) == last_counter_id:
                await message.channel.send("<@{id}> RUINED IT at **{current}**!!!!! DONT COUNT TWICE IN A ROW".format(id=message.author.id, current=current))
            elif count != func.nextLetter(current):
                await message.channel.send("<@{id}> RUINED IT at **{current}**!!!!! WRONG LETTER!!!!! dumbass".format(id=message.author.id, current=current))


            try:
                mycursor.execute("SELECT * FROM users WHERE id = %s", (message.author.id,))
                len(mycursor.fetchone())

                mycursor.execute("UPDATE users SET `incorrect` = `incorrect` + 1 WHERE id = %s", (message.author.id,))
                db.commit()
            except:
                mycursor.execute("INSERT INTO users (id, correct, incorrect) VALUES (%s, %s, %s)", (message.author.id, 0, 1))
                db.commit()

    await bot.process_commands(message)

@bot.command()
async def help(ctx):

    help = discord.Embed(
        title = "glalphabet uwu",
        description = "prefix is 'g!'",
        colour = embed_colour
    )

    commands = "g!user ?[@user/userId]\ng!server\ng!lb"

    help.add_field(name="commands", value=commands)
    help.set_footer(text="abcdefghijklmnopqrstuvwxyz")
    help.set_image(url="https://media.discordapp.net/attachments/815332398333689886/981968722564636763/glamont_uwu.gif")

    await ctx.send(embed=help)

@bot.command()
async def user(ctx, *user):

    if len(user) > 0:
        id = user[0].strip('<@>')
    else:
        id = ctx.author.id

    db, mycursor = func.connect()
    mycursor.execute("SELECT `correct`, `incorrect` FROM users WHERE id = %s", (id,))
    correct, incorrect = mycursor.fetchone()

    correct_rate = str(func.truncate((correct / (correct + incorrect)) * 100))
    score = str(correct - incorrect)
    username = ctx.message.guild.get_member(int(id))
    user_colour = username.color
    user_pfp = username.avatar_url

    user = discord.Embed(
        title = username,
        colour = user_colour,
        description = "correct rate: **{correct_rate}%**\n total correct: **{correct}**\n total incorrect: **{incorrect}**\n score: **{score}**".format(correct_rate=correct_rate, correct=str(correct), incorrect=str(incorrect), score=score)
    )

    user.set_thumbnail(url=user_pfp)

    await ctx.send(embed=user)

@bot.command()
async def server(ctx):

    db, mycursor = func.connect()
    mycursor.execute("SELECT current, `last counter id`, `high score` FROM server")
    current, last_counter_id, high_score = mycursor.fetchone()

    server_icon = ctx.guild.icon_url

    if current == "":
        current = "none"
    
    if last_counter_id == "":
        last_counter = "none"
    else:
        last_counter = '<@'+last_counter_id+'>'

    server = discord.Embed(
        title = "glamont",
        colour = embed_colour,
        description = "current number: **{current}**\n last counted by: **{last_counter}**\n high score: **{high_score}**".format(current=current, last_counter=last_counter, high_score=high_score)
    )

    server.set_thumbnail(url=server_icon)

    await ctx.send(embed=server)

@bot.command()
async def lb(ctx):

    leaderboard = []

    db, mycursor = func.connect()
    mycursor.execute("SELECT * FROM users")

    for row in mycursor:
        username = await bot.fetch_user(row[0])
        leaderboard.append((username, row[1]-row[2]))

    leaderboard.sort(key=lambda user: user[1], reverse=True)

    description = ""

    for i in range(len(leaderboard)):
        user = leaderboard[i]
        description += '**#' + str(i+1) + '** ' + str(user[0]) + ', **' + str(user[1]) + '**\n'

    leaderboard = discord.Embed(
        title = "glamont leaderboard",
        colour = embed_colour,
        description = description
    )

    await ctx.send(embed=leaderboard)

bot.run(TOKEN)