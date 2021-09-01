# -*- coding: utf-8 -*-
import random as rnd
import pickle
import orjson as json
import asyncio
from Template import str_back
from untils import req, until, Event
from Sqlbd import Sqlbd
from Addon import Addon, middelware, addon_init


_p1 = '🔍 Поиск гифки%b'

keyb = [str_back]
keyb2 = [_p1, '⭐ Случайная гифка%b', '😜 Гиф эмоции']
keyb3 = ['➡ Ещё%b', _p1]

with open('addons/gif/gif_post', 'rb') as f:
    gif_post = pickle.load(f, encoding="bytes")

_rnd_doc = ['doc-30688695_534588958',
            'doc-30688695_534588679',
            'doc370862629_584672902',
            'doc473068630_499674952',
            'doc321511581_564219945',
            'doc2773139_548999789']

_msg1 = 'Напиши новый запрос или\n➡ Ещё - гифка по запросу "{}"'
_msg2 = '\n\n🔍 Поиск гифки\n⭐ Случайная гифка\n😜 Гиф эмоции'
_msg3 = '{}, я могу найти для тебя гифку! 😉{}'
_msg4 = 'Что выберешь?{}'
_msg5 = 'Напиши что ищешь?'
_msg6 = 'Выбери "поиск гифки" или "случайная гифка"'


_BD = Sqlbd('cache_gif')


@addon_init(['!ГИФКА', 'ГИФ', 'GIF', 'ГИФКУ'], '🔍', True, 2)
class Gif(Addon):
    __slots__ = ('gif_in_eng', 'search', 'first', 'cursor', 'index_gif', 'content')

    def __init__(self, username, user_id):
        super(Gif, self).__init__(username, user_id)
        self.lock = 3
        self.gif_in_eng = 0
        self.search = ''
        self.first = self.set_condition(self.user_id, 'gif_first', 1, False, 0)
        self.cursor = ''
        self.index_gif = -1
        self.content = []

    def get_gif(self):
        return rnd.choice(gif_post)

    async def cache(self, event, gif_id, link):
        await asyncio.sleep(15)
        if not event.from_comment:
            event.from_comment = True
            await event.uploads(link)
        atta = event.attachments_out
        if atta:
            await _BD.put(gif_id, atta[0])
        return True

    async def seach_gif(self, event: Event) -> Event:
        event.is_can_edit_prev_msg = False
        event.set_typing()
        apikey = "ZX9BSI8PKQSA"
        lmt = 30
        try:
            url = f"https://api.tenor.com/v1/search?key={apikey}&q={event.text}&limit={lmt}"
            res = await req.get(url)

            try:
                all_gif = [i['media'][0]['mediumgif']['url']
                           for i in json.loads(res)["results"]]
            except KeyError:
                all_gif = []

            if all_gif:
                choices = rnd.choice(all_gif)
                gif_id = ('telegram' if event.from_telegram else '') + choices.split('/')[-2]
                ans = await _BD.get_all(key='gif_id', val=gif_id)
                if ans and ans[0]:
                    ans = ans[0][1]
                    return event.attachment(ans)

                await event.uploads(choices)
                if not event.from_telegram:
                    asyncio.create_task(self.cache(event, gif_id, choices))
                return event

            else:
                gifs = await event.search_doc()
                assert gifs
                return event.attachment(rnd.choice(gifs))

        except:
            out = None
            if self.gif_in_eng == 0:
                self.gif_in_eng = 1
                event.text = await until.translate(event.text, 'ru-en')
                print(event.text)
                out = await self.seach_gif(event)
                self.gif_in_eng = 0

            if not out:
                event.answer('Ничего не нашел(')
                return event.attachment(rnd.choice(_rnd_doc))
            return out

    async def get_gif_emotion(self, event, new_seach=False):
        event.is_can_edit_prev_msg = False
        await event.answer('Ищу гифки, жди... 🔎').send(nonkeyb=True)
        event.is_can_edit_prev_msg = True

        event.set_typing()

        if self.index_gif > 8 or new_seach:
            self.index_gif = 0
            url = 'https://api.gfycat.com/v1/gfycats/search'
            params = {'search_text': event.text,
                      'locale': 'ru-RU',
                      'cursor': self.cursor}

            res = await req.get(url, params=params)
            response = json.loads(res)

            self.cursor = response.get("cursor", "")
            response = response.get("gfycats", [])

            content = [i.get("max5mbGif", "") for i in response]

            self.content = content
            content = content[:3]
            self.index_gif += 3

        else:
            content = self.content[self.index_gif:self.index_gif+3]
            self.index_gif += 3

        await event.uploads(content)
        return event

    def ret(self, event: Event):
        if not event.text_out:
            return event.answer(_msg1, self.search).keyboard('➡ Ещё%b', '⭐ Случайная гифка%b', *keyb)
        else:
            return event.keyboard('⭐ Случайная гифка%b', *keyb)

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if event.from_comment:
            event.text = ' '.join(event.text.split()[1:])
            return await self.seach_gif(event)

        if self.isstep(0, 1):
            h = '' if event.support_keyb_inline else _msg2
            if self.first == 0:
                self.first = 1
                return event.answer(_msg3, self.username, h).keyboard(*keyb2, *keyb, tablet=1)
            else:
                return event.answer(_msg4, h).keyboard(*keyb2, *keyb, tablet=1)

        if event.check('ПОИСК ГИФОК', 'ПОИСК', '🔍 ПОИСК ГИФКИ', 'НАЙТИ', 'ПОИСК ГИФКИ'):
            self.setstep(3)
            return event.answer(_msg5).keyboard(*keyb)

        if event.check('СЛУЧАЙНАЯ ГИФКА', 'ГИФКА'):
            self.setstep(2)
            event.keyboard(*keyb3, *keyb)

            if event.from_telegram:
                return event.answer(f'https://vk.com/{self.get_gif()}')
            else:
                return event.answer('Держи').attachment(self.get_gif())

        if event.check('ГИФ ЭМОЦИИ'):
            self.cursor = ''
            self.setstep(4)
            return event.answer(_msg5).keyboard(*keyb)

        if self.isstep(1):
            return event.answer(_msg6).keyboard(*keyb2, *keyb)

        if self.isstep(2):
            if event.check('еще', 'ещё'):
                event.keyboard(*keyb3, *keyb)
                if event.from_telegram:
                    return event.answer(f'https://vk.com/{self.get_gif()}')
                else:
                    return event.answer('Держи').attachment(self.get_gif())

        if self.isstep(3):
            if event.check('еще', 'ещё'):
                event.text = self.search
                await self.seach_gif(event)
                return self.ret(event)

            self.search = event.text
            await self.seach_gif(event)
            return self.ret(event)

        if self.isstep(4):
            if event.check('еще', 'ещё'):
                event.text = self.search
                await self.get_gif_emotion(event)
                return self.ret(event)

            self.search = event.text
            self.cursor = ''
            await self.get_gif_emotion(event, new_seach=True)
            return self.ret(event)





