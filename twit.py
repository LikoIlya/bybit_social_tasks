import csv
from itertools import cycle
import asyncio
from pathlib import Path
import random
import curl_cffi
from better_proxy import Proxy
import twitter

import config

for filepath in (
    config.TWITTERS_TXT,
    config.PROXIES_TXT,
    config.RESULTS_CSV,
    config.LIKE_TXT,
    config.FOLLOW_TXT,
    config.RETWEET_TXT,
    config.PHRASES_TXT,
    config.QUOTE_TXT,
    config.REPLY_MSGS_TXT,
    config.REPLY_TXT,
):
    filepath.touch(exist_ok=True)


def load_lines(filepath: Path | str) -> list[str]:
    with open(filepath, "r") as file:
        return [line.strip() for line in file.readlines() if line != "\n"]


def load_accounts_ids_from_file(
    filepath: Path | str,
    *,
    separator: str = ":",
    index: int = 0,
) -> list[int]:
    """
    :param filepath: Путь до файла с данными об аккаунтах.
    :param separator: Разделитель между данными в строке.
    :return: Список ID Twitter аккаунтов.
    """
    accounts = []
    for line in load_lines(filepath):
        data = line.split(separator)[index]
        accounts.append(data)
    return accounts


TWITTER_ACCOUNTS = zip(
    load_accounts_ids_from_file(config.TWITTERS_TXT),
    twitter.account.load_accounts_from_file(
        config.TWITTERS_TXT,
        fields=("ACCOUNT_INTERNAL_ID", "auth_token", "password", "email", "username"),
    ),
)
PROXIES = Proxy.from_file(config.PROXIES_TXT)

if not PROXIES:
    PROXIES = [None]


def write_result(rows, result):
    with open(config.RESULTS_CSV, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow(result)


def get_sleep_time():
    sleep_time = random.randint(5, 10)  # as default sleep time
    match config.SLEEP_TIME:
        case int(time):
            sleep_time = time
        case tuple(time_range):
            sleep_time = random.randint(int(time_range[0]), int(time_range[1]))
        case list(choices):
            choices = [int(x) for x in choices]
            sleep_time = random.choice(choices)
        case None:
            pass
    return sleep_time


async def action_rows_builder(
    actions: list[config.Actions], twitter_client: twitter.Client
):
    rows = []
    for action in actions:
        match action:
            case config.Actions.FOLLOW:
                ids = config.FOLLOW_TXT.read_text().splitlines()
                users = await twitter_client.request_users_by_ids(ids)
                for id in ids:
                    row = f"{action.name} https://x.com/{users[int(id)].username}"
                    rows.append(row)
                continue
            case config.Actions.LIKE:
                ids = config.LIKE_TXT.read_text().splitlines()
            case config.Actions.RETWEET:
                ids = config.RETWEET_TXT.read_text().splitlines()
            case config.Actions.QUOTE:
                ids = config.QUOTE_TXT.read_text().splitlines()
            case config.Actions.REPLY:
                ids = config.REPLY_TXT.read_text().splitlines()
        for id in ids:
            try:
                tweet = await twitter_client.request_tweet(id)
                row = f"{action.name} {tweet.url}"
            except twitter.errors.TwitterException as exc:
                print(f"Ошибка запроса: {exc}")
                row = f"{action.name} ??? ERROR {id} ???"
            rows.append(row)
    return [rows]


async def main():
    proxy_to_account_list = list(zip(cycle(PROXIES), TWITTER_ACCOUNTS))

    for proxy, (twitter_account_id, twitter_account) in proxy_to_account_list:  # type: (Proxy, twitter.Account), str, str, Path,
        rows = ["id"]
        result = {
            "id": twitter_account_id,
        }
        try:
            async with twitter.Client(twitter_account, proxy=proxy) as twitter_client:
                await twitter_client.establish_status()
                action_rows = await action_rows_builder(
                    config.ACTION_SEQUENCE, twitter_client
                )
                rows.extend(*action_rows)
                print(rows)
                for action in config.ACTION_SEQUENCE:
                    ids = []
                    func = None
                    match action:
                        case config.Actions.FOLLOW:
                            ids = config.FOLLOW_TXT.read_text().splitlines()
                            func = twitter_client.follow
                            print("Делаю подписки...")
                        case config.Actions.LIKE:
                            ids = config.LIKE_TXT.read_text().splitlines()
                            func = twitter_client.like
                            print("Делаю лайки...")
                        case config.Actions.RETWEET:
                            ids = config.RETWEET_TXT.read_text().splitlines()
                            func = twitter_client.repost
                            print("Делаю ретвиты...")
                        case config.Actions.QUOTE:
                            ids = config.QUOTE_TXT.read_text().splitlines()
                            func = twitter_client.quote
                            print("Делаю цитаты...")
                        case config.Actions.REPLY:
                            ids = config.REPLY_TXT.read_text().splitlines()
                            func = twitter_client.reply
                            print("Делаю ответы...")
                    for id in ids:
                        try:
                            if action == config.Actions.FOLLOW:
                                user = await twitter_client.request_user_by_id(int(id))
                                act_key = f"{action.name} https://x.com/{user.username}"
                                print(f"Подписываюсь на {user.username}")
                            elif action in [
                                config.Actions.LIKE,
                                config.Actions.RETWEET,
                                config.Actions.QUOTE,
                                config.Actions.REPLY,
                            ]:
                                try:
                                    tweet = await twitter_client.request_tweet(id)
                                    act_key = f"{action.name} {tweet.url}"
                                except twitter.errors.TwitterException as exc:
                                    act_key = f"{action.name} ??? ERROR {id} ???"
                                    raise exc
                            if action == config.Actions.QUOTE:
                                phrase = random.choice(
                                    config.PHRASES_TXT.read_text().splitlines()
                                )
                                response = await func(tweet.url, phrase)
                            elif action == config.Actions.REPLY:
                                message = random.choice(
                                    config.REPLY_MSGS_TXT.read_text().splitlines()
                                )
                                response = await func(id, message)
                            else:
                                response = await func(id)
                            if isinstance(response, twitter.Tweet):
                                response = response.url
                            result[act_key] = response

                            await asyncio.sleep(get_sleep_time())
                        except curl_cffi.requests.errors.RequestsError as exc:
                            print(f"Ошибка запроса. Возможно, плохой прокси: {exc}")
                            continue
                        except Exception as exc:
                            print(f"Что-то очень плохое: {exc}")
                            err_ctx = exc.__str__().replace("\n", ' ')
                            result[act_key] = f"ERROR {err_ctx}"
                            continue
        except Exception as err:
            print(err)
            result["error"] = str(err)
            with open(config.RESULTS_CSV, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(*result.values())
            continue
        write_result(rows, result)


if __name__ == "__main__":
    asyncio.run(main())
