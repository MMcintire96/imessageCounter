import sqlite3
import os
from textblob import TextBlob
import argparse
import datetime

# move to another file
def get_connection():
    ''' Returns the connect cursor '''
    db_path = os.path.expanduser('~') + '/Library/Messages/chat.db'
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        return c
    except Exception as e:
        print(str(e))


def get_user_ids():
    ''' Gets a list of users and returns a dict containing id and num  '''
    c = get_connection()
    c.execute("SELECT * FROM handle")
    users = []
    for row in c.fetchall():
        user = {
            'id': row[0],
            'num': row[1],
        }
        users.append(user)
    return users


class TargetUser:

    def __init__(self, number):
        self.number = number
        self.messages, self.my_responses = self.get_messages()
        self.sentiment = self.user_sentiment()
        self.my_sentiment = self.my_sentiment()


    def convert_date(self, unix_time):
        ''' Converts the date to Mac Coco time '''
        unix_time = int(unix_time[0:9])
        mac_coca_time = 978307200
        unix_time = unix_time + mac_coca_time
        d = datetime.datetime.utcfromtimestamp(unix_time)
        return str(d)

    def get_messages(self):
        ''' Gets all the messages and time from the user '''
        users = get_user_ids()
        c = get_connection()
        if self.number != 'all':
            for item in users:
                if item['num'] == self.number:
                    user_id = item['id']
                    break
            c.execute("SELECT * FROM message WHERE handle_id=?", (str(user_id),))
        else:
            c.execute("SELECT * FROM message")
        user_messages = []
        me_messages = []
        for row in c.fetchall():
            data = {
                'text': row[2],
                'readable_date': self.convert_date(str(row[15])),
                'unix_date': row[15],
                'is_from_me': row[21],
            }
            if data['is_from_me'] == 1:
                me_messages.append(data)
            else:
                user_messages.append(data)
        return user_messages, me_messages

    # average response time is sum(their_time - my_time) = my_time
    # this needs to be invertable f(me) = sum(user_time - my_time)
    # f^-1(me) = sum(my_time - user_time)
    # TODO fix this - there is a difference in freq of responses
    # TODO convert time int readable after the average
    ''' what if we take the derivative as lim x-> 0 '''
    def text_time(self):
        user_msgs = self.messages
        my_msgs = self.my_responses
        user_times = ([x['unix_date'] for x in user_msgs])
        my_times = ([x['unix_date'] for x in my_msgs])
        all_times = user_times + my_times
        user_minus_my = 0
        print(len(user_times))
        print(len(my_times))
        for t in all_times:
            try:
                user_minus_my += user_times[0] - my_times[0]
                user_times.pop(0)
                my_times.pop(0)
            except Exception as e:
                pass
        print(user_minus_my)

    def user_sentiment(self):
        '''Returns the averages of the users sentiment'''
        user_pol, user_subj = 0, 0
        for usr_item in self.messages:
            tb_data = TextBlob(usr_item['text'])
            user_pol += tb_data.sentiment.polarity
            user_subj += tb_data.sentiment.subjectivity
        return {'polarity': user_pol/len(self.messages), 'subjectivity': user_subj/len(self.messages)}

    def my_sentiment(self):
        '''Returns the averages of the my sentiment'''
        my_pol, my_subj = 0, 0
        for my_item in self.my_responses:
            tb_data = TextBlob(my_item['text'])
            my_pol += tb_data.sentiment.polarity
            my_subj += tb_data.sentiment.subjectivity
        return {'polarity': my_pol/len(self.my_responses), 'subjectivity': my_subj/len(self.my_responses)}


parser = argparse.ArgumentParser()
parser.add_argument('--number', type=str)
args = parser.parse_args()
try:
    if args.number == None:
        print('Enter a number with the --number <number> flag')
    else:
        num = args.number
        user = TargetUser(num)
        print(user.sentiment)
except Exception as e:
    pass





