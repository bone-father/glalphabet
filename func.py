import discord
import datetime
import random
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv('USER')
PASSWD = os.getenv('PASSWD')

def connect():

    db = mysql.connector.connect(
        host="us-cdbr-east-06.cleardb.net",
        user=USER,
        passwd=PASSWD,
        database="heroku_50de5be591848c5"
    )

    return(db, db.cursor())


def nextLetter(current):

    glalphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a']

    if current == '':
        return 'a'
    else:
        current_split = list(current)

        for i in range(len(current_split)-1, -1, -1):

            letter = current_split[i]

            next_index = glalphabet.index(letter)+1
            current_split[i] = glalphabet[next_index]

            if letter != 'Z':
                break

            if i == 0:
                current_split.insert(0, 'a')

        return ''.join(current_split)


def isValidCount(input):

    glalphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    is_valid_count = True

    for char in input:
        if char in glalphabet:
            pass
        else:
            is_valid_count = False
            break
    
    if input == "":
        is_valid_count = False

    return is_valid_count


def containDeezNuts(message):

    message = message.replace(" ", "").lower()

    if "eez" in message and "nuts" in message:
        return True
    elif "ees" in message and "nuts" in message:
        return True
    else:
        return False


def truncate(num):

    return int(num*1000)/1000


def sortUsers():
    
    leaderboard = []

    db, cursor = connect()
    cursor.execute("SELECT * FROM users")

    for row in cursor:
        leaderboard.append((row[0], row[1]-row[2]))

    db.close()
    leaderboard.sort(key=lambda user: user[1], reverse=True)
    
    return leaderboard


def sortUsersDeezNuts():
    
    leaderboard = []

    db, cursor = connect()
    cursor.execute("SELECT * FROM users")

    for row in cursor:
        if (row[3] > 0):
            leaderboard.append((row[0], row[3]))

    db.close()
    leaderboard.sort(key=lambda user: user[1], reverse=True)

    return leaderboard


def updateScore(id, column, deez_nuts):

    if column == "correct":
        correct = 1
        incorrect = 0

    elif column == "incorrect":
        correct = 0
        incorrect = 1
        
    if deez_nuts==True:
        deez_nuts = 1
    else:
        deez_nuts = 0

    db, cursor = connect()

    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        len(cursor.fetchone())

        cursor.execute("UPDATE users SET {column} = {column} + 1, `deez nuts` = `deez nuts` + %s WHERE id = %s".format(column=column), (deez_nuts, id))
    except:
        cursor.execute("INSERT INTO users (id, correct, incorrect, `deez nuts`) VALUES (%s, %s, %s, %s)", (id, correct, incorrect, deez_nuts))

    db.commit()
    db.close()


def completeEquation(num):

    operators = ['+', '-', '*', '/']
    primes = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    if num in primes:

        if num == 1:
            op = random.choice(operators[:2:])
        else:
            op = random.choice(operators[:3:])
            
        if op == '*':
            next_num = random.randint(2, 10)
        else:
            next_num = random.randint(1, 10)

    else:

        op = random.choice(operators)
        if op == '/':
            while(True):
                next_num = random.randint(2, 10)
                if num % next_num == 0 and num != next_num:
                    break
        elif op == '*':
            next_num = random.randint(2, 10)
        else:
            next_num = random.randint(1, 10)

    return op, next_num


def generateEquation():

    operators = ['+', '-', '*', '/']

    num_1 = random.randint(1, 10)

    op_1, num_2 = completeEquation(num_1)

    if op_1 in operators[2:4]:
        
        op_2, num_3 = completeEquation(eval(str(num_1)+op_1+str(num_2)))

    else:

        op_2, num_3 = completeEquation(num_2)

    equation = (str(num_1) + ' ' + op_1 + ' ' + str(num_2) + ' ' + op_2 + ' ' + str(num_3) + ' = ?').replace('*', '×').replace('/', '÷')
    answer = int(eval(str(num_1)+op_1+str(num_2)+op_2+str(num_3)))

    return equation, answer


def timeDifference(time1, time2):

    time1 = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S.%f")
    time2 = datetime.datetime.strptime(time2, "%Y-%m-%d %H:%M:%S.%f")

    diff = time2 - time1

    return (diff.days * 1440) + (diff.seconds / 60)


def countdown(time, equation, twelve_hours, last_time, save):

    if time == 1:
        unit = "second"
    else:
        unit = "seconds"

    if save == 1:
        description = "you currently have 1/1 saves. no saves will be earned this round.\n\n**" + equation + "**\n\nyou have {time} {unit} left...".format(
                      time=str(time), unit=unit)
    elif twelve_hours == False:
        diff = timeDifference(str(datetime.datetime.now()), str(datetime.datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S.%f")+datetime.timedelta(hours=12)))
        hours = int(round(diff) / 60)
        minutes = round(diff) % 60
        description = "you've played in the last 12 hours. {hours} hr {minutes} min until saves can be earned again\n\n**".format(
                      hours=str(hours), minutes=str(minutes)) + equation + "**\n\nyou have {time} {unit} left...".format(time=str(time), unit=unit)
    else:
        description = "1 correct answer = 0.5 saves. you currently have {save}/1\n\n**".format(
                      save=str(save).rstrip("0").rstrip(".")) + equation + "**\n\nyou have {time} {unit} left...".format(time=str(time), unit=unit)

    embed = discord.Embed(title="math time!!!", description=description, colour=discord.Colour.from_rgb(111, 120, 219))
    embed.set_footer(text="gub")

    return embed