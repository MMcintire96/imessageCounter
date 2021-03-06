import sqlite3
import os
from textblob import TextBlob
import argparse
import datetime
import cv2
import json

class Users(object):

    def __init__(self):
        self.all_users = self.get_user_ids()

    def get_connection(self):
        ''' Returns the connect cursor '''
        db_path = os.path.expanduser('~') + '/Library/Messages/chat.db'
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
        except sqlite3.OperationalError as e:
            print("DB not found - check db_path")
        return c

    def get_user_ids(self):
        ''' Gets a list of users and returns a dict containing id and num  '''
        c = self.get_connection()
        c.execute("SELECT * FROM handle")
        users = []
        for row in c.fetchall():
            user = {
                'id': row[0],
                'num': row[1],
            }
            yield user


class TargetUser(object):

    def __init__(self, number):
        self.number = number

    def convert_date(self, unix_time):
        ''' Converts the date to Mac Coco time '''
        unix_time = int(unix_time[0:9])
        mac_coca_time = 978307200
        unix_time = unix_time + mac_coca_time
        d = datetime.datetime.utcfromtimestamp(unix_time)
        return str(d)

    def get_messages(self):
        ''' Gets all the messages and time from the user '''
        users = Users().get_user_ids()
        c = Users().get_connection()
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
                'has_attch': row[34],
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
        user_msgs, my_msgs = self.get_messages()
        user_times = ([x['unix_date'] for x in user_msgs])
        my_times = ([x['unix_date'] for x in my_msgs])
        all_times = user_times + my_times
        print(json.dumps(user_times, indent=4), file=open('u.txt', 'w'))
        print(json.dumps(my_times, indent=4), file=open('m.txt', 'w'))
        if len(user_times) > len(my_times):
            r = len(my_times)
        else:
            r = len(user_times)
        times = []
        for t in range(r):
            try:
                time_slope = (user_times[0] - my_times[0]) / 60
                user_times.pop(0)
                my_times.pop(0)
                times.append(time_slope)
            except Exception as e:
                pass
        avg_time = sum(times)/len(times)
        t = self.convert_date(str(int(avg_time)))
        print(t)

    def avg_sentiment(self, **kwargs):
        '''Returns the averages of the users sentiment'''
        user_lst, me_lst = self.get_messages()
        user_pol, user_subj = 0, 0
        me_pol, me_subj = 0, 0
        for usr_item in user_lst:
            tb_data = TextBlob(str(usr_item['text']))
            user_pol += tb_data.sentiment.polarity
            user_subj += tb_data.sentiment.subjectivity
        for me_item in me_lst:
            tb_data = TextBlob(str(me_item['text']))
            me_pol += tb_data.sentiment.polarity
            me_subj += tb_data.sentiment.subjectivity
        usr_sent = {'polarity': user_pol/len(user_lst), 'subjectivity': user_subj/len(user_lst)}
        me_sent = {'polarity': me_pol/len(me_lst), 'subjectivity': me_subj/len(me_lst)}
        if len(kwargs) is not 0:
            if kwargs['contains'] == 'both':
                return usr_sent, me_sent
            elif kwargs['contains'] == 'me':
                return me_sent
            else:
                print("kwargs{contains} either 'me' or 'both'")
        else:
            return usr_sent

    def avg_attach(self, **kwargs):
        '''Returns the avg amount of attachments for either user/me or both'''
        user_lst, me_lst = self.get_messages()
        u_freq, m_freq = 0, 0
        for item in user_lst:
            u_freq += item['has_attch']
        for item in me_lst:
            m_freq += item['has_attch']
        if len(kwargs) is not 0:
            if contains == 'both':
                return u_freq/len(u_freq), m_freq/len(m_freq)
            elif contains == 'me':
                return m_freq/len(m_freq)
            else:
                print("kwargs{contains} either 'me' or 'both'")
        else:
            return u_freq/len(u_freq)

    def list_attach(self):
        '''Returns a list of the file names of attachments'''
        c = Users().get_connection()
        c.execute("SELECT * FROM attachment")
        file_lst = [x[4] for x in c.fetchall()]
        return file_lst


def show_attachments():
    '''Shows all your attachments in a cv2 window'''
    f_lst = user.list_attach()
    formats = ['jpeg', 'jpg', 'png']
    for f in f_lst:
        try:
            f = f.split('~')[1]
            print('File_name %s' %f)
            if f.split('.')[1].lower() in formats:
                f = os.path.expanduser('~') + f
                img = cv2.imread(f)
                cv2.imshow('output', img)
                # press any key to go next or q to quit
                if cv2.waitKey(0) & 0xFF == ord('q'):
                    break
            else:
                pass
        except Exception as e:
            print(str(e))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--number', type=str)
    args = parser.parse_args()
    try:
        if args.number == None:
            print('Enter a number with the --number <number> flag')
            print('Calling with "all"')
            num = 'all'
        else:
            num = args.number
    except Exception as e:
        pass


    user = TargetUser(num)
    usr_mess, me_mess = user.get_messages()
    print(json.dumps(usr_mess, indent=4), file=open('User_out.txt', 'w'))
    print(json.dumps(me_mess, indent=4), file=open('Me_out.txt', 'w'))
    usr_sent, me_sent = user.avg_sentiment(contains='both')
    print("Stats on the %s" %num)
    print(usr_sent)
    print("Stats on You: ")
    print(me_sent)
    print('\nSee the output files in this dir')
