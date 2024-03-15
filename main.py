import datetime
import asyncio
import configparser
import requests
from aiogram import Bot
import logging

from log import logger
import models
from utils import make_group_post

config = configparser.ConfigParser()
config.read('config.ini')

loop = asyncio.get_event_loop()

DELAY = {'task_delay': 20.0}

# Setting logger
logger_main = logging.getLogger('log.main.py')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


#  WALLAPOP settings
PARS_URL = config['WALLAPOP']['filter_url']
BASE_PAGE = 'https://es.wallapop.com/item/'

#  TELEGRAM settings
GROUP_ID = config['TELEGRAM']['group_id']
TELEGRAM_BOT = Bot(token=config['TELEGRAM']['token'])


async def task_watch():
    print(f'start task {datetime.datetime.now()}')
    try:
        response = requests.get(PARS_URL, headers=HEADERS)
        search_objects = response.json()['search_objects']

        for ads in search_objects:
            ads_url = BASE_PAGE+ads["content"]['web_slug']
            create = models.Ads.create(ads_id=ads['id'], ads_url=ads_url)
            if create:
                post = {}
                ads_detail = ads['content']

                title = ads_detail.get('title', '-')
                price = ads_detail['price']
                engine = ads_detail.get('engine', '-')
                km = ads_detail.get('km')
                gearbox = ads_detail.get('gearbox', '-')
                description = ads_detail.get('storytelling', '-')
                photos = []
                for photo in ads_detail['images']:
                    photos.append(photo['medium'])

                message = f'<b>{title}</b>\n\n' \
                          f'Цена: {price} €\n' \
                          f'Топливо: {engine.title()}\n' \
                          f'Пробег: {km}\n' \
                          f'Коробка: {gearbox.title()}\n' \
                          f'Описание: {description}\n' \
                          f'<a href="{ads_url}">Ссылка</a>'

                post['ads_id'] = ads['id']
                post['msg'] = message
                post['photos'] = photos

                await make_group_post(TELEGRAM_BOT, GROUP_ID, post)

    except Exception as ex:
        logger.warning(f'task_watch - {ex}')

    print(f'end task {datetime.datetime.now()}')

    when_to_call = loop.time() + DELAY['task_delay']
    loop.call_at(when_to_call, task_callback)


def task_callback():
    asyncio.ensure_future(task_watch())


if __name__ == '__main__':
    task_callback()
    loop.run_forever()

