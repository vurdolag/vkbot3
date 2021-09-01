# -*- coding: utf-8 -*-
import random as rnd
import config
from untils import req, Event, Global, logs, get_proxy
from Sqlbd import Sqlbd
from Addon import Addon, middelware, addon_init
from Template import str_back, str_error
import asyncio
import ujson as json
import recompile as re
import deviantart
import time
from typing import Optional

keyb = ['⬅ Сменить%b', str_back]

keyb2 = ['🎨 Арт фото%b', '◼ Черно-белое%b',
         '❔ Что на фото%b', '✨ Текст в фото%b',
         '🙎 Лицо%b', '🌄 Случайный арт%b', str_back]

_help = (f'🎨 1. Арт фото - сделать из фото арт\n◼ 2. Черно-белое - фото в цветное'
         f'\n❔ 3. Что на фото - нейросеть скажет, что изображено на фото\n✨ 4. Текст в фото -'
         f' создаст фото по тексту.\n🙎 5. Лицо - нейросеть создаст уникальное лицо\n'
         f'🌄 6. Случайный арт - пришлет случайный арт или фото')

style = ['https://sun9-63.userapi.com/c854532/v854532039/19f963/GIbZ8bkq8JI.jpg',
         'https://sun9-54.userapi.com/c854532/v854532039/19f96d/hoDI11fi_mw.jpg',
         'https://sun9-63.userapi.com/c854532/v854532039/19f976/WHbJO5nIwkg.jpg',
         'https://sun9-57.userapi.com/c854532/v854532039/19f984/q87MmGhjdE0.jpg',
         'https://sun9-15.userapi.com/c854532/v854532039/19f98d/JGOgbRNbkYQ.jpg',
         'https://sun9-69.userapi.com/c854532/v854532039/19f996/ifywgGFJKpI.jpg',
         'https://sun9-48.userapi.com/c854532/v854532039/19f9a0/kUpiXzXsdUw.jpg',
         'https://sun9-9.userapi.com/c854532/v854532039/19f9aa/1Gc-U7-LeRE.jpg',
         'https://sun9-34.userapi.com/c854532/v854532039/19f9b2/ZGYk_3FiiCM.jpg']


def get_token_deviantart() -> str:
    return deviantart.Api(config.deviantart_id, config.deviantart_secret).access_token


class AuthDeviantart:
    token_deviantart = get_token_deviantart()


devart = AuthDeviantart()

_BD = Sqlbd('cache_art')


@addon_init(["!ФОТО АРТ", '!АРТ'], '🎨', True, 2)
class Img(Addon):
    __slots__ = ('old_photo', 'count', 'offset', 'timer', 'search', 'token')

    def __init__(self, username, user_id):
        super(Img, self).__init__(username, user_id)
        self.lock = 5
        self.old_photo = ''
        self.count = rnd.randint(0, len(style) - 1)
        self.offset = 0
        self.timer = int(time.time())
        self.search = ['', '']
        self.token = devart

    def counter(self) -> int:
        a = self.count
        self.count += 1
        return a % len(style)

    async def nero(self, mode: str, params, event: Event):
        if not event.from_comment:
            await event.answer('Обрабатываю запрос... ⌛').send(nonkeyb=True)
            event.set_typing()

        url = f"https://api.deepai.org/api/{mode}"
        headers = {'api-key': config.deepai}
        try:
            response = await req.post(url, data=params, headers=headers, timeout=300)
            response = json.loads(response.decode('utf-8'))
            try:
                return await event.uploads(response['output_url'])
            except:
                try:
                    return response['output']
                except:
                    return ''

        except:
            logs()
            return ''

    async def get_face(self, event: Event) -> Event:
        event.is_can_edit_prev_msg = False
        event.set_typing()
        url = "https://thispersondoesnotexist.com/image"
        headers = {'User-Agent': 'My User Agent 1.0'}
        try:
            response = await req.get(url, headers=headers, proxy=get_proxy())
            return await event.uploads(response)

        except:
            logs()
            return event.answer(str_error)

    async def cache_art(self, event: Event, id_art, link, short_link, caption=''):
        await asyncio.sleep(2 + rnd.random() * 3)
        if not event.from_comment:
            event.from_comment = True
            await event.uploads(link, caption=caption)
        atta = event.attachments_out
        if atta:
            await _BD.put(id_art, atta[0], short_link)
            await asyncio.sleep(rnd.random() * 30 + 30)
            owner_id = rnd.choice(config.group_for_post)
            Global.start_task(event.social.create_post(owner_id, event.text, atta))
        return True

    async def get_art(self, q='', event: Event = None):
        event.is_can_edit_prev_msg = False
        event.set_typing()
        for _ in range(5):
            if int(time.time()) - self.timer > 3600 * 24:
                self.offset = 0
                self.search[1] = ''
                self.timer = int(time.time())

            if q and q != self.search[0]:
                self.search[0] = q
                self.search[1] = await event.translate(q, 'ru-en')
                self.offset = 0

            cont = []
            params = {'limit': 5,
                      'offset': self.offset,
                      'q': self.search[1],
                      'timerange': '1month',
                      'access_token': self.token.token_deviantart}

            url = 'https://www.deviantart.com/api/v1/oauth2/browse/popular'
            try:
                res = await req.get(url, params=params)
                response = json.loads(res).get('results')

                if response:
                    for i in response:
                        try:
                            cont.append([i['preview']['src'], i['content']['src'],
                                         i['content']['width'], i['content']['height']])
                        except KeyError:
                            pass

                self.offset += 5
                if cont:
                    out = rnd.choice(cont)
                    id_art = out[0].split('?')[0].split('/f/')[-1].split('/v1/fill')[0]
                    id_art = ('telegram' if event.from_telegram else '') + re.img1.sub('', id_art)
                    ans = await _BD.get_all(key='id_art', val=id_art)
                    if ans:
                        ans = ans[0]
                        return event.answer(ans[2]).attachment(ans[1])

                    else:
                        short_link = await event.get_short_link(out[1])
                        short_link = f'Cсыль на ориг - {short_link} {out[2]}X{out[3]} pix'
                        await event.answer(short_link if not event.from_telegram else '').uploads(out[0])
                        if not event.from_telegram:
                            Global.start_task(self.cache_art(event, id_art, out[0], short_link,
                                                             caption=self.search[0]))
                        return event

                else:
                    img = await event.search_img(self.search[1])
                    if img:
                        return event.attachment(rnd.choice(img))

                return event.answer('Ничего подходящего не нашел, попробуй поменять запрос.')
            except KeyError:
                pass
            except:
                logs()
                self.token.token_deviantart = get_token_deviantart()

        return event.answer(str_error)

    def end(self, event: Optional[Event] = None):
        self.step = 0
        self.old_photo = ''

    def choose_module(self, event: Event):
        if event.check('1', 'АРТ ФОТО'):
            self.setstep(2)
            return event.answer('Пришли фотку и я наложу случайный эффект 🖼'
                                '\n\n♨ Свой фильтр\n⬅ Сменить - другая функция.'
                                ).keyboard('♨ Свой фильтр%b', *keyb)

        elif event.check('2', 'ЧЕРНО-БЕЛОЕ', 'ЧЕРНОБЕЛОЕ'):
            self.setstep(3)
            return event.answer('Пришли черно-белую фотографию и я сделаю её цветной'
                                '\n\n⬅ Сменить - другая функция.')

        elif event.check('3', 'ЧТО НА ФОТО'):
            self.setstep(4)
            return event.answer('Пришли фотографию и я скажу что на ней изображено, но это не точно ☺'
                                '\n\n⬅ Сменить - другая функция.')

        elif event.check('4', 'ТЕКСТ В ФОТО'):
            self.setstep(5)
            return event.answer('Напиши любой текст и я сгенерирую '
                                'по нему фото (но может получится очень крипово)'
                                '\n\n⬅ Сменить - другая функция.')

        elif event.check('5', 'ЛИЦО'):
            self.setstep(6)

        elif event.check('6', 'СЛУЧАЙНЫЙ АРТ'):
            self.setstep(7)

        elif self.isstep(1):
            return event.answer('Введи число, номер функции')

        return None

    @middelware
    async def mainapp(self, event: Event) -> Event:
        rnd.shuffle(style)

        if event.check('СБРОСИТЬ ПОИСК'):
            self.search = ['', '']
            return event.answer('Поиск арт фото сброшен.\n\n'
                                'Напиши новый запрос или жми кнопку - ⏩ Ещё арт').keyboard('⏩ Ещё арт%b', *keyb)

        if event.check('СВОЙ ФИЛЬТР') and self.isstep(2):
            return event.answer('Пришли 2 фотки, первая фотка на которой нужно применить эффект, вторая '
                                'фоткая твоего стиля, например картина или арт.'
                                '\n\n⬅ Сменить - другая функция.'
                                ).keyboard(*keyb)

        if event.check('!СМЕНИТЬ', 'СМЕНИТЬ') and self.step >= 1:
            self.setstep(1)
            self.old_photo = ''
            return event.answer(_help).keyboard(*keyb2)

        if self.isstep(0, 1):
            return event.answer(f'Как обработать фото?\n\n{_help}').keyboard(*keyb2)

        event.keyboard(*keyb)

        if self.step > 0 and self.choose_module(event):  # выбор модуля
            return event

        if event.attachments:
            url_photo = await event.get_photo()
            self.old_photo = url_photo
        else:
            url_photo = self.old_photo

        if self.isstep(2):
            if len(url_photo) == 2:
                params = {'content': url_photo[0],
                          'style': url_photo[1]}
                await self.nero('CNNMRF', params, event)
                if event.attachments_out:
                    return event.answer('Пришли ещё фотки.\n⬅ Сменить - другая функция.')
                else:
                    return event.answer(str_error)

            elif len(url_photo) == 1:
                params = {'content': url_photo[0],
                          'style': style[self.counter()]}
                await self.nero('CNNMRF', params, event)
                if event.attachments_out:
                    return event.answer('Пришли ещё фотку'
                                        '\n🔄 Другой фильтр'
                                        '\n♨ Свой фильтр'
                                        '\n⬅ Сменить - другая функция.'
                                        ).keyboard('🔄 Другой фильтр%b', '♨ Свой фильтр%b', *keyb)
                else:
                    return event.answer(str_error)
            else:
                return event.answer('Нужно 1 или 2 фото если ты используешь свой фильтр')

        if self.isstep(3):
            if len(url_photo) == 1:
                params = {'image': url_photo[0]}
                await self.nero('colorizer', params, event)

                if event.attachments_out:
                    return event.answer('\nПришли ещё фотку.\n⬅ Сменить - другая функция.')
                else:
                    return event.answer(str_error)
            else:
                return event.answer('Нужно фото')

        if self.isstep(4):
            if url_photo:
                params = {'image': url_photo[0]}

                res = await self.nero('neuraltalk', params, event)
                if res:
                    return event.answer('Держи:\n\n' + await event.translate(res, 'ru-en'))
                else:
                    return event.answer(str_error)
            else:
                return event.answer('Это не фотка')

        if self.isstep(5):
            params = {'text': await event.translate(event.text, 'ru-en')}
            await self.nero('text2img', params, event)

            if event.attachments_out:
                return event.answer('\nНапиши ещё сообщение.\n⬅ Сменить - другая функция.')
            else:
                return event.answer(str_error)

        if self.isstep(6):
            event.is_can_edit_prev_msg = False
            await event.answer('Создаю лицо, жди... ⌛').send(nonkeyb=True)
            await self.get_face(event)
            event.is_can_edit_prev_msg = True
            if event.attachments_out:
                return event.answer('Держи.'
                                    '\n⏩ Ещё лицо - новое лицо.'
                                    '\n⬅ Сменить - другая функция.'
                                    ).keyboard('⏩ Ещё лицо%b', *keyb)
            else:
                return event.answer(str_error)

        if self.isstep(7):
            txt = re.space.sub(' ', re.img2.sub('', event.text.lower())).strip()

            await self.get_art(txt, event)
            if event.attachments_out:
                h = keyb
                d = ''
                a = '\n⏩ Ещё арт - новый арт.'

                if self.search[1]:
                    h = keyb + ['Сбросить поиск%b']
                    d = '\n🔀 Сбросить поиск'
                    a = f'\n⏩ Ещё арт - "{self.search[0]}"'

                return event.answer_add('\nНапиши что ищешь.'
                                        f'{a}'
                                        f'\n⬅ Сменить - другая функция.{d}'
                                        ).keyboard('⏩ Ещё арт%b', *h)
            else:
                return event

        self.setstep(1)
        return event.answer(f'Как обработать фото?\n\n{_help}').keyboard(*keyb2)
