# coding: utf-8
from datetime import datetime
import logging
import random

import pytz
import requests

# from telegram.ext import BaseFilter, Filters, MessageHandler
from telegram.ext import CommandHandler
from telegram import ChatAction

log = logging.getLogger()
TZ = pytz.timezone('Asia/Shanghai')


def random_san_meme():
    return random.choice((
        '姝雅大小姐已经歇了。',
        '什么？姝雅女神居然不在',
        '姝雅再不播我就要死了。',
        '姝雅不在，滚！',
        '姝雅小姐姐又去哪里摸鱼了。',
        '你能表演一下那个吗？',
        '亲爱的姝雅每天都会直播。',
        '别问了，姝雅没直播。',
    ))


def random_san_nick():
    return random.choice((
        '姝雅',
        '姝雅女神',
        '姝雅小姐姐',
        '姝雅大小姐',
        '姝雅女王',
        '小伞',
        '大胸伞',
    ))


def is_san_live(live):
    if live['error']:
        text = '好神秘啊，怕不是进错房间了？'
    else:
        live = live['data']
        san_live_url = 'http://douyu.com/1903971'
        if live['room_status'] == '1':
            text = (
                '么么哒，{}正在直播~'
                '而且有{}个色狼在看直播，整个房间都污污的。 {}'
            ).format(random_san_nick(), live['online'], san_live_url)
        elif live['room_status'] == '2':
            now = TZ.normalize(datetime.utcnow().replace(tzinfo=pytz.utc))
            last_live = TZ.localize(datetime.strptime(live['start_time'], '%Y-%m-%d %H:%M'))
            rest_duration = now - last_live
            # Rested for less than one day
            if rest_duration.days == 0:
                text = '刚刚播完，让{}歇一歇吧，不要猝死在直播间。'.format(random_san_nick())
            else:
                text = '{}已经摸了 {} 天 {} 小时 {} 分钟了。\n{}'.format(
                    random_san_nick(),
                    rest_duration.days,
                    rest_duration.seconds // 3600,
                    rest_duration.seconds % 3600 // 60,
                    random_san_meme()
                )
        else:
            text = '斗鱼怎么了，简直说不出话。'

    return text


def check_san_live(bot, update):
    bot.sendChatAction(
        chat_id=update.message.chat_id, action=ChatAction.TYPING
    )
    api_url = 'http://open.douyucdn.cn/api/RoomApi/room/1903971'
    try:
        data = requests.get(
            api_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',  # noqa
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,ja-JP;q=0.8,ja;q=0.6,zh-CN;q=0.4,zh;q=0.2,en;q=0.2',
                'DNT': '1',
                'Host': 'open.douyucdn.cn',
                'Upgrade-Insecure-Requests': '1',
            },
            timeout=5
        ).json()
    except requests.RequestException as e:
        return update.message.reply_text('出事儿啦！{}'.format(e.message), quote=True)
    else:
        text = is_san_live(data)
        update.message.reply_text(text, quote=True)


san_live_handler = CommandHandler('live', check_san_live)
