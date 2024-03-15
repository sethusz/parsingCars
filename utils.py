from io import BytesIO

from PIL import Image
import asyncio
import requests
import logging
import os
from aiogram.types import InputMediaPhoto, InputFile

from log import logger

# Setting logger
logger_utils = logging.getLogger('log.utils.py')


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


async def download_photo(paths: list, ads_number: str) -> list:
    try:
        paths_result = []
        for number, path in enumerate(paths, start=1):
            if number > 6:
                continue
            response = requests.get(path, headers=HEADERS)
            webp_image = Image.open(BytesIO(response.content))
            name = f'{ads_number}_{number}.jpeg'
            webp_image.save(name, 'JPEG', optimize=True, quality=95)
            paths_result.append(name)
            print(f'save photo {name}')
        return paths_result
    except Exception as ex:
        return []


async def delete_photo(paths: list) -> None:
    for save_path in paths:
        if os.path.exists(save_path):
            os.remove(save_path)
            print(f"File {save_path} deleted successfully.")
        else:
            print(f"File {save_path} not found.")


async def make_group_post(bot, group, post):
    media = []

    photo_paths = await download_photo(paths=post['photos'], ads_number=post['ads_id'])
    try:

        for n, photo in enumerate(photo_paths):
            print('input photo', n)
            if n == 0:
                media.append(InputMediaPhoto(media=InputFile(photo), caption=post['msg'], parse_mode='HTML'))
            else:
                media.append(InputMediaPhoto(media=InputFile(photo)))

        await bot.send_media_group(group, media)

        await delete_photo(photo_paths)

        print(f'SUCCESS SEND TELEGRAM #{post["ads_id"]}')
    except Exception as ex:
        await delete_photo(photo_paths)
        logger_utils.warning(f'send telegram post ex - {ex}')
        await asyncio.sleep(60)
