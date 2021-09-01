# -*- coding: utf-8 -*-
from untils import subscribe, req, Event
from Addon import Addon, middelware, addon_init
from Template import str_back, str_error
import time
from lxml import etree

keyb = [str_back]
keyb1 = ['На вчера%b', 'На завтра%b', 'На послезавтра%b', 'Другой гороскоп%b', 'Рассылка%g', str_back]
horo = ('\n1. Общий\n'
        '2. Эротический\n'
        '3. Антигороскоп\n'
        '4. Бизнес\n'
        '5. Здоровье\n'
        '6. Кулинарный\n'
        '7. Любовный\n'
        '8. Мобильный\n')
horo_choise = {'1': 'com', '2': 'ero', '3': 'anti', '4': 'bus', '5': 'hea', '6': 'cook', '7': 'lov', '8': 'mob',
               'общий': 'com', 'эротический': 'ero', 'антигороскоп': 'anti', 'бизнес': 'bus',
               'здоровье': 'hea', 'кулинарный': 'cook', 'любовный': 'lov', 'мобильный': 'mob'}
horo_choise_rev = {v: k for k, v in horo_choise.items()}
zodiac = ('\n1. Овен\n'
          '2. Телец\n'
          '3. Близнецы\n'
          '4. Рак\n'
          '5. Лев\n'
          '6. Дева\n'
          '7. Весы\n'
          '8. Скорпион\n'
          '9. Стрелец\n'
          '10. Козерог\n'
          '11. Водолеи\n'
          '12. Рыбы\n')
zodiac_choise = {'1': 'aries', '2': 'taurus', '3': 'gemini', '4': 'cancer',
                 '5': 'leo', '6': 'virgo', '7': 'libra', '8': 'scorpio', '9': 'sagittarius',
                 '10': 'capricorn', '11': 'aquarius', '12': 'pisces',
                 'овен': 'aries', 'телец': 'taurus', 'близнецы': 'gemini', 'рак': 'cancer',
                 'лев': 'leo', 'дева': 'virgo', 'весы': 'libra', 'скорпион': 'scorpio', 'стрелец': 'sagittarius',
                 'козерог': 'capricorn', 'водолеи': 'aquarius', 'рыбы': 'pisces'}

zodiac_choise_rev = {v: k for k, v in zodiac_choise.items()}
horo_day = {'на вчера': 'yesterday', 'на завтра': 'tomorrow', 'на послезавтра': 'tomorrow02'}


class horoscope_data:
    tim = 0
    data = {}


_msg1 = 'Напиши цифру от 1 до 8 или название гороскопа, можно голосовым сообщением'
_msg2 = 'Напиши цифру от 1 до 12 или название знака'
_msg3 = 'Чтобы выбрать другой гороскоп пиши - Другой гороскоп или выбери ' \
        'гороскоп На вчера, На завтра, На послезавтра. Чтобы выйти - Назад'


@addon_init(['!ГОРОСКОП'], '🌠', True, 2)
class Goroscope(Addon):
    __slots__ = 'horos', 'zadiacs'

    def __init__(self, username, user_id):
        super(Goroscope, self).__init__(username, user_id)
        self.horos = ''
        self.zadiacs = ''

    def pars_xml(self, i, x):
        root = etree.fromstring(x)
        y = {}
        for appt in root.getchildren():
            x = {}
            for elem in appt.getchildren():
                if elem.text:
                    x[elem.tag] = elem.text
            if x:
                y[appt.tag] = x
        horoscope_data.data[i] = y

    async def get_horo(self):
        if time.time() - horoscope_data.tim > 3600 * 24:
            horoscope_data.tim = time.time()
            horoscope_data.data = {}

            title = ['com', 'ero', 'anti', 'bus', 'hea', 'cook', 'lov', 'mob']
            for i in title:
                url = f'https://ignio.com/r/export/utf/xml/daily/{i}.xml'
                x = await req.get(url)
                self.pars_xml(i, x)
            print(time.time() - horoscope_data.tim)
        return True

    async def get(self, txt: str) -> str:
        await self.get_horo()
        txt = txt.lower().split()
        a, b, c = '', '', ''
        if len(txt) == 2:
            a, b, c = txt[1], '', ''
        if len(txt) == 3:
            a, b, c = txt[1], txt[2], ''
        if len(txt) > 3:
            a, b, c = txt[1], txt[2], txt[3]

        x = horoscope_data.data[horo_choise.get(a, 'com')][zodiac_choise.get(b, 'aries')][horo_day.get(c, "today")]
        return x

    async def check(self, _dict: dict, event: Event) -> str:
        return _dict.get(await event.checker_text(event.text.lower()), 0)

    @middelware
    async def mainapp(self, event: Event) -> Event:
        event.is_can_edit_prev_msg = False

        if event.from_comment:
            return event.answer(await self.get(await event.checker_text(event.text.lower())))

        await self.get_horo()

        if event.check('другой гороскоп'):
            self.end()

        if self.isstep(0, 1):
            return event.answer(f'Какой гороскоп выберешь?{horo}\nНапиши цифру').keyboard(*keyb)

        if self.step > 0:
            if event.check('рассылка'):
                return event.answer(f'Хочешь подписаться на рассылку новых гороскопов по'
                                    f' теме "{horo_choise_rev[self.horos].capitalize()}" для '
                                    f'знака зодиака {zodiac_choise_rev[self.zadiacs].capitalize()}?\n'
                                    ).keyboard('Да, подписаться%g', 'Отказаться%r', tablet=1)

            if event.check('да, подписаться'):
                key = 'гороскоп'
                command = f'{key} {horo_choise_rev[self.horos]} {zodiac_choise_rev[self.zadiacs]}'
                if subscribe.create(key, event, command):
                    return event.answer('Подписка оформлена, теперь тебе будут приходить свежие гороскопы каждый день. '
                                        'Чтобы отказаться от рассылки гороскопов напиши - отписка гороскоп'
                                        ).keyboard(*keyb1)
                else:
                    return event.answer(str_error)

            if event.check('отказаться'):
                return event.answer('Подписка отменена').keyboard(*keyb1)

        if self.isstep(1):
            try:
                self.horos = await self.check(horo_choise, event)
                if self.horos:
                    self.setstep(2)
                    return event.answer(f'Выбери знак зодиака{zodiac}\nНапиши цифру или '
                                        f'название знака зодиака, можно голосовым сообщением').keyboard(*keyb)
                else:
                    return event.answer(_msg1).keyboard(*keyb)
            except:
                return event.answer(_msg1).keyboard(*keyb)

        if self.isstep(2):
            try:
                self.zadiacs = await self.check(zodiac_choise, event)
                if self.zadiacs:
                    self.setstep(3)
                    return event.answer(
                        f'Гороскоп на сегодня:\n{horoscope_data.data[self.horos][self.zadiacs]["today"]}'
                                        ).keyboard(*keyb1)
                else:
                    return event.answer(_msg2).keyboard(*keyb)
            except:
                return event.answer(_msg2).keyboard(*keyb)

        if self.isstep(3):
            d = await self.check(horo_day, event)
            if d:
                return event.answer(f'Гороскоп {event.text.lower()}:\n'
                                    f'{horoscope_data.data[self.horos][self.zadiacs][d]}'
                                    ).keyboard(*keyb1)
            else:
                return event.answer(_msg3).keyboard(*keyb1)
