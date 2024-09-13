import requests
from typing import Final
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, Application, filters

#Weather API Key
WEATHER_API_KEY = '<hidden>'

#Telegram Bot API Key
TOKEN: Final = '<hidden>'
BOT_USERNAME: Final = '<hidden>'

#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome to Weather Bot!!!\nThis bot will provide you with current weather data\n\nSource : OpenWeather\n\nEnter the name of a city to get weather report')

#Error
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update.message.chat.id} caused error {context.error}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_input = update.message.text
    response = getWeather(city_input)

    await update.message.reply_text(response)

def getWeather(city):
    name=city.strip().title()
    url_geocoding = f'http://api.openweathermap.org/geo/1.0/direct?q={name}&limit=1&appid={WEATHER_API_KEY}'
    req_geo = requests.get(url_geocoding).json()
    if not req_geo:
        return 'Sorry, the city you entered does not exist'

    lat = req_geo[0]['lat']
    long = req_geo[0]['lon']

    url_current = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={WEATHER_API_KEY}'
    req_current = requests.get(url_current).json()


    response = f'Weather Report:\n\nCity : {name}\nDesc : {req_current["weather"][0]["main"]}\nTemp : {req_current["main"]["temp"]} K\nHumidity : {req_current["main"]["humidity"]} %\nVisibility : {req_current["visibility"]} metres'
    return response


if __name__ == '__main__':
    
    print('Starting bot..')
    app = Application.builder().token(TOKEN).build()

    #Commands
    app.add_handler(CommandHandler('start',start_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Error
    app.add_error_handler(error)

    #Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=0.2)
