import argparse
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json, requests, time
from datetime import datetime


ifttt_webhook_url = 'https://maker.ifttt.com/trigger/Price_Alert/with/key/eo41Kv7KaU0G8jJqQDtGc8aPUcznocoDKM_Fz1i9rN5'


# function to get the bitcoin price
def get_latest_bitcoin_price():

    # coinmarketcap api url
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    headers = {
        'Accepts': 'application/json',

        # coinmarketcap individual key
        'X-CMC_PRO_API_KEY': '936cee4c-60d5-4102-85bd-d97e64c76ce6',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url)
    # getting the json data
        data = json.loads(response.text)
    # return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    print("BTC Price", float(data['data'][0]['quote']['USD']['price']))
    return float(data['data'][0]['quote']['USD']['price'])


# requesting the notification from IFTTT
def post_ifttt_webhook(event, value):
    # The payload that will be sent to IFTTT service
    data = {'value1': value}
    # inserts our desired event
    ifttt_event_url = ifttt_webhook_url.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)
    print("IFTTT", ifttt_event_url)


def format_bitcoin_history(bitcoin_history):
    rows = []
    for bit_price in bitcoin_history:
        # Formats the date into a string: '26.03.2020 19:09'
        date = bit_price['date'].strftime('%d.%m.%Y %H:%M')
        new_price = bit_price['price']
        # <b> (bold) tag creates bolded text
        # 26.03.2020 19:09: $<b>6877.4</b>
        row = '{}: $<b>{}</b>'.format(date, new_price)
        rows.append(row)

        # Use a <br> (break) tag to create a new line
        # Join the rows delimited by <br> tag: row1<br>row2<br>row3
    return '<br>'.join(rows)


def run (bitcoin_threshold, time_gap):
    bitcoin_history = []
    threshold = float(bitcoin_threshold[0])
    intervals = float(time_gap[0])
    while True:
        new_price = get_latest_bitcoin_price()
        date = datetime.now()
        bitcoin_history.append({'date': date, 'price': new_price})

        # Send an emergency notification
        if new_price < threshold:
            post_ifttt_webhook('Bitcoin_Price_Emergency', new_price)

        # Send a Telegram notification
        # Once we have 5 items in our bitcoin_history send an update
        if len(bitcoin_history) == 1:
            post_ifttt_webhook('Bitcoin_Price_Update',
                               format_bitcoin_history(bitcoin_history))
            # Reset the history
            bitcoin_history = []

        # Time gap as you want
        time.sleep(intervals * 60)


# this is is command line utility function, that takes the argument, parse it ans then call the run function
def main():
    parser = argparse.ArgumentParser(description="Bitcoin price tracker")
    # command line variable for time gap
    parser.add_argument("-i", "--interval", type=int, nargs=1,
                        metavar="interval", default=[1], help="Time interval in minutes")
    # command line variable for threshold
    parser.add_argument("-t", "--threshold", type=int, nargs=1,
                        metavar="threshold", default=[10000], help="Threshold in USD")
    new_args = parser.parse_args()
    print('Running Application with time interval of ',  new_args.interval[0], ' and threshold = $',  new_args.threshold[0])
    # calls the run function
    run(new_args.threshold,  new_args.interval)


if __name__ == '__main__':
    main()
