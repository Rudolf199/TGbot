import asyncio
import json

import bs4
import requests
import lxml
from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN
from headers import headers
# loop = asyncio.get_event_loop()
# Поток нам не нужен, т.к. он и так создается в диспатчере.
# bot = Bot(BOT_TOKEN, parse_mode="HTML")
# dp = Dispatcher(bot)


def get_data(url):
    r = requests.get(url=url, headers=headers)
    with open("index.html", "w", encoding='utf-8') as file:
        file.write(r.text)

def get_first_news():
    user = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    }

    url = "https://ria.ru/"
    r = requests.get(url=url, headers=user)

    soup = bs4.BeautifulSoup(r.text, "lxml")
    articles = soup.find_all("a", class_="cell-list__item-link color-font-hover-only")

    news_dict = {}

    for article in articles:
        article_title = article.find("span", class_="cell-list__item-desc").text.strip()
        article_desc = article.find("span", class_="cell-list__item-title").text.strip()
        article_url = article.get("href")
        article_id = article_url.split("/")[-1]
        if article_url[-1] == "l":
            article_id = article_id[:-5]
        else:
            article_id = article_id[:-22]
        # print(article_id)
        news_dict[article_id] = {
            "article_title": article_title,
            "article_desc": article_desc,
            "article_url": article_url
        }

        # article_data_time = article.find("span", class_="elem-info").text
        print(f"{article_title} | {article_url} | {article_desc}")
    with open("news_dict.json", "w", encoding='utf-8') as news_file:
        json.dump(news_dict, news_file, indent=4, ensure_ascii=False)

def check_news_update():
    with open("news_dict.json", encoding='utf-8') as news_file:
        news_dict = json.load(news_file)
    # print(news_list)

    user = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    }

    url = "https://ria.ru/"
    r = requests.get(url=url, headers=user)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    articles = soup.find_all("a", class_="cell-list__item-link color-font-hover-only")
    fresh_news = {}
    for article in articles:
        article_url = article.get("href")
        article_id = article_url.split("/")[-1]
        if article_url[-1] == "l":
            article_id = article_id[:-5]
        else:
            article_id = article_id[:-22]
        if article_id in news_dict:
            continue
        else:
            article_title = article.find("span", class_="cell-list__item-desc").text.strip()
            article_desc = article.find("span", class_="cell-list__item-title").text.strip()
            # article_url = article.get("href")

            news_dict[article_id] = {
                "article_title": article_title,
                "article_desc": article_desc,
                "article_url": article_url
            }
            fresh_news[article_id] = {
                "article_title": article_title,
                "article_desc": article_desc,
                "article_url": article_url
            }
    with open("news_dict.json", "w", encoding='utf-8') as news_file:
        json.dump(news_dict, news_file, indent=4, ensure_ascii=False)

    return fresh_news

def main():
    get_first_news()
    print("hello\n", check_news_update())

if __name__ == '__main__':
    main()
    # from handlers import dp, send_to_admin
    # executor.start_polling(dp, on_startup=send_to_admin)

