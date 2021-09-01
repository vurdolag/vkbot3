# -*- coding: utf-8 -*-
from untils import req, Event, Global
from Sqlbd import Sqlbd
from Addon import Addon, middelware, addon_init
from Template import str_back
from asyncio import sleep, create_task
import re
from PIL import Image, ImageFilter
from io import BytesIO
import random as rnd

str_wait = '!Ждать%b'

keyb = [str_back]
keyb2 = ['!Старт%b', str_wait, '!Правила%b', str_back]
keyb3 = ['!Стоп%b', '!Блокировать%r']

with open('addons/chat/bad.txt', 'r', encoding='utf-8') as f:
    _bad_word = f.readline()

bad_word = "|".join(_bad_word.lower().split(', '))


class Chats:
    available_user = {}  # id_user : [ban_list,]
    in_chat = {}  # id_user: id_user

    __slots__ = ()


_msg1 = 'Собеседник отключился ❌\nВыбери !Старт или !Ждать'
_msg2 = '💬 К вам подключился собеседник, можете общаться!\n!стоп — остановить диалог'
_msg3 = '💬 Подключились к анонимному собеседнику теперь можете общаться!\n!стоп — остановить диалог'
_msg4 = '❌ Нет подходящих собеседников, попробуйте подождать 🙃 \nНажмите кнопку !Ждать'
_msg5 = 'Бот:\nВ этом чате можно отправлять только текстовые сообщения и фотографии.'
_msg6 = 'Упс... собеседник запретил отправлять ему сообщения(((\nВыбери !Старт или !Ждать'
_msg7 = 'Ожидают общения: {}\nАктивных чатов: {}\n\nЗдесь можно анонимно общаться.\nЧтобы начать - !Старт'
_msg8 = 'Ожидают общения: {}\n'
_msg9 = 'Собеседник добавил вас в черный список'
_msg10 = 'Собеседник добавлен в ЧС'
_msg11 = ('Правила:\nЗапрещены оскорбления, любые ссылки, фото неприемлемого содержания. Работает мат '
          'фильтр и фильтр фото(неприемлимые фото будут замыливаться).')
_msg12 = 'Сейчас нету доступных собеседников\nЖдем собеседника...'
_msg13 = 'Ждем собеседника 🙃'
_msg14 = 'Команды:\n!Старт - для начала чата\n!Ждать - для поиска собеседника\n!Назад - выйти в меню бота'


_BD = Sqlbd('chat')


@addon_init(['!анонимный чат', '!чат'], '🗣', False, 2)
class Chat(Addon):
    __slots__ = 'lock', 'ban_list', 'already_chat', 'filter_bad_word'

    def __init__(self, username, user_id):
        super(Chat, self).__init__(username, user_id)
        self.lock = 2
        self.ban_list = []
        self.already_chat = []
        self.filter_bad_word = True

    async def get_bd(self) -> list:
        ans = await _BD.get(self.user_id, 'id_block')
        return [i[0] for i in ans] if ans else [1]

    async def disconector(self, event: Event, msg=_msg1):
        if Chats.in_chat.get(event.ids(), 0):
            x = Chats.in_chat[event.ids()]
            p = x.split('_')
            if msg:
                await event.answer(msg).keyboard(*keyb2).send(peer_id=p[-1], group=p[0])

            self.already_chat.append(x)
            if Chats.in_chat.get(x):
                del Chats.in_chat[x]
            if Chats.in_chat.get(event.ids()):
                del Chats.in_chat[event.ids()]

    async def conector(self, event: Event) -> Event:
        key = list(Chats.available_user.keys())
        rnd.shuffle(key)
        for user in key:
            ban = Chats.available_user[user] + self.ban_list
            if user != event.ids() and event.ids(
            ) not in ban and user not in ban and not Chats.in_chat.get(user, 0):
                Chats.in_chat[event.ids()] = user
                Chats.in_chat[user] = event.ids()
                del Chats.available_user[user]
                event.keyboard(*keyb3)

                p = user.split('_')
                await event.answer(_msg2).send(peer_id=p[-1], group=p[0])
                await sleep(0.1)
                return event.answer(_msg3)

        return event.answer(_msg4).keyboard(str_wait, str_back)

    async def attachment_conv(self, event: Event, imgs: list) -> Event:
        img_temp = []
        for i in imgs:
            img = await req.get(i)
            res = await event.moderation_img(img)
            await sleep(0.3)
            # print(res)
            if res.get('adult', 0) > 0.9 or res.get('gruesome', 0) > 0.9:
                im = Image.open(BytesIO(img))
                im = im.filter(ImageFilter.GaussianBlur(30))
                stream = BytesIO()
                im.save(stream, format="JPEG", quality=75)
                stream.seek(0)
                i = stream.read()

            img_temp.append(i)

        await event.uploads(img_temp, telegram=True)
        return event

    async def sender(self, event: Event) -> Event:
        p = Chats.in_chat.get(event.ids(), 0).split('_')
        imgs = ''
        if event.attachments:
            if event.attachments_type == 'photo':
                imgs = await event.get_photo()

            else:
                return event.answer(_msg5).keyboard(*keyb3)

        peer_id_new = int(p[-1])
        group_id_new = int(p[0])

        peer_id_old = event.peer_id
        group_id_old = event.group_id

        event.user_id = peer_id_new
        event.peer_id = peer_id_new
        event.group_id = group_id_new
        event.social = Global.social_tmp[group_id_new]

        event.set_typing(peer_id_new)

        if not await event.messages_allowed(peer_id_new, group_id_new):
            await self.disconector(event, '')
            await event.answer(_msg6).keyboard(*keyb2).send(peer_id=peer_id_old, group=group_id_old)
            return event.answer('')

        event.answer(re.sub(bad_word, '*censored*', event.text, flags=re.IGNORECASE)
                     if self.filter_bad_word
                     else event.text)

        if event.attachments_type == 'photo':
            await self.attachment_conv(event, imgs)

        if event.from_telegram:
            event.from_telegram = False

        return event.keyboard(*keyb3)

    def set_event(self, event: Event):
        event.support_keyb_inline = False
        event.keyb_one_time = True
        event.support_callback = False
        event.from_callback_button = False

    def end(self, event: Event = None):
        self.step = 0
        create_task(self.disconector(event))
        if Chats.available_user.get(event.ids()):
            del Chats.available_user[event.ids()]

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if not self.ban_list:
            self.ban_list = await self.get_bd()

        self.set_event(event)

        if self.isstep(2) and not Chats.in_chat.get(event.ids()):
            self.setstep(1)

        if self.isstep(0, 1):
            return event.answer(_msg7,
                                len(Chats.available_user),
                                len(Chats.in_chat)
                                ).keyboard(*keyb2)

        if event.check('!закончить', '!стоп'):
            self.setstep(1)
            await self.disconector(event)
            return event.answer(_msg8, len(Chats.available_user)).keyboard(*keyb2)

        if event.check('!в черный список', '!блокировать', '!блок', '!чс'):
            self.setstep(1)
            x = Chats.in_chat.get(event.ids(), 0)
            self.ban_list.append(x)
            await _BD.put(event.ids(), x)
            await _BD.put(x, event.ids())
            await self.disconector(event, _msg9)
            return event.answer(_msg10).keyboard(*keyb2)

        if event.check('!правила'):
            return event.answer(_msg11).keyboard(*keyb2)

        if event.check('!подключиться', '!старт', '!начать'):
            if self.isstep(2):
                await self.disconector(event)

            self.setstep(2)
            if len(Chats.available_user) != 0:
                return await self.conector(event)

            else:
                Chats.available_user[event.ids()] = self.ban_list
                return event.answer(_msg12).keyboard(*keyb2)

        if event.check('!ожидать', '!ждать', '!искать'):
            if self.isstep(2):
                await self.disconector(event)

            self.setstep(2)
            Chats.available_user[event.ids()] = self.ban_list
            return event.answer(_msg13).keyboard('!Старт%b', *keyb)

        if self.step > 1:
            return await self.sender(event)

        return event.answer(_msg14).keyboard(*keyb2)
