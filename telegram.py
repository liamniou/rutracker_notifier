from pprint import pprint
import telepot
bot = telepot.Bot('447936469:AAHzcTHK_R9D_U6qtyZzlyABIxvAFWPz6BA')
#bot.sendMessage(294967926, 'Hey!')


#Receive message
response = bot.getUpdates()
pprint(response)