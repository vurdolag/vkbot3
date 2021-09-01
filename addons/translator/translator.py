# -*- coding: utf-8 -*-
from untils import until, Event
from Addon import Addon, middelware, addon_init
from Template import str_back

L = {'азербайджанский': 'az', 'малаялам': 'ml', 'албанский': 'sq', 'мальтийский': 'mt', 'амхарский': 'am',
                  'македонский': 'mk', 'английский': 'en', 'маори': 'mi', 'арабский': 'ar', 'маратхи': 'mr',
                  'армянский': 'hy', 'марийский': 'mhr', 'африкаанс': 'af', 'монгольский': 'mn', 'баскский': 'eu',
                  'немецкий': 'de', 'башкирский': 'ba', 'непальский': 'ne', 'белорусский': 'be', 'норвежский': 'no',
                  'бенгальский': 'bn', 'панджаби': 'pa', 'бирманский': 'my', 'папьяменто': 'pap', 'болгарский': 'bg',
                  'персидский': 'fa', 'боснийский': 'bs', 'польский': 'pl', 'валлийский': 'cy', 'португальский': 'pt',
                  'венгерский': 'hu', 'румынский': 'ro', 'вьетнамский': 'vi', 'русский': 'ru', 'гаитянский': 'ht',
                  'себуанский': 'ceb', 'галисийский': 'gl', 'сербский': 'sr', 'голландский': 'nl', 'сингальский': 'si',
                  'горномарийский': 'mrj', 'словацкий': 'sk', 'греческий': 'el', 'словенский': 'sl', 'грузинский': 'ka',
                  'суахили': 'sw', 'гуджарати': 'gu', 'сунданский': 'su', 'датский': 'da', 'таджикский': 'tg',
                  'иврит': 'he', 'тайский': 'th', 'идиш': 'yi', 'тагальский': 'tl', 'индонезийский': 'id',
                  'тамильский': 'ta', 'ирландский': 'ga', 'татарский': 'tt', 'итальянский': 'it', 'телугу': 'te',
                  'исландский': 'is', 'турецкий': 'tr', 'испанский': 'es', 'удмуртский': 'udm', 'казахский': 'kk',
                  'узбекский': 'uz', 'каннада': 'kn', 'украинский': 'uk', 'каталанский': 'ca', 'урду': 'ur',
                  'киргизский': 'ky', 'финский': 'fi', 'китайский': 'zh', 'французский': 'fr', 'корейский': 'ko',
                  'хинди': 'hi', 'коса': 'xh', 'хорватский': 'hr', 'кхмерский': 'km', 'чешский': 'cs', 'лаосский': 'lo',
                  'шведский': 'sv', 'латынь': 'la', 'шотландский': 'gd', 'латышский': 'lv', 'эстонский': 'et',
                  'литовский': 'lt', 'эсперанто': 'eo', 'люксембургский': 'lb', 'яванский': 'jv', 'малагасийский': 'mg',
                  'японский': 'ja', 'малайский': 'ms'}

keyb = ['!Все языки%b', str_back]
keyb2 = ['!Сменить язык%b', '!Быстрая команда%b', str_back]


NotWork = 0
Start = 1
ChangeLang = 2


@addon_init(["!ПЕРЕВОДЧИК", 'ПЕРЕВОД'], '🇬🇧', True, 3)
class Translator(Addon):
    __slots__ = 'LANG', 'now_lang', 'first'

    def __init__(self, username, user_id):
        super(Translator, self).__init__(username, user_id)
        self.lock = 1
        self.LANG = self.state('LANG', 'en-ru')
        self.now_lang = self.state('now_lang', ['Английского', 'Русский'])
        self.first = self.state('first_translator', 1, return_value=0)

    def get_lang_list(self):
        return list(L.keys())

    def state(self, key, value, update=False, return_value=-1):
        return self.set_condition(self.user_id, key, value, update, return_value)

    async def choise_lang(self, event: Event) -> Event:
        message = event.text.lower().split()
        if len(message) != 2:
            return event.answer('Нужно указать 2 слова через пробел\n\nПример: японский английский')

        m1, m2 = message[0], message[1]

        a = L.get(m1, 0)
        b = L.get(m2, 0)

        if a == 0 or b == 0:
            l = self.get_lang_list()
            for i in l:
                if i[0] == m1[0]:
                    if event.distance(i, m1) <= 2:
                        a = i
                if i[0] == m2[0]:
                    if event.distance(i, m2) <= 2:
                        b = i

            m1, m2 = a, b
            a = L.get(a, 0)
            b = L.get(b, 0)
            if a == 0 or b == 0:
                return event.answer(f'Видимо такого языка у меня нету в базе или ты '
                                    f'{event.gender("допустил", "допустила")}'
                                    f' ошибку...\n\nМожно узнать какие языки я '
                                    f'поддерживаю командой !Все языки')

        self.LANG = a + '-' + b
        if self.step:
            self.setstep(Start)
        self.now_lang = [m1, m2]

        self.state('now_lang', self.now_lang, update=True)
        self.state('LANG', self.LANG, update=True)

        if self.step:
            return event.answer(f'Ты {event.gender("выбрал", "выбрала")} {m1} и {m2}')
        else:
            return event

    async def get_translate(self, event: Event) -> Event:
        return event.answer(f'Перевод:\n{await event.translate(event.text, self.LANG)}')

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if event.check('!ВСЕ ЯЗЫКИ', '/ВСЕ ЯЗЫКИ') and self.step >= 1:
            a = ''
            for i in list(L.keys()):
                a += i + '\n'
            return event.answer(a).keyboard(*keyb)

        if event.check('!БЫСТРАЯ КОМАНДА'):
            return event.answer('Доступна быстрая команда, пример:\n\n'
                                '?? [языки] [текст для перевода]\n'
                                'или если языки уже выбраны\n'
                                '?? [текст для перевода]'
                                ).keyboard(*keyb2).attachment('photo-168691465_457250877')

        if event.check('!СМЕНИТЬ ЯЗЫК', '/СМЕНИТЬ ЯЗЫК' '!OTHER LANGUAGE'):
            self.setstep(ChangeLang)
            return event.answer('С какого на какой язык перевести? '
                                'Напиши пару языков например:\n\n'
                                'русский английский').keyboard(*keyb)

        if self.isstep(NotWork, Start):
            if self.first == 0:
                self.first = 1
                return event.answer(f'{self.username}, я могу превести с {self.now_lang[0]} на '
                                    f'{self.now_lang[1]}, что перевести?\n\n'
                                    f'Сменить языки командой - !Сменить язык'
                                    ).keyboard(*keyb2)
            else:
                return event.answer(f'Выбраны языки:\n{self.now_lang[0]} - '
                                    f'{self.now_lang[1]}\nЧто перевести?\n\n'
                                    f'➡ !Сменить язык\n'
                                    f'➡ !Быстрая команда'
                                    ).keyboard(*keyb2)

        if self.isstep(Start):
            event.keyboard(*keyb2)
            if event.text:
                return await self.get_translate(event)
            else:
                return event.answer('Нету текста для перевода')

        if self.isstep(ChangeLang):
            event.keyboard(*keyb)
            return await self.choise_lang(event)



















