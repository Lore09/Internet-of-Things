import logging
import os
from dotenv import load_dotenv

from query import *
from parse_msg import *

from telegram import Update, BotCommand
from telegram.ext import Updater, filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
BOT_TOKEN   = os.getenv('BOT_TOKEN',    None)
URL_REQUEST = os.getenv('URL_REQUEST',  None)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


help_msgs = {
            "start"         : "I'm a bot that can help you to handle the alarms",

            "help"          : "show this message",

            "get_devices"   : "returns all the devices",
            
            "get_alarms"    : "returns all the alarms",
            
            "remove_alarms" : """remove an alarm given:
                                - device ID
                                - alarm ID
                        Example: /remove_alarm esp 1
            """,
            
            "add_alarm"     : """add a new alarm given
                                - device ID
                                - type (1 for standard, 2 for periodic)
                                - the other info
                                    - if 1, a string representing the datime object, composed as:
                                        day-month-year-hour-minute (all integers)
                                        Example: /add_alarm esp 1 10-6-2024-8-00
                                    - if 2, a string with the days (two letters) and the time
                                        Example: /add_alarm esp 2 MO-WE-FR-8-0

            """,

            "trigger_alarm" : "trigger an alrm given the device ID",

            "stop_alarm"    : "stop an alarm given the device ID"
}


help_text = f"""{help_msgs["start"]}
    
Commands:
    
/help           {help_msgs["help"]}

/get_devices    {help_msgs["get_devices"]}
    
/get_alarms     {help_msgs["get_alarms"]}
    
/remove_alarm   {help_msgs["remove_alarms"]}
    
/add_alarm      {help_msgs["add_alarm"]}

/trigger_alarm  {help_msgs["trigger_alarm"]}

/stop_alarm     {help_msgs["stop_alarm"]}
"""



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=help_text
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=help_text
    )

# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id, 
#         text=update.message.text
#     )


async def get_devices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, _ = fetch_devices(URL_REQUEST)
    # Sending text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text
    )


async def get_alarms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, _ = fetch_alarms(URL_REQUEST) 
    # Sending text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text
    )


async def remove_alarm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    text = parse_remove_msg(message, help_msgs, URL_REQUEST)
    # send response
    await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=text
            )


async def add_alarm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    text = parse_add_msg(message, help_msgs, URL_REQUEST)
    # send response
    await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=text
            )
            

async def trigger_alarm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    text = parse_trigger_msg(message, help_msgs, URL_REQUEST)
    # send response
    await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=text
            )


async def stop_alarm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    text = parse_stop_msg(message, help_msgs, URL_REQUEST)
    # send response
    await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=text
            )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Sorry, I didn't understand that command."
    )



def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    # application.add_handler(echo_handler)

    get_devices_handler = CommandHandler('get_devices', get_devices)
    application.add_handler(get_devices_handler)

    get_alarms_handler = CommandHandler('get_alarms', get_alarms)
    application.add_handler(get_alarms_handler)

    remove_alarm_handler = CommandHandler('remove_alarm', remove_alarm)
    application.add_handler(remove_alarm_handler)

    add_alarm_handler = CommandHandler('add_alarm', add_alarm)
    application.add_handler(add_alarm_handler)

    trigger_alarm_handler = CommandHandler('trigger_alarm', trigger_alarm)
    application.add_handler(trigger_alarm_handler)

    stop_alarm_handler = CommandHandler('stop_alarm', stop_alarm)
    application.add_handler(stop_alarm_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    
    # Set up the command menu (is not working?)
    commands = [
        BotCommand("start",         "Start the bot"),
        BotCommand("help",          "Show help message"),
        BotCommand("get_devices",   help_msgs["get_devices"]),
        BotCommand("get_alarms",    help_msgs["get_alarms"]),
        BotCommand("remove_alarm",  help_msgs["remove_alarms"]),
        BotCommand("add_alarm",     help_msgs["add_alarm"]),
        BotCommand("trigger_alarm", help_msgs["trigger_alarm"]),
        BotCommand("stop_alarm",    help_msgs["stop_alarm"]),
    ]
    application.bot.set_my_commands(commands)

    application.run_polling()



if __name__ == '__main__':
    main()    
