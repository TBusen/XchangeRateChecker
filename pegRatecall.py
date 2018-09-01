import requests
from twilio.rest import Client
import os


def get_conversion(base, symbol):
    # base url
    base_url = f'https://api.exchangeratesapi.io/latest?base={base}&symbols={symbol} HTTP/1.1'
    response = requests.get(base_url)
    json = response.json()
    return json


# set up base conversion pairs
combos = (('USD', 'CHF'), ('CHF', 'EUR'), ('USD', 'EUR'))

response = [get_conversion(a, b)
            for a, b in combos]  # call api's and put in list

# parse out response
rates = list()


for responses in response:
    base = responses['base']
    to = next(iter(responses['rates']))  # get value key of iterator
    rate = next(iter(responses['rates'].values()))  # get rate
    date = responses['date']
    rates.append((base, to, rate, date))


for base, to, rate, date in rates: # set rates variables
    if base == 'USD' and to == 'CHF':
        usd2chf = rate
    elif base == 'CHF' and to == 'EUR':
        chf2eur = rate
    else:
        usd2eur = rate

usd2chf2eur = usd2chf * chf2eur  # us to swiss to eur


def what_to_do():
    if (1 - (usd2chf2eur/usd2eur)) < 0.01:  # if < than 1% difference it doesn't really matter
        return 'doesnt_matter'
    elif usd2chf2eur < usd2eur:  # if euros is larger then don't convert to chf first
        return 'go_euro'
    else:  # if chf is larger then don't use us credit card
        return 'go_swiss'


def text_message(): # generate text message based on curent xchange rates
    if what_to_do() == 'doesnt_matter':
        return '''Just your husband's awesome currency monitoring service notifying you that there is less than a 1 percent difference when converting from 🇺🇸 --> 🇨🇭 --> 🇪🇺 and 🇺🇸 --> 🇪🇺, it doesn't really matter.  Use whatever card you want, the world is your oyster this month. 😎🍻'''
    elif what_to_do() == 'go_euro':
        return f'''Just your husband's awesome currency monitoring service notifying you that you'll lose less money this month if you use your 🇺🇸 credit cards.  For every $100 you spend you'll save ${round(100*((1-usd2chf2eur) - (1-usd2eur)),2)} 🤑🤑🤑.  Va dépenser de l\'argent, bravo pour la France!'''
    else:
        return f'''Just your husband's awesome currency monitoring service notifying you that you'll lose less money this month if you use your 🇨🇭 bank account.  For every $100 you spend you'll save {round(100*((1-usd2eur) - (1-usd2chf2eur)),2)} 💰💰💰.  La Suisse est chère, économisez votre argent!'''

# make api call to twillio

account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_TOKEN']
client = Client(account_sid, auth_token)

client.messages.create(
    body=text_message(),
    from_=os.environ['FROM_NO'],
    to=os.environ['TO_NO']
)
