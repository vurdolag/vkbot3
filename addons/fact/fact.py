# -*- coding: utf-8 -*-
from Sqlbd import Sqlbd
from Addon import Addon, middelware, addon_init
from Template import str_back, str_error
import random as rnd


keyb = ['➡ Еще факт%b', str_back]

NotWork = 0
Start = 1

_msg1 = 'Чтобы выйти в меню напиши - !НАЗАД'

BD = Sqlbd('facts')


@addon_init(['!факт'], '❓', True, 2)
class Fact(Addon):
    async def get(self):
        try:
            ans = await BD.get_all(key='from_id', val=0)
            f = rnd.choice(ans)
            return f[1]
        except:
            return str_error

    @middelware
    async def mainapp(self, event):
        if event.from_comment:
            return event.answer(await self.get())

        if self.isstep(NotWork, Start):
            return event.answer(await self.get()).keyboard(*keyb)

        if self.isstep(Start):
            if event.check('EЩЕ ФАКТ', 'ЕЩЁ', 'ЕЩЕ'):
                return event.answer(await self.get()).keyboard(*keyb)
            else:
                return event.answer(_msg1).keyboard(str_back)







