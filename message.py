from os.path import expanduser
import sqlite3
import json


# to use, change get_words(val_here) with either an id(get_users) or just 'all'


# connect to sql
def get_connection():
    db_path = expanduser("~") + '/Library/Messages/chat.db'
    return sqlite3.connect(db_path)


# get specif users by id - need to know their phone/email
def get_users():
    connection = get_connection()
    c = connection.cursor()
    
    c.execute("SELECT * FROM `handle`")
    recipients = []
    for row in c:
        user = {
            'ID': row[0],
            'Contact': row[1],
        }
        recipients.append(user)
    
    connection.close()
    return recipients


# get message for either 'all' or just id
def get_messages(id):
    connection = get_connection()
    c = connection.cursor()
    if id == 'all':
        c.execute("SELECT * FROM `message`")
        messages = []
        for row in c:
            text = row[2]
            messages.append(text)
    else:
        c.execute("SELECT * FROM `message` WHERE handle_id=" + str(id))
        messages = []
        for row in c:
            text = row[2]
            messages.append(text)

    connection.close()
    return messages


def word_count(id):
    # terrible code right here, should learn reGex
    messages = str(get_messages(id)).replace('[', '').replace(']', '').lower()
    messages = messages.replace(',', '').replace('"', '').replace("'", '')
    messages = messages.replace('?', '').replace('.', '').replace('!', '')
    words = messages.split()
    word_list = []
    final_list = []

    # could do this better, very slow code - could just remove the indexing
    for i in words:
        if i not in word_list:
            word_list.append(i)

    for i in range(0, len(word_list)):
        new_word = {
            'Word': word_list[i],
            'Count': words.count(word_list[i]),
        }
        final_list.append(new_word)

    return final_list


def get_words(id):
    user_id = id
    countlist = word_count(user_id)

    # sort the list
    sorted_list = []
    for i in range(len(countlist)):
        count = countlist[i]['Count']
        word = countlist[i]['Word']
        sorted_list.append((count, word))

    sorted_list.sort(reverse=True)

    # cant json dumps cause object is a set - cant seralize
    f = open('Output.txt', 'w')
    f.write(str(sorted_list))
    # write to file
    print(sorted_list)


get_words('all')
