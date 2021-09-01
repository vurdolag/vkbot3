# -*- coding: utf-8 -*-
import ujson as json
from untils import req, until, logs, Event
from Addon import Addon, middelware, addon_init
from Template import str_error, str_back, str_maybe_later
import recompile as rec


_p1 = 'Начать игру%b'
_p2 = 'Правила%b'
_p3 = 'Повтор%b'

keyb = [_p1, _p2, str_back]
keyb2 = [_p1, str_back]
keyb3 = ['Русские слова%b', 'Английские слова%b', 'Страны%b', 'Города%b', str_back]
keyb4 = [_p3, _p2, str_back]
keyb5 = [_p3, 'Значение%b', _p2, str_back]


MOD = [
    ['1', 'русские слова', 'rus'],
    ['2', 'английские слова', 'eng'],
    ['3', 'страны', 'countries'],
    ['4', 'города', 'cities']
]

_L = 7


_msg1 = ('Бот загадывает слово, в котором все буквы заменяются знаками подчёркивания "_".\n'
         'Игрок предлагает букву, которая может быть в слове. Если есть, то бот заменяет ею '
         'пропуски. Если такой буквы нет, то разбивается сердечко.\nЕсли целые сердечки закончились,'
         ' игрок проигрывает и считается повешенным. Если игроку удаётся угадать слово, '
         'он выигрывает.{}')

_msg2 = '\n\n➡ 1. Русские слова\n➡ 2. Английские слова\n➡ 3. Страны\n➡ 4. Города\n'
_msg3 = '\n\n➡ 1. Начать игру\n➡ 2. Правила\n⬅ Назад в меню'
_msg4 = 'Какую тему выберешь?{}'
_msg5 = 'Добро пожаловать в игру Виселица{}'
_msg6 = '{}\n{}\n\n{}\n\nБыло: {}'
_msg7 = 'Увы, тебя повесили!\nЗагаданное слово: {}{}'
_msg8 = '\n\n➡ 1. Повторим?\n➡ 2. Правила\n➡ 3. Значение слова'
_msg9 = 'Поздавляю ты выграл{}!{}'
_msg10 = '\n\n➡ 1. Начать игру\n⬅ Назад в меню'


_id_photo_lost = 'photo-168691465_457246054'
_id_photo_win = 'photo-168691465_457246055'


@addon_init(['!виселица'], '😵', False, 1)
class Gallows(Addon):
    __slots__ = 'lives', 'word', 'temp_word', 'about', 'char', 'mod'

    def __init__(self, username, user_id):
        super(Gallows, self).__init__(username, user_id)
        self.lives = 7
        self.word = ''
        self.temp_word = '*'
        self.about = ''
        self.char = ''
        self.mod = 'rus'

    def upd(self):
        self.lives = 7
        self.word = ''
        self.temp_word = '+'
        self.about = ''
        self.char = ''
        self.mod = 'rus'

    async def get_word(self, mod):
        try:
            url = f'https://engine.lifeis.porn/api/words.php?{mod}'
            d = await req.post(url)
            d = json.loads(d.decode('utf-8'))['data']
            return d['word'], d['explanation']

        except:
            logs()
            return str_error

    def word_creater(self, key=''):
        tmp = ''
        key = key.lower()
        for i in self.word.lower():
            if (i == key or i in self.temp_word.lower()) and key:
                tmp += i + ' '
            else:
                tmp += '_ '
        if key not in self.char and key:
            self.char += key + ' '
        return tmp

    def lv(self):
        return '💔' * (_L - self.lives) + '❤' * self.lives

    @middelware
    async def mainapp(self, event: Event) -> Event:
        event.text = rec.clear.sub('', event.text).strip()

        if event.check('2', 'ПРАВИЛА', '➡ ПРАВИЛА', 'КАК') and self.step != 2:
            h = '' if event.support_keyb_inline else _msg10
            return event.answer(_msg1, h).keyboard(*keyb2)

        if self.isstep(4):
            if event.check('1', 'ПОВТОРИМ', 'ДА', 'АГА', 'ПОВТОР', 'НАЧАТЬ ИГРУ'):
                event.text = 'НАЧАТЬ ИГРУ'

            elif event.check('3', 'ЗНАЧЕНИЕ', 'ЗНАЧЕНИЕ СЛОВА'):
                if self.mod in ['countries', 'cities']:
                    return event.answer(await until.wiki(self.word)).keyboard(*keyb4)

                else:
                    return event.answer(self.about).keyboard(*keyb4)

            else:
                self.end()
                self.upd()
                return event.answer(str_maybe_later).keyboard()

        if event.check('1', 'НАЧАТЬ ИГРУ', 'ИГРАТЬ') and self.step != 2:
            self.setstep(2)
            h = ['', 1] if event.support_keyb_inline else [_msg2, 2]
            return event.answer(_msg4, h[0]).keyboard(*keyb3, tablet=h[1])

        if self.isstep(0, 1):
            h = '' if event.support_keyb_inline else _msg3
            return event.answer(_msg5, h).keyboard(*keyb)

        if self.isstep(2):
            self.upd()
            for i in MOD:
                if event.text.lower() in i:
                    self.mod = i[-1]
                    break

            if self.mod:
                self.setstep(3)
                self.word, self.about = await self.get_word(self.mod)

                self.temp_word = '_ ' * len(self.word)
                out = self.word_creater()
                h = 'Пришли английскую букву' if self.mod == 'eng' else 'Пришли букву'
                return event.answer(_msg6, h, self.lv(), out, self.char).keyboard(str_back)

            else:
                return event.answer(str_error).keyboard(*keyb3)

        if self.isstep(3):
            out = self.word_creater(event.text.lower()[:1])

            if self.lives < 2 and out == self.temp_word.lower():
                self.setstep(4)
                h = '' if event.support_keyb_inline else _msg8
                return event.answer(_msg7, self.word, h).keyboard(*keyb5, tablet=1).attachment(_id_photo_lost)

            if '_' not in out:
                self.setstep(4)
                h = '' if event.support_keyb_inline else _msg8
                return event.answer(_msg9, event.gender("", "а"), h
                                    ).keyboard(*keyb5, tablet=1).attachment(_id_photo_win)

            h = 'Пришли английскую букву' if self.mod == 'eng' else 'Пришли букву'

            if out != self.temp_word.lower():
                self.temp_word = out
                return event.answer(_msg6, h, self.lv(), out, self.char).keyboard(str_back)

            else:
                self.lives -= 1
                return event.answer(_msg6, h, self.lv(), out, self.char).keyboard(str_back)

        return event.answer('Что - то не пойму...')



























