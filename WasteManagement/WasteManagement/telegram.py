
import requests

TOKEN = '425256030:AAHyvDT4i7cOzFWeceswXnuFvR0L7jijzBs'


def get_bot_url(cmd):
    return 'https://api.telegram.org/bot{}/{}'.format(TOKEN, cmd)


CHANNEL_ID = {
    "SALESMANTRACKING": -239207477
}


def send_message(channel_name, message):
    response = requests.post(
        get_bot_url('sendMessage'),
        data={
            'chat_id': CHANNEL_ID[channel_name],
            'text': message,
            'parse_mode': "HTML",
        }
    )
    return response
