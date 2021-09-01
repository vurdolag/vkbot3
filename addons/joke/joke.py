# -*- coding: utf-8 -*-
from untils import req, logs, Event
from Sqlbd import Sqlbd
from Addon import Addon, middelware, addon_init
from Template import str_error, str_back
from recompile import joke_re1, joke_re2, joke_re3, joke_re4, joke_re5, quot

cmd = '!анекдот,!рассказ,!стих,!афоризм,!цитаты,!тосты,!статусы,!bash'


def cmd_up(y):
    return y.split(',')


cmd_clear = ('анекдот,рассказ,стих,афоризм'
             'цитаты,тосты,статусы,баш,bash')

MOD = [['1', '!АНЕКДОТ'],
       ['2', '!РАССКАЗ'],
       ['3', '!СТИХ'],
       ['4', '!АФОРИЗМЫ', 'АФОРИЗМ'],
       ['5', '!ЦИТАТЫ', 'ЦИТАТА'],
       ['6', '!ТОСТЫ', 'ТОСТ'],
       ['7', '!СТАТУСЫ', 'СТАТУС'],
       ['8', '!BASH']]

_help = ''
for i in MOD:
    _help += f'\n{i[0]}. {i[1].capitalize()}'


keyb = ['😂 !Анекдот%b', '😆 !Рассказ%b',
        '📜 !Стих%b', '💭 !Афоризмы%b',
        '☝ !Цитаты%b', '🎉 !Тосты%b',
        '😎 !Статусы%b', '🗯 !Bash%b',
        str_back]

Start = 1

_BD = Sqlbd('facts')


@addon_init(['!АНЕКДОТ, СТИХ, ЦИТАТЫ ...', *cmd_up(cmd)], '😂', True, 2)
class Joke(Addon):
    """
    Шутейки
    """
    async def get_joke(self, mode):
        url = f'http://rzhunemogu.ru/RandJSON.aspx?CType={mode}'
        try:
            response = await req.get(url, timeout=5)
            response = response.decode('cp1251').split('"content":"')[-1][0:-2]
            await _BD.put(self.user_id, response, int(mode))
            return response

        except:
            logs()
            return str_error

    async def get_quote(self):
        url = f'https://finewords.ru/sluchajnaya?_=1579426725762'
        try:
            for _ in range(3):
                response = await req.get(url, timeout=5)
                response = joke_re4.sub("", response.decode())
                if 'HTML' in response:
                    continue

                await _BD.put(self.user_id, response, 5)
                return response
            return str_error

        except:
            logs()
            return str_error

    async def get_bash(self):
        try:
            url = 'https://bash.im/forweb/?u'
            res = await req.get(url)
            res = res.decode()
            res = joke_re1.findall(res)
            res = joke_re2.sub("", res[0])
            res = joke_re3.sub("\n", res)
            res = quot.sub('"', res)
            await _BD.put(self.user_id, res, 8)
            return res

        except:
            return str_error

    async def get(self, event: Event):
        message = event.text.upper()
        message = joke_re5.sub('', message)
        if event.check('5', '!ЦИТАТЫ', '!ЦИТАТА'):
            return event.answer(await self.get_quote()).keyboard(*keyb)
        if event.check('8', '!БАШ', '!BASH'):
            return event.answer(await self.get_bash()).keyboard(*keyb)

        for i in MOD:
            if message in i:
                return event.answer(await self.get_joke(i[0])).keyboard(*keyb)

        h = '' if event.support_keyb_inline else f'{_help}\n⬅ Назад'
        return event.answer(f'Что выберешь?{h}').keyboard(*keyb)

    @middelware
    async def mainapp(self, event: Event) -> Event:
        self.setstep(Start)
        return await self.get(event)








