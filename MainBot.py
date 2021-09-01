# -*- coding: utf8 -*-
import asyncio
import time
import random
from untils import logs, until, Event, smart_re, Global, async_timer, smart_re_tuple
from Sqlbd import Sqlbd
from Addon import Addon, addon_dict, addon_load
from addons.admin.admin import admin
import config
from addons.simple_answer import Simple
from Models import UserDataBD
from typing import Optional, Dict, List
import re

addon_load()

from addons.menu import Menu


key_back = '⬅ !Назад'

_allcommand = ['помощь', '!помощь', '!игры', '!развлечения', '!полезное', key_back]
for i in addon_dict.values():
    _allcommand += i[0]

smile = ['😭', '😢', '😰', '😲', '😬', '😖', '😓', '🤕', '🤧']
EVENT = Optional[Event]

bd_mail = Sqlbd('mail')
bd_userdata = Sqlbd('userdata', UserDataBD)
bd_msg = Sqlbd('message')
bd_reviews = Sqlbd('reviews')


def event_processing(_):
    @async_timer
    async def wrapper(cls, event: Event) -> Event:
        ids = event.ids()

        if len(event) > 30 or event.from_telegram:
            await bd_msg.put(ids, time.time(), event.text)

        if ids not in Global.user:  # запрос инфо о пользователе
            print('Новый юзер', ids)
            first_message = -1
            try:
                user_info: List[UserDataBD] = await bd_userdata.get(event.user_id)
                if user_info:
                    first_message = 0
                else:
                    user_info = await event.save_user_info()
                    await bd_mail.delete(f"id = {event.user_id} and id_group = {event.group_id}")

                info = user_info[0]
                bot = cls(info.id, info.fname, info.gender)

            except:
                bot = cls(event.user_id, 'user_name', 1)
                logs.event_processing()

            bot.first_message = first_message
            Global.user[ids] = bot

        else:
            bot = Global.user[ids]

        try:
            await bot.event_route(event)  # отправка в обработчик
            await event.send()  # отправка результата

        except:
            await event.answer(f"Упс... ошибка {random.choice(smile)}").send()
            logs.event_processing()
            
        return event
    return wrapper


class Bot:
    __slots__ = (
        'user_id', 'user_name', 'first_message', 'active_addon',
        'lock', 'sex', 'menu', 'ban', 'reviews', 'int_to_command', 'simple')

    def __init__(self, user_id=0, username='username', sex=0):
        logs.log(f"Создан объект бота! {username} {user_id}")
        self.user_id: int = user_id
        self.user_name: str = username
        self.first_message: int = -1
        self.active_addon: Optional[Addon] = None
        self.sex: int = sex
        self.menu: Menu = Menu()
        self.ban: int = 0
        self.reviews: bool = False
        self.int_to_command: Dict[int, str] = {0: '!помощь'}
        self.simple: Simple = Simple(self)

    def __getattr__(self, item):
        return self.fast_addon(item)

    @classmethod
    @event_processing
    async def route(cls, event):
        pass

    def reset(self):
        self.active_addon = None

    def checker(self, msg: str) -> str:
        text = msg.upper()
        if 18 > len(text) > 4 and text not in _allcommand:
            for i in _allcommand:
                if i[0] == text[0] and len(i) > 3:
                    if until.distance(i, text) <= 2:
                        msg = i
        return msg

    def preparation(self, event: Event) -> str:
        event.sex = self.sex

        if self.first_message < 1:
            if self.first_message == -1:
                asyncio.create_task(self.wait_hello(event))
            self.first_message += 1

        message = ''
        if event.from_comment:
            self.reset()
        else:
            if not event.time_send:
                event.keyboard()
            message = re.sub(r'[^\w\d\-! ]', '', event.text.lower()).strip()

        message = self.checker(message)
        if self.int_to_command:
            try:
                message = self.int_to_command.get(int(message), '!помощь')
            except:
                pass
            self.int_to_command = {}

        if (message in _allcommand
                and self.active_addon
                and (self.active_addon.step != self.active_addon.lock)):
            self.reset()

        return message

    def RE(self, string: str, event: Event, lock=True, del_pat=False) -> bool:
        if (not self.active_addon or event.time_send or not lock) and smart_re(
                string).search(event.text.lower()):
            if del_pat:
                event.text = event.re_del(string, event.text).text
            return True
        else:
            return False

    def ex_match(self, msg: str, *lst: str, lock=True) -> bool:
        tmp = not self.active_addon if lock else True
        b = smart_re_tuple(lst, full=True).search(msg.lower())
        return b and tmp

    def fast_addon(self, key: str):
        key = key.upper()
        addon_list = addon_dict.get(key)

        if addon_list is None or len(addon_list) != 6:
            raise Exception(f"Error key '{key}'")
        else:
            return addon_list[2](self.user_name, self.user_id)

    def review(self, event: Event, message: str):
        if self.reviews and message not in _allcommand:
            self.reviews = False
            if not event.check('не хочу', 'назад', 'стоп', 'нет'):
                bd_reviews.put(event.group_id, self.user_id, int(time.time()), event.text, sync=True)

                return event.answer('Спасибо за отзыв! 😊').keyboard()

            else:
                return event.answer('Ну ладно 😎').keyboard()
        else:
            self.reviews = False
            return False

    def first_message_(self, event: Event) -> Event:
        m = "\n🎨 !Фото Арт\n📢 !Озвучь текст\n🗣 !Анонимный чат\n🌠 !Гороскоп\n⚙ !Меню"
        h = "" if event.support_keyb_inline else m
        return event.answer(f'Привет, {self.user_name}! 😉\n\nЧто выберешь?{h}'
                            ).keyboard('🎨 !Фото Арт%b', '📢 !Озвучь текст%b', '🗣 !Анонимный чат%b',
                                       '🌠 !Гороскоп%b', '⚙ !Меню%g', tablet=1)

    def hello(self, event: Event) -> Event:
        if self.first_message > 2:
            return event.answer("Хе хе заровались же 😆").keyboard()
        else:
            self.first_message += 1
            return event.answer("Привет! 😊").keyboard()

    def help(self, event: Event, message='', add=False, now=False) -> Event:
        return self.menu.mainapp(message, event, self, add, now)

    async def audio_msg(self, event):
        if event.attachments_type == 'audio_message' and not event.text:
            atta = event.attachments[0]['audio_message']['link_ogg']
            event.text = await event.voice_to_text(atta)
            event.audio_msg = event.text
            logs(f'audio mgs => {event.text}')
            print('audio mgs =>', event.text)

    async def wait_hello(self, event: Event) -> bool:
        await asyncio.sleep(60 * 60)
        if self.first_message != 0 or not event.support_keyb or not await event.messages_allowed():
            return False
        else:
            await event.answer('Ну ладно как хочешь, если что смотри '
                               'мои команды здесь https://vk.com/@kreo_0-komandy-bota'
                               ).keyboard('🎨 !Фото Арт%b', '📢 !Озвучь текст%b',
                                          '🗣 !Анонимный чат%b', '🌠 !Гороскоп%b',
                                          '⚙ !Меню%g', tablet=1).send()
            return True

    async def addon_route(self, message: str, event: Event, addons: dict) -> Event:
        if self.active_addon and self.active_addon.step == 0:
            self.reset()

        if not self.active_addon:
            for addon in addons.values():
                if smart_re_tuple(addon[0], full=True).findall(message.lower()):
                    self.active_addon = addon[2](self.user_name, self.user_id)
                    break

        if self.active_addon:
            await self.active_addon.mainapp(event)
            if event.is_stop:
                self.reset()
                self.help(event, message=self.menu.step, add=True)
            return event

    async def event_route(self, event: Event) -> Event:
        await self.audio_msg(event)
        message = self.preparation(event)

        if await self.simple.api(event):
            return event

        if not event.from_chat and not event.from_comment and not self.RE(r'^\?', event, lock=False):
            if event.user_id in config.admin and self.RE(r'!админ', event) and await admin(event):
                return event

            if self.simple.first(event):
                return event

            if self.help(event, message):
                return event

            # -----------------------
            if not event.time_send and await self.addon_route(message, event, addon_dict):
                return event
            # ----------------------

            if self.review(event, message):
                return event

            if self.first_message == 0:
                return self.first_message_(event)

        if await self.simple.addon(event):  # простой ответ с логикой или быстрые команды
            return event

        if self.simple.answer(event):  # простой вопрос ответ
            return event

        if await self.simple.end(event):
            return event
