from os.path import expanduser
import sqlite3
import json
from textblob import TextBlob
import unidecode


# WIP  working on fixing errors when the user is not found in contacts
# ALSO unkown if the file path is standard for everyone to contacts



def get_connection():
    db_path = expanduser('~') + '/Library/Messages/chat.db'
    return sqlite3.connect(db_path)


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


def get_sent(id):
    messages = get_messages(id)
    message = []
    for i in range(len(messages)):
        # stringify messages and unidecode (dont know if textblob does it)
        sentence = str(messages[i])
        sentence = unidecode.unidecode(sentence)
        sentence = TextBlob(sentence)
        polarity = sentence.sentiment.polarity
        subjectivity = sentence.sentiment.subjectivity
        # this changes polairty away from int to str - not used here
        if polarity > 0.0:
            pol_value = 'Positive'
        elif polarity == 0.0:
            pol_value = 'Neutral'
        else:
            pol_value = 'Negative'

        sent_analysis = {
            'Polarity': polarity,
            'Pol_Value': pol_value,
            'subjectivity': subjectivity,
            'Sentence': unidecode.unidecode(str(messages[i]))
        }
        message.append(sent_analysis)
    return message


# gets the contacts name from address book DB
# not sure if this is standard across all macs
def contacts_connect(id):
    ad_path = expanduser('~') + '/Library/Application Support/AddressBook/Sources/FD5AD280-0D87-48AA-8C07-DE12FAF9A4D1/AddressBook-v22.abcddb'
    connection = sqlite3.connect(ad_path)
    c = connection.cursor()
    c.execute("SELECT * FROM `ZABCDCONTACTINDEX`")
    contacts = []
    for row in c:
        person = {
            'index': row[0],
            'zContact': row[3],
            'info': row[5],
        }
        contacts.append(person)
    # fix error here - if user not found in contacts it prints an error
    users = get_users()
    for i in range(len(users)):
        if users[i]['ID'] == id:
            person = users[i]['Contact']
    for i in range(len(contacts)):
        number = str(person).replace('+1', '')
        find_num = contacts[i]['info'].find(number)
        if find_num > -1:
            contact = contacts[i]['info']

    return contact


def get_user_sent(id):
    message = get_sent(id)
    person = contacts_connect(id)
    # get message polarity
    polarity = []
    for i in range(len(message)):
        pol = message[i]['Polarity']
        polarity.append(pol)
    # get average
    pol_sum = sum(polarity)
    n = len(polarity)
    if n == 0:
        print(person + ' has no messages saved')
        average_polarity = 'none'
    else:
        average_polarity = pol_sum / n
        print(person + 'Has an average polairty of %s' % average_polarity)


get_user_sent(1)
