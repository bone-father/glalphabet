import discord
from discord.ext import commands
import func
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=['g!', 'G!'], help_command=None, intents=intents)

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

    help = discord.Embed(
        title = "glalphabet",
        description = "prefix is 'g!'",
        colour = embed_colour
    )

    commands = "g!user ?[@user/userid]\ng!server\ng!lb\ng!lb deez nuts"

    help.add_field(name="commands", value=commands)
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
    cursor.execute("SELECT `correct`, `incorrect`, `deez nuts` FROM users WHERE id = %s", (id,))
    correct, incorrect, deez_nuts = cursor.fetchone()
    db.close()

    correct_rate = func.truncate((correct / (correct + incorrect)) * 100)
    score = correct - incorrect

    leaderboard = func.sortUsers()
    index = [idx for idx, tup in enumerate(leaderboard) if (tup[0]) == str(id)][0] + 1

    leaderboard_deez_nuts = func.sortUsersDeezNuts()
    index_deez_nuts = [idx for idx, tup in enumerate(leaderboard_deez_nuts) if (tup[0]) == str(id)][0] + 1

    username = ctx.message.guild.get_member(int(id))
    user_colour = username.color
    user_pfp = username.avatar_url

    user = discord.Embed(
        title = username,
        colour = user_colour,
        description = "correct rate: **{correct_rate}%**\n total correct: **{correct}**\n total incorrect: **{incorrect}**\n score: **{score} (#{index})**\n deez nuts: **{deez_nuts} (#{index_deez_nuts})**".format
        (correct_rate=str(correct_rate), correct=str(correct), incorrect=str(incorrect), score=str(score), index=str(index), deez_nuts=str(deez_nuts), index_deez_nuts=str(index_deez_nuts))
    )

    user.set_thumbnail(url=user_pfp)

    await ctx.send(embed=user)


@bot.command()
async def server(ctx):

    db, cursor = func.connect()
    cursor.execute("SELECT current, `last counter id`, `high score` FROM server")
    current, last_counter_id, high_score = cursor.fetchone()
    db.close()

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
        description = "current letter: **{current}**\n last counted by: **{last_counter}**\n high score: **{high_score}**".format(current=current, last_counter=last_counter, high_score=high_score)
    )

    server.set_thumbnail(url=server_icon)

    await ctx.send(embed=server)


@bot.command()
async def lb(ctx, *nuts):

    if ''.join(nuts) == "deeznuts":
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


bot.run(TOKEN)