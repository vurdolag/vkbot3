# -*- coding: utf-8 -*-
from untils import Event
from Addon import Addon, middelware, addon_init
from Template import str_back

_DATA = {'a': '\u0250',
         ' ': ' ',
         'b': 'q',
         'c': '\u0254',
         'd': 'p',
         'e': '\u01DD',
         'f': '\u025F',
         'g': '\u0183',
         'h': '\u0265',
         'i': '\u0131',
         'j': '\u027E',
         'k': '\u029E',
         'l': '\u0283',
         'm': '\u026F',
         'n': 'u',
         'r': '\u0279',
         't': '\u0287',
         'v': '\u028C',
         'w': '\u028D',
         'y': '\u028E',
         '.': '\u02D9',
         '[': ']',
         '(': ')',
         '{': '}',
         '?': '\u00BF',
         '!': '\u00A1',
         "‘": ',',
         ',': "‘",
         '<': '>',
         '_': '\u203E',
         '\u203F': '\u2040',
         '\u2045': '\u2046',
         '\u2234': '\u2235',
         '\r': '\n',
         'а': '\u0250',
         'б': '\u018D',
         'в': '\u029A',
         'г': '\u0279',
         'д': '\u0253',
         'е': '\u0259',
         'ё': '\u01DD',
         'ж': 'ж',
         'з': '\u03B5',
         'и': 'и',
         'й': '\u0146',
         'к': '\u029E',
         'л': 'v',
         'м': 'w',
         'н': 'н',
         'о': 'о',
         'п': 'u',
         'р': 'd',
         'с': '\u0254',
         'т': '\u026F',
         'у': '\u028E',
         'ф': 'ф',
         'х': 'х',
         'ц': '\u01F9',
         'ч': '\u04BA',
         'ш': 'm',
         'щ': 'm',
         'ъ': 'q',
         'ы': '\u0131q',
         'ь': 'q',
         'э': '\u0454',
         'ю': 'о\u0131',
         'я': '\u0281',
         'А': '\u2200',
         'Б': '\u0261',
         'В': '\u029A',
         'Г': '\u02E9',
         'Д': '\u2207',
         'Е': '\u018E',
         'Ё': '\u018E',
         'Ж': 'Ж',
         'З': '\u2107',
         'И': 'И',
         'Й': '\u1E47',
         'К': '\u0A2E',
         'Л': 'V',
         'М': 'W',
         'Н': 'H',
         'О': 'O',
         'П': '\u2210',
         'Р': '\u217E',
         'С': '\u0186',
         'Т': '\u22A5',
         'У': '\u028E',
         'Ф': 'Ф',
         'Х': 'X',
         'Ц': 'n',
         'Ч': '\u0570',
         'Ш': '\u0BF1',
         'Щ': 'm',
         'Ъ': 'q',
         'Ы': '\u09F7q',
         'Ь': 'q',
         'Э': '\u0404',
         'Ю': 'O\u09F7',
         'Я': '\u04C3',
         '1': '1',
         '2': '5',
         '3': '\u2107',
         '4': 'h',
         '5': '2',
         '6': '9',
         'L': '7',
         '8': '8',
         '9': '6',
         '0': '0'}

_layout_data = dict(zip(map(ord,
                            "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                            'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~!@#$%^&'),
                            "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                            'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё!"№;%:?'))

NotWork = 0
Start = 1


@addon_init(['!ПЕРЕВЕРНИ ТЕКСТ', '!ПЕРЕВЕРНИ'], '🙃', True, 2)
class Txt(Addon):
    __slots__ = ()

    def gen_txt(self, event: Event):
        if event.text:
            text = event.text[::-1]
            out = ''
            for i in text:
                out += _DATA.get(i, i)

            event.answer(out)
        else:
            event.answer('Нету текста. Пустое сообщение...')

    def keyboard_layout(self, event: Event) -> Event:
        return event.answer(event.text.translate(_layout_data))

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if event.from_comment:
            event.text = ' '.join(event.text.split()[1:])
            self.gen_txt(event)
            return event

        if self.isstep(NotWork, Start):
            return event.answer(f'{self.username}, я могу перевернуть 🙃 текст вверх ногами\n\n'
                                'Пришли любой текст ✍').keyboard(str_back)

        if self.isstep(Start):
            self.gen_txt(event)
            return event.keyboard(str_back)
