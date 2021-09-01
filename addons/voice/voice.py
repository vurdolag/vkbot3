# -*- coding: utf-8 -*-
from fake_useragent import UserAgent
from Addon import Addon, middelware, addon_init
from Template import str_back, str_yes, str_error

from untils import req, Event, logs, get_proxy

import random as rnd
import recompile as rec
import config
from aiohttp import ClientSession

speak = {1: 'ermilov',
         2: 'levitan',
         3: 'zahar',
         4: 'silaerkan',
         5: 'oksana',
         6: 'kolya',
         7: 'kostya',
         8: 'nastya',
         9: 'sasha',
         10: 'nick'}


keyb = [
    #'🗣 Голос%b',
    #'💥 Эмоции%b',
    str_back]
keyb2 = [str_yes, 'Ещё пример%b', str_back]
keybemo = ['😉 Обычный%b', '😃 Добрый%g', '😡 Злой%r', str_back]

tmp = ''
for i in speak:
    tmp += '\n' + str(i) + '. ' + speak[i]


NotWork = 0
Start = 1
Emotion = 20
EmotionEdit = 21
VoiceChange = 10


@addon_init(['!ОЗВУЧЬ ТЕКСТ', '!ОЗВУЧЬ', '!ОЗВУЧ', '!ОЗВ'], '📢', True, 2)
class Voice(Addon):
    __slots__ = 'emotion', 'speaker', 'first'

    def __init__(self, username, user_id):
        super(Voice, self).__init__(username, user_id)
        self.lock = 1
        self.emotion = self.set_condition(self.user_id, 'voice_emotion', 'neutral', False)
        self.speaker = self.set_condition(self.user_id, 'voice_speaker', 'random', False)
        self.first = self.set_condition(self.user_id, 'voice_first', 1, False, 0)

    def head(self) -> dict:
        user_ag = UserAgent().chrome
        return {
            'User-Agent': user_ag,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'DNT': '1'}

    async def synthesize(self, event: Event, speaker='random', emotion='neutral') -> Event:
        #if speaker == 'random':

        speaker = rnd.choice(('ya-oksana', 'ya-zahar', 'ya-ermil', 'ya-jane', 'ya-omazh'))

        text = rec.voice1.sub('', event.text)

        url = 'https://voxworker.com/ru/ajax/convert'
        '''
        url = 'https://tts.voicetech.yandex.net/generate'
        params = {'key': config.ya_speech,
                  'text': text,
                  'format': 'mp3',
                  'lang': 'ru-RU',
                  'speed': '1',
                  'emotion': emotion,
                  'speaker': speaker,
                  'robot': '1'}
        '''

        params = {
            'voice': speaker,
            'speed': '1.0',
            'pitch': 1,
            'text': text
                }

        if not text:
            return event.answer('Я могу озвучить только текст и аудио сообщения '
                                '(с четким произношением слов)')

        try:
            proxy = get_proxy()
            headers = self.head()

            async with ClientSession() as session:
                async with await session.post(url, data=params, proxy=proxy, headers=headers) as res:
                    response = await res.json()

                assert response['status']

                async with await session.get(response['voice'], proxy=proxy, headers=headers) as res:
                    audio_bytes = await res.read()

        except:
            logs()
            return event.answer(str_error)

        try:
            _atta = await event.uploads(audio_bytes, type='doc', ret=True, telegram='audio')
            atta = _atta[0]

        except:
            logs()
            return event.answer(str_error)

        short_url = await event.get_short_link(atta[1])

        return event.answer(f'Вот ссылка - {short_url}' if not event.from_telegram else '').attachment(atta[0])

    async def get_quote(self) -> str:
        url = f'https://finewords.ru/sluchajnaya?_=1579426725762'
        try:
            for _ in range(3):
                _response = await req.get(url, timeout=5)
                response = rec.voice2.sub('', _response.decode())
                if 'HTML' in response:
                    continue
                return response
            return str_error

        except:
            logs()
            return str_error

    @middelware
    async def mainapp(self, event: Event) -> Event:
        event.is_can_edit_prev_msg = False

        #if event.check('🗣 СМЕНИТЬ ГОЛОС', 'ГОЛОС', '!СМЕНИТЬ ГОЛОС', '!ГОЛОС') and self.step >= 1:
        #    self.setstep(VoiceChange)
        #    return event.answer('Какой голос выберешь? Введи номер.\n' + tmp).keyboard(*keyb)

        #if event.check('💥 СМЕНИТЬ ЭМОЦИЮ', 'ЭМОЦИ', '!СМЕНИТЬ ЭМОЦИЮ', '!ЭМОЦИИ') and self.step >= 1:
        #    self.setstep(Emotion)
        #    return event.answer('Какую эмоцию выберешь?\n1. Обычный\n2. Добрый\n3. Злой').keyboard(*keybemo)

        if self.isstep(Emotion):
            if event.check('1', 'ОБЫЧНЫЙ'):
                self.emotion = 'neutral'

            elif event.check('2', 'ДОБРЫЙ'):
                self.emotion = 'good'

            elif event.check('3', 'ЗЛОЙ'):
                self.emotion = 'evil'

            else:
                return event.answer('Выбери одно из\n1. Обычный\n2. Добрый\n3. Злой').keyboard(*keybemo)
            self.setstep(EmotionEdit)

            event.keyboard(*keyb2)

            event.text = 'Тебе нравиться такое, звучание эмоции? Жми да если понравилось!'

            await self.synthesize(event, self.speaker, self.emotion)

            return event.answer('Эмоция голоса подошла?\nДа или Нет?')

        if self.isstep(VoiceChange):
            if event.check('ДА', '✅ ДА'):
                self.setstep(Start)
                self.set_condition(self.user_id, 'voice_speaker', self.speaker)
                return event.answer('Отлично! Жду твоё текстовое сообщение.').keyboard(*keyb)

            if event.check('ЕЩЁ ПРИМЕР'):
                pass
            else:
                try:
                    self.speaker = speak[int(event.text)]
                except:
                    return event.answer('Введи число').keyboard(*keyb)

            event.keyboard(*keyb2)

            event.text = await self.get_quote()
            # event.text = 'Тебе нравиться как звучит этот Голос?'

            await self.synthesize(event, self.speaker, self.emotion)

            return event.answer('Голос подошел?\n✅ Да? или введи номер другого голоса.')

        if self.isstep(EmotionEdit):
            if event.check('ДА'):
                self.setstep(Start)
                self.set_condition(self.user_id, 'voice_emotion', self.emotion)
                return event.answer('Отлично! Жду твоего сообщение 😌').keyboard(*keyb)
            else:
                self.setstep(Emotion)
                return event.answer('Какую эмоцию выберешь?\n1. Обычный\n2. Добрый\n3. Злой').keyboard(*keybemo)

        if self.isstep(NotWork, Start):
            if self.first == 0:
                self.first = 1
                return event.answer(f'Могу озвучить текстовое сообщение!\n'
                                    #f'Можно выбрать голос и эмоцию, команды:\n!Голос\n'
                                    #'!Эмоции\n\nЖду твоё текстовое сообщение ✍'
                                    ).keyboard(*keyb)
            else:
                return event.answer(
                    #'Можно сменить !Голос !Эмоции\n\n'
                    'Жду твоё текстовое сообщение ✍'
                                    ).keyboard(*keyb)

        if self.isstep(Start):
            if len(event) > 1500:
                return event.answer('Слишком длинное сообщение 😞\nдлина сообщения '
                                    'должна быть не более 1500 символов ☝').keyboard(*keyb)

            if len(event) == 0:
                return event.answer(f'Упс 😞 кажется ты {event.gender("прислал", "прислала")} пустое сообщение,'
                                    f'пришли текст или аудио сообщение (с четким произношением слов)').keyboard(*keyb)

            event.keyboards = ''
            if not event.from_comment:
                await event.answer('Обрабатываю запрос... ⌛').send(nonkeyb=True)

            await self.synthesize(event, self.speaker, self.emotion)

            return event.keyboard(*keyb)
