"""This script runs Telegram bot """

#Libraries 'dateparser' and 'requests' needed to be installed
import dateparser
import datetime
import SQLHandler
import requests

"""Handles bot API operations"""
class BotHandler:

    """Constructor creates object with API token"""
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    """Gets all unread messages"""
    def get_updates(self, offset):
        method = 'getUpdates'
        parameters = {'timeout': 30, 'offset': offset}
        response = requests.get(self.api_url + method, parameters)
        return response.json()['result']

    """Gets chat id"""
    @staticmethod
    def get_chat_id(data):
        response = data['message']['chat']['id']
        return response

    """Send message 'text' to chat 'chat_id'"""
    def send_message(self, chat_id, text):
        parameters = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        response = requests.post(self.api_url + method, parameters)
        return response

    """Get 'update_id' of last message"""
    @staticmethod
    def get_last_update_id(data):
        return data[-1]['update_id']


"""Check if it's a date or not"""
def recognize_date(text):
    return dateparser.parse(text, locales=['en'], settings={'PREFER_DATES_FROM': 'future', 'DATE_ORDER': 'DMY'})


"""Recognize input command"""
def response_commands(text):
    if text in ['/start', '/help']:
        return 'help'
    elif text == '/t':
        return 'd' + datetime.datetime.now().strftime("%Y%m%d")
    elif text == '/tm':
        return 'd' + (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y%m%d")
    else:
        return 0


"""Recognize input text"""
def response_text(text):
    if recognize_date(text) is None:
        return 0
    else:
        return recognize_date(text).strftime("d%Y%m%d")


"""Create text to response"""
def response_message(date):
    database = SQLHandler.SQLHandler()
    if database.check_if_exists(date) == 1:
        schedule = database.read_from_base(date)
        response = '-------------------\n'
        for i in range(len(schedule)):
            response += schedule[len(schedule) - 1 - i][0] + "\n"  # CLASS NAME
            response += schedule[len(schedule) - 1 - i][1] + " - " # STARTING HOUR
            response += schedule[len(schedule) - 1 - i][2] + "\n-------------------\n"  # ENDING HOUR
    else:
        response = 'No classes this day'
    return response


"""Main function, operates outcoming messages"""
def main():

    # API key here
    bot = BotHandler(your_token)

    offset = 0

    help_message = 'To get schedule, use commands\n/t and /tm, or write weekday\n or date in format dd.mm'

    while True:
        # Get updates
        update = bot.get_updates(offset)
        # If there's an update, set new offset
        if len(update) > 0:
            offset = bot.get_last_update_id(update) + 1

        for i in range(0, len(update)):
            update_text = update[i]['message']['text']
            chat_id = update[i]['message']['chat']['id']

            # If command
            if update_text[0] == '/':
                response = response_commands(update_text)
                if response == 0:
                    bot.send_message(chat_id, 'Unknown command')
                elif response == 'help':
                    bot.send_message(chat_id, help_message)
                else:
                    bot.send_message(chat_id, response_message(response))
            # If plain text
            elif response_text(update_text) != 0:
                bot.send_message(chat_id, response_message(response_text(update_text)))
            else:
                bot.send_message(chat_id, 'Unrecognized input')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
