# TELEGRAM BOT WITH SCHEDULE FOR FERI, UNIVERSITY OF MARIBOR
# THIS SCRIPT WORKS WITH SQL DATABASE
# YOU MAY USE IT WITHOUT MODIFICATION IF YOU CHANGE DATABASE DATA

# LIBRARIES 'requests' AND 'mysql-connector' NEEDED TO BE INSTALLED
import mysql.connector
import requests
import re
import datetime
#from enum import Enum


class BotHandler:

    # CONSTRUCTOR CREATES OBJECT WITH API TOKEN
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    # GETS ALL UNREAD MESSAGES
    def get_updates(self, offset):
        method = 'getUpdates'
        parameters = {'timeout': 30, 'offset': offset}
        response = requests.get(self.api_url + method, parameters)
        return response.json()['result']

    # GETS CHAT ID
    def get_chat_id(self, data):
        response = data['message']['chat']['id']
        return response

    # SEND MESSAGE 'text' TO CHAT 'chat_id'
    def send_message(self, chat_id, text):
        parameters = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        response = requests.post(self.api_url + method, parameters)
        return response

    # GETS 'update_id' OF LAST MESSAGE
    def get_last_update_id(self, data):
        return data[-1]['update_id']


# HANDLES SQL OPERATIONS
class SQL_Handler():

    # NEW CONNECTION
    def __init__(self):
        self.database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="schedule"
        )
        self.mycursor = self.database.cursor()

    # CHECK IF DATABASE WITH NAME 'name' EXISTS
    def check_if_exists(self, name):
        self.mycursor.execute("SHOW TABLES LIKE '" + name + "'")
        result = self.mycursor.fetchall()
        if len(result) == 0:
            return 0
        else:
            return 1

    # READS VALUES FROM DATABASE
    def read_from_base(self, name):
        self.mycursor.execute("SELECT * FROM " + name)
        result = self.mycursor.fetchall()
        return result

    # CLOSES CONNECTION TO DATABASE
    '''def close_connecion(self):
        self.database.shutdown()'''
    

# GETS USER INPUT AS A PARAMETER AND CHECK IF IT'S DATE OR NOT
# IF YES RETURN DATE IN FORMAT YYYYMMDD (AS STORED IN .ics CALENDAR)
# IF NO RETURN 0
def recognize_date(date):
    now = datetime.datetime.now()
    if date in ["t", "T", "td", "Td", "today", "Today", "/t"]:  # TODAY
        return now.strftime("d%Y%m%d")
    elif date in ["tomorrow", "tm", "Tomorrow", "Tomorow", "tomorow", "Tm", "tommorow", "/tm"]:  # TOMORROW
        date_rt = now + datetime.timedelta(days=1)
        return date_rt.strftime("d%Y%m%d")
    elif re.match("^([0-9]{2}[.|\/]*){2}[0-9]{4}$", date):   # FOR EXACT DATE
        find = re.search("([0-9]{2}[.|\/]*){2}[0-9]{4}", date).group()      # INPUT IN FORMAT DD.MM.YYYY OR DD/MM/YYYY
        find = find.replace("/", "")                                       # OR DDMMYYYY
        find = find.replace(".", "")
        tmp_day = find[0:2]
        tmp_month = find[2:4]
        find = find[4:8] + tmp_month + tmp_day
        return "d" + find
    elif re.match("^[0-9]{2}[.|\/]*[0-9]{2}$", date):   # FOR EXACT DATE
        find = date                                     # INPUT IN FORMAT DDMM OR DD/MM OR DD.MM
        find = find.replace("/", "")
        find = find.replace(".", "")
        tmp = find[0:2]
        find = now.strftime("%Y") + find[2:4] + tmp
        return "d" + find
    elif re.match("^[0-9]{2}$", date):                  # FOR EXACT DATE IN CURRENT MONTH
        return "d" + now.strftime("%Y") + now.strftime("%m") + date  # INPUT IN FORMAT DD
    else:
        return 0


# MAIN FUNCTION
# PROCESSING UPDATES AND GIVES RESPONSE
def main():
    SBot = BotHandler('723994825:AAHwsrRH0Q_6pJ36KA8PtYCk6yf4bQT3KxE')  # CREATE OBJECT WITH DEFINED TELEGRAM API TOKEN
    database = SQL_Handler()
    offset = None  # INITIAL OFFSET

    # INFINITE LOOP
    # (1) GET UPDATE, IF NOT EMPTY SET NEW OFFSET
    # (2) FOR EVERY OBJECT IN UPDATE,
    # READ TEXT AND SEND RESPONSE
    while True:
        now = datetime.datetime.now()
        time = now.strftime("%d") + '/' + now.strftime("%m") + '/' + now.strftime("%y") + '\n' + now.strftime("%H") + ':' + now.strftime("%M")

        # (1)
        update = SBot.get_updates(offset)
        if len(update) > 0:
            offset = SBot.get_last_update_id(update) + 1

        # (2)
        for i in range(0, len(update)):
            update_text = update[i]['message']['text']
            chat_id = update[i]['message']['chat']['id']
            # CHECK IF IT'S DATE
            if recognize_date(update_text) != 0:
                # IF YES CHECK IF TABLE FOR THIS DATE EXISTS
                if database.check_if_exists(recognize_date(update_text)):
                    # IF YES START FORMING RESPONSE
                    schedule = database.read_from_base(recognize_date(update_text))
                    response = "--------------------------------- \n"
                    # FOR EVERY ELEMENT
                    for i in range(len(schedule)):
                        response += schedule[i][0] + "\n"  # CLASS NAME
                        response += schedule[i][1] + ":00 - "  # STARTING HOUR
                        response += schedule[i][2] + ":00\n"  # ENDING HOUR
                        response += schedule[i][3] + "\n--------------------------------- \n"  # LOCATION
                    SBot.send_message(chat_id, response)  # SEND RESPONSE
                else:
                    SBot.send_message(chat_id, "Looks like there's no classes!")  # TABLE NOT FOUND
            else:
                SBot.send_message(chat_id, "Wrong input.")  # NOT DATE


# RUN UNTIL INTERRUPTED BY USER
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
