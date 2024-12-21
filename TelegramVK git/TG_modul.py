import asyncio
import json
import logging
import os
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.utils.markdown import link
from aiogram.filters.command import Command
from aiogram.types import URLInputFile, LinkPreviewOptions, InputMediaPhoto
from config import TG_API_TOKEN, CHANNEL_ID, ID_CHAT_BOT
from config import  NAMES_GROUP_LIST
import re

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=TG_API_TOKEN)
# Диспетчер
dp = Dispatcher()
# Хэндлер на команду /start

# Регулярное выражение для проверки ссылок
url_pattern = re.compile(r'^(http|https)://')

# Флаг для управления отправкой сообщений
sending_active = False
def get_photo_file(post):# Функция создаёт массив изображений для отправки "альбома"
    images = []
    for attachment in post['attachments']:
        if attachment['type'] == 'photo':
            photo_sizes = attachment['photo']['sizes']
            max_size_photo = max(photo_sizes, key=lambda x:x['height']*x['width'])
            images.append(max_size_photo['url'])
    return images

async def sending_posts():
    global sending_active
    media = []

    # Множества для хранения уникальных постов
    sent_posts = set()  # Для хранения идентификаторов постов
    sent_texts = set()  # Для хранения текстов постов

    for name_group in NAMES_GROUP_LIST:
        with open(f"Data_group_vk/{name_group}/posts_text.json", "r", encoding="utf-8") as file:
            data_posts = json.load(file)

            for post in data_posts:
                if not sending_active:  # Проверяем, если отправка отключена
                    return

                # Проверка постов на рекламные и на репосты (рекламу)
                if 'marked_as_ads' in post and post['marked_as_ads'] == 1:
                    print('ads')
                    print(post['text'])
                    continue  # Пропускаем рекламные посты
                elif 'copy_history' in post:
                    print('repost')
                    print(post['text'])
                    continue  # Пропускаем репосты
                elif 'is_pinned' in post and post['is_pinned'] == 1:
                    print('pin post')
                    continue  # Пропускаем закрепленные посты

                # Не рекламный пост
                post_text = post['text']
                post_id = post['id']

                # Проверяем, был ли этот пост уже отправлен
                if post_id in sent_posts or (post_text, post_id) in sent_texts:
                    print(f"Пост с ID {post_id} уже отправлен, пропускаем.")
                    continue  # Пропускаем дубликаты

                # Добавляем идентификатор поста и текст в множества
                sent_posts.add(post_id)
                sent_texts.add((post_text, post_id))



                if url_pattern.match(post_text):  # Если это ссылка
                    await bot.send_message(chat_id=CHANNEL_ID, text=post_text + '\n' + '👉 ' + f'<a href="{owner_post}">ПРОДАВЕЦ</a>',parse_mode='HTML')  # Отправляем текстом
                    continue  # Переходим к следующему посту

                post_text = post['text']
                if 'signer_id' in post:
                    owner_post = 'https://vk.com/id' + str(post['signer_id'])
                else:
                    print(post['id'])
                    owner_post = 'Анонимно'

                # Продолжаем с обычным постом
                owner_post = f'https://vk.com/id{post["signer_id"]}' if 'signer_id' in post else ''

                # Получаем фотографии из поста
                for photo in get_photo_file(post):
                    media.append(URLInputFile(photo))  # Добавляем фото в список

                if media:  # Если есть фотографии, отправляем альбом
                    caption = post_text + '\n' + '👉 ' + f'<a href="{owner_post}">ПРОДАВЕЦ</a>'

                    while True:
                        try:
                            # Подготовка списка медиа с подписью только для первой фотографии
                            media_group = []
                            for index, image in enumerate(media):
                                if index == 0:  # первая фотография с подписью
                                    media_group.append(InputMediaPhoto(media=image, caption=caption, parse_mode='HTML'))
                                else:  # остальные фотографии без подписи
                                    media_group.append(InputMediaPhoto(media=image))

                            # Отправка медиа-группы
                            await bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
                            media.clear()  # Очищаем список после отправки
                            break  # Успешная отправка, выходим из цикла
                        except aiogram.exceptions.TelegramRetryAfter as e:
                            print(f"Ошибка: {e}. Повторная попытка через {e.retry_after} секунд.")
                            await asyncio.sleep(e.retry_after)  # Ждем указанное время перед повторной попыткой
                        except Exception as e:
                            print(f"Произошла ошибка: {e}")

    # В конце функции, очистим media, если что-то осталось
    media.clear()  # Очищаем список после завершения
    await bot.send_message(chat_id=ID_CHAT_BOT,text='Все посты отправлены')

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global sending_active
    sending_active = True
    await message.answer('Отправка началась')
    await sending_posts()

@dp.message(Command("stop"))
async def cmd_start(message: types.Message):
    global sending_active
    sending_active = False
    await message.answer('Отправка остановлена')

async def maintg():
    await dp.start_polling(bot)