from telegram_bot import BotGadu
from keep_alive import keep_alive



if __name__ == '__main__':
    bot = BotGadu()
    keep_alive()
    bot.run()
    