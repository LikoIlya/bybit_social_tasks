from enum import IntEnum
from pathlib import Path
from typing import Literal


class Actions(IntEnum):
    TWEET = 0
    FOLLOW = 1
    LIKE = 2
    RETWEET = 3
    QUOTE = 4
    REPLY = 5


# Последовательность действий для выполнения
ACTION_SEQUENCE = [
    Actions.FOLLOW, 
    Actions.LIKE, 
    Actions.RETWEET,
    Actions.QUOTE,
    Actions.REPLY
]

# файлы с данными
TWITTERS_TXT = Path("twitters.txt") # файл с аккаунтами
PROXIES_TXT = Path("proxies.txt") # файл с прокси
LIKE_TXT = Path("to_like.txt") # файл с твитами для лайка
FOLLOW_TXT = Path("to_follow.txt") # файл с аккаунтами для подписки
RETWEET_TXT = Path("to_retweet.txt") # файл с твитами для ретвита
PHRASES_TXT = Path("quote_phrases.txt") # файл с фразами для цитат
QUOTE_TXT = Path("to_quote.txt") # файл с твитами для цитат
REPLY_MSGS_TXT = Path("reply_msgs.txt") # файл с сообщениями для ответов
REPLY_TXT = Path("to_reply.txt") # файл с твитами для ответов

RESULTS_CSV = Path("results.csv") # файл с результатами

# время ожидания между циклами в секундах
# можно указать кортеж или список из двух чисел, тогда будет выбираться случайное время между ними
# или просто число - тогда будет ждать ровно столько секунд
SLEEP_TIME: tuple | list | int = (3, 10) 