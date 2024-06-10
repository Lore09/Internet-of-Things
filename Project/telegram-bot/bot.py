import logging
import os
from dotenv import load_dotenv

from query import fetch_alarms

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
            "start": "I'm a bot that can help you to handle the alarms",

            "help": "show this message",
            
            "get_alarms": "returns all the alarms",
            
            "remove_alarms" : """remove an alarm given:
                                - Device ID
                                - Alarm ID
                        Example: /remove_alarm 1 1
            """,
            

}


help_text = f"""{help_msgs["start"]}
    
Commands:
    
**/help**            {help_msgs["help"]}
    
**/get_alarms**      {help_msgs["get_alarms"]}
    
**/remove_alarm**    {help_msgs["remove_alarms"]}
    
**/add_alarm**
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


async def get_alarms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, _ = fetch_alarms(URL_REQUEST) 
    # Sending text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text
    )


async def remove_alarm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""

    message = update.message.text
    splitted_msg = message.split(" ")
    
    if len(splitted_msg) != 3:
        # check message length
        text="Error: the message doesn't contain the correct information\n" + help_msgs["remove_alarm"]
    
    else:
        try:
            device_id   = int(splitted_msg[1])
            alarm_id    = int(splitted_msg[2])

            status_code = query_remove(URL_REQUEST, device_id, alarm_id)

            if status_code == 200:
                text = "Done!"
            else:
                text = "Sorry, there is an internal error"

        except ValueError: 
            text = """
            Error: the message doesn't contain the correct information
            The two numbers must be integer\n""" + help_msgs["remove_alarm"]
    
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

    get_alarms_handler = CommandHandler('get_alarms', get_alarms)
    application.add_handler(get_alarms_handler)

    remove_alarm_handler = CommandHandler('remove_alarm', remove_alarm)
    application.add_handler(remove_alarm_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    
    # Set up the command menu (is not working?)
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("get_alarms", "Start the bot"),
        BotCommand("remove_alarm", "Show help message"),
    ]
    application.bot.set_my_commands(commands)

    application.run_polling()



if __name__ == '__main__':
    main()    
