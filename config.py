from enum import IntEnum
from pathlib import Path


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
    Actions.QUOTE
]

# файлы с данными
TWITTERS_TXT = Path("twitters.txt") # файл с аккаунтами
PROXIES_TXT = Path("proxies.txt") # файл с прокси
LIKE_TXT = Path("to_like.txt") # файл с твитами для лайка
FOLLOW_TXT = Path("to_follow.txt") # файл с аккаунтами для подписки
RETWEET_TXT = Path("to_retweet.txt") # файл с твитами для ретвита
PHRASES_TXT = Path("quote_phrases.txt") # файл с фразами для цитат
QUOTES_TXT = Path("to_quote.txt") # файл с твитами для цитат
REPLY_MSGS_TXT = Path("reply_msgs.txt") # файл с сообщениями для ответов
REPLIES_TXT = Path("to_reply.txt") # файл с твитами для ответов

RESULTS_TXT = Path("results.txt") # файл с результатами
