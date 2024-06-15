from functools import partial
from itertools import cycle
import asyncio
import random
from unittest import result
import curl_cffi
from better_proxy import Proxy
import twitter

import config

for filepath in (
    config.TWITTERS_TXT,
    config.PROXIES_TXT,
    config.RESULTS_TXT,
    config.LIKE_TXT,
    config.FOLLOW_TXT,
    config.RETWEET_TXT,
    config.PHRASES_TXT,
    config.QUOTES_TXT,
    config.REPLY_MSGS_TXT,
    config.REPLIES_TXT
):
    filepath.touch(exist_ok=True)


TWITTER_ACCOUNTS = twitter.account.load_accounts_from_file(config.TWITTERS_TXT)
PROXIES = Proxy.from_file(config.PROXIES_TXT)

if not PROXIES:
    PROXIES = [None]

def write_result(result):
    with open(config.RESULTS_TXT, "a") as results_file:
        results_file.write(f"{result}\n")

async def main():

    proxy_to_account_list = list(zip(cycle(PROXIES), TWITTER_ACCOUNTS))

    for (proxy, twitter_account) in proxy_to_account_list:  # type: (Proxy, twitter.Account), str, str, Path,
        try:
            async with twitter.Client(twitter_account, proxy=proxy) as twitter_client:
                for action in config.ACTION_SEQUENCE:
                    ids = []
                    act_chr = ""
                    func = None
                    match action:
                        case config.Actions.FOLLOW:
                            ids = config.FOLLOW_TXT.read_text().splitlines()
                            act_chr = "F"
                            func = twitter_client.follow
                            print("Делаю подписки...")
                        case config.Actions.LIKE:
                            ids = config.LIKE_TXT.read_text().splitlines()
                            act_chr = "L"
                            func = twitter_client.like
                            print("Делаю лайки...")
                        case config.Actions.RETWEET:
                            ids = config.RETWEET_TXT.read_text().splitlines()
                            act_chr = "RT"
                            func = twitter_client.repost
                            print("Делаю ретвиты...")
                        case config.Actions.QUOTE:
                            ids = config.QUOTES_TXT.read_text().splitlines()
                            act_chr = "Q"
                            func = twitter_client.quote
                            print("Делаю цитаты...")
                        case config.Actions.REPLY:
                            ids = config.REPLIES_TXT.read_text().splitlines()
                            act_chr = "R"
                            func = twitter_client.reply
                            print("Делаю ответы...")
                    for id in ids:
                        final_message = f"{twitter_account.auth_token}"
                        try:
                            if act_chr == "Q":
                                tweet = await twitter_client.request_tweet(id)
                                phrase = random.choice(config.PHRASES_TXT.read_text().splitlines())
                                result = await func(tweet.url, phrase)
                            elif act_chr == "R":
                                message = random.choice(config.REPLY_MSGS_TXT.read_text().splitlines())
                                result = await func(id, message)
                            else:
                                result = await func(id)
                            if isinstance(result, twitter.Tweet):
                                result = result.url
                            print(f"{twitter_account} {id} {act_chr}:{result}")
                            final_message = f"{final_message} {id} {act_chr}:{result}"
                            write_result(final_message)
                            await asyncio.sleep(3)
                        except curl_cffi.requests.errors.RequestsError as exc:
                            print(f"Ошибка запроса. Возможно, плохой прокси: {exc}")
                            continue
                        except Exception as exc:
                            print(f"Что-то очень плохое: {exc}")
                            continue
        except Exception as err:
            print(err)
            continue
if __name__ == "__main__":
    asyncio.run(main())
