import gc
from keep_alive import keep_alive
from telegram_bot import BotGadu


if __name__ == '__main__':
    count = gc.get_count()
    gc.collect()
    print(f'old cache values : {count} and reset values are : {gc.get_count()}')
    bot = BotGadu()
    keep_alive()
    bot.run()
    