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

            if (letter != 'Z'):
                break

            if (i == 0):
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
    if "ees" in message and "nuts" in message:
        return True
    else:
        return False


import mysql.connector
def connect():

    db = mysql.connector.connect(
        host="us-cdbr-east-06.cleardb.net",
        user="b98c3bc0e5dcec",
        passwd="b2fc02c7",
        database="heroku_35067e70ff92b61"
    )

    return(db, db.cursor())


def truncate(num):

    return int(num*1000)/1000


def sortUsers():
    
    leaderboard = []

    db, mycursor = connect()
    mycursor.execute("SELECT * FROM users")

    for row in mycursor:
        leaderboard.append((row[0], row[1]-row[2]))

    leaderboard.sort(key=lambda user: user[1], reverse=True)
    
    return leaderboard


def sortUsersDeezNuts():
    
    leaderboard = []

    db, mycursor = connect()
    mycursor.execute("SELECT * FROM users")

    for row in mycursor:
        if (row[3] > 0):
            leaderboard.append((row[0], row[3]))

    leaderboard.sort(key=lambda user: user[1], reverse=True)

    return leaderboard


def updateScore(id, column, deez_nuts):

    if (column == "correct"):
        correct = 1
        incorrect = 0

    elif (column == "incorrect"):
        correct = 0
        incorrect = 1
        
    if deez_nuts==True:
        deez_nuts = 1
    else:
        deez_nuts = 0

    db, mycursor = connect()

    try:
        mycursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        len(mycursor.fetchone())

        mycursor.execute("UPDATE users SET `{column}` = `{column}` + 1, `deez nuts` = `deez nuts` + %s WHERE id = %s".format(column=column), (deez_nuts, id))
    except:
        mycursor.execute("INSERT INTO users (id, correct, incorrect, `deez nuts`) VALUES (%s, %s, %s, %s)", (id, correct, incorrect, deez_nuts))

    db.commit()