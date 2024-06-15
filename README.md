# bybit_social_tasks
1. Версия python 3.11
2. Устанавливаем зависимости pip install -r requirements.txt
3. При первичном запуске создаются все необходимые файлы
4. Файл [config.py](./config.py) содержит `ACTION_SEQUENCE` в котором задаем последовательность действий.
5. В файл proxies.txt вводим прокси в формате socks5://login:pass@ip:port или http://login:pass@ip:port
6. В файл twitters.txt вводим auth_token от аккаунта
7. Файл quote_phrases.txt - текст для цитирования (выбирается рандомно).
8. Файл reply_msgs.txt - текст для ответов (выбирается рандомно).
9. В файл to_follow.txt вводим account_id для фоллова
10. В файл to_like.txt вводим tweet_id для лайка
11. В файл to_quote.txt вводим tweet_id для цитаты
12. В файл to_reply.txt вводим tweet_id для ответов
13. В файл to_retweet.txt вводим tweet_id для ретвита
14. В файле results.txt будут находиться данные в формате auth_token [USER/TWEET_ID] [ACTION:True/False/URL]
