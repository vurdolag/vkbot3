# -*- coding: utf-8 -*-
import ujson as json
from untils import req, logs
from Addon import Addon, addon_init
from Template import str_error, str_back
import random as rnd


class AddTxt(Addon):
    __slots__ = 'step', 'USERNAME', 'USER_ID'

    async def get_txt(self, event):
        event.set_typing()
        try:
            url = 'https://models.dobro.ai/gpt2/medium/'
            text = event.text
            params = json.dumps({"prompt": text, "length": 55, "num_samples": 4})

            us = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/79.0.3945.117 Safari/537.36')}
            d = await req.post(url, data=params, headers=us)
            d = json.loads(d.decode('utf-8'))
            d = rnd.choice(d["replies"])
            return text + d

        except:
            logs()
            return str_error

    async def mainapp(self, event):

        if event.stoper():
            self.end()
            return event.answer('Вышли в главное меню')

        if self.isstep(0, 1):
            return event.answer('Пришли фразу, и бот допишет её за тебя в мини-историю'
                                ).keyboard(str_back)

        if self.isstep(1):
            response = await self.get_txt(event)
            return event.answer(response).keyboard(str_back)










