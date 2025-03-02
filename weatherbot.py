import requests
from typing import Final
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, Application, filters
from os import getenv
from dotenv import load_dotenv
import google.generativeai as genai
import re


# Load .env file
load_dotenv()

#Weather API Key
WEATHER_API_KEY = getenv("WEATHER_API_KEY")

#Telegram Bot API Details
TOKEN: Final = getenv("TOKEN")
BOT_USERNAME: Final = getenv("BOT_USERNAME")

#Gemini API Key
GEMINI_API_KEY = getenv("GEMINI_API_KEY")

#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome to Weather Bot!!!\nThis bot will provide you with current weather data\n\nSource : OpenWeather and Gemini\n\nEnter the ZIP code of your area to get weather report and nearby places.\n\n[Note that Gemini may provide inaccurate results. Try generating multiple times to get better results]')

#Error
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update.message.chat.id} caused error {context.error}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    zip = update.message.text

    weather_response = getWeather(zip)
    if weather_response:
        gemini_response = getGemini(weather_response,zip)
        await update.message.reply_text(gemini_response)
    else:
        await update.message.reply_text("Invalid ZIP code or not found in our database. Please try again")

def getWeather(zip):
    zip_country=zip.strip() + ",in"
    url_geocoding = f'https://api.openweathermap.org/data/2.5/weather?zip={zip_country}&appid={WEATHER_API_KEY}'
    req_current = requests.get(url_geocoding).json()
    if 'cod' in req_current and req_current['cod'] == '404':
        print ('Sorry, the city you entered does not exist')
        return 0

    response = f'Weather Report:\nArea : {req_current["name"]}\nLatitude : {req_current["coord"]["lat"]}\nLongitude : {req_current["coord"]["lon"]}\nClimate : {req_current["weather"][0]["main"]}\nTemperature : {req_current["main"]["temp"] - 273.15:.2f} °C\nHumidity : {req_current["main"]["humidity"]} %\nVisibility : {req_current["visibility"]} metres\n'
    
    return response

def getGemini(weather_response, zip):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[f''' @Google Maps suggest specific locations nearby to visit in the zip code - {zip} 

Kindly take note of the clauses:
1. THE ZIP CODE OF THE LOCATIONS SHOULD BE *STRICTLY* {zip}. If some address has a different zip code, either remove that entry of search again for another
2. Verify twice about the map links whether they are working
3. It should ideally contain two parks, malls, temples or churches or mosques, local restaurants. If there are no places with the matching zip code, display the text "No Nearby Places Found"
4. I want the result in the following format. Replace Location_1 and Location_2 with the respective names:

Here are your results buddy:
10-----10
              
Parks:
              
Location_1: Address.. 
<map link>
              
Location_2: Address.. 
<map link>
              
Malls:
              
Location_1: Address.. 
<map link>
              
Location_2: Address.. 
<map link>
              
Religious places:
              
Location_1: Address.. 
<map link>
              
Location_2: Address.. 
<map link>
              
Restaurants:
              
Location_1: Address.. 
<map link>
              
Location_2: Address.. 
<map link>
              
10-----10
              
The following is an example response:
              
Here are your results buddy:
10-----10

Parks:

Sanjay Gandhi Park: Sanjay Gandhi Park, 80 Feet Rd, Chandra Layout, Stage 2, Hoysala Nagar, Bengaluru, Karnataka 560006, India.
<https://maps.app.goo.gl/jL5WjWfB85dG5n137>

Srikanteshwara Park: 7th Main Rd, RPC Layout, Vijayanagar, Bengaluru, Karnataka 560006, India.
<https://maps.app.goo.gl/gW2H2R3W9qjG8rM48>

Malls:

Religious places:

Shree Veeranjaneya Swamy Temple: 1st Main Rd, RPC Layout, Vijayanagar, Bengaluru, Karnataka 560006, India.
<https://maps.app.goo.gl/R6fE6YjYw47G9g8N6>

Jayamahal Church: 4/1, Jayamahal Main Rd, Jayamahal, Bengaluru, Karnataka 560006, India.
<https://maps.app.goo.gl/X91XbFf7f65d9bC58>

Restaurants:

The Marwadi Kitchen: 110, 1st Main Rd, RPC Layout, Vijayanagar, Bengaluru, Karnataka 560006, India.
<https://maps.app.goo.gl/X9TdxQWJ35Ff19W36>

Naati Mane: 5, 10th Main Rd, RPC Layout, Vijayanagar, Bengaluru, Karnataka 560006, India.
<https://maps.app.goo.gl/QG352H367L5Qo7xW9>

10-----10'''])
    # Extract content
    match = re.search(r"10-----10(.*?)10-----10", response.text, re.DOTALL)
    if match:
        content_between = match.group(1).strip()
        return weather_response + "\nHere are some places to visit:\n\n" + content_between


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
