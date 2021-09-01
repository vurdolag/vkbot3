# -*- coding: utf-8 -*-
from untils import until, Event
from Addon import Addon, middelware, addon_init
from Template import str_back
from addons.smile.emo import emo
import re


NotWork = 0
Start = 1


@addon_init(['!СМАЙЛЫ', '!ТЕКСТ В СМАЙЛЫ',  '!СМАЙЛ'], '😅', True, 2)
class Smile(Addon):
    __slots__ = ()

    def text_to_smile(self, text):
        tmp = ''
        e = ''
        text = text.lower().split()
        for i in text:
            for emoji in emo:
                patern = f"({'|'.join(emo[emoji].split())})"
                if re.findall(patern, i):
                    e = re.sub(patern, emoji, i)
                    break
                else:
                    e = i
            tmp += e + ' '

        return tmp

    def smile_coder(self, text):
        pass

    def smile_decoder(self, text):
        pass

    @middelware
    async def mainapp(self, event: Event):
        if event.from_comment:
            return event.answer(self.text_to_smile(event.text))

        if self.isstep(NotWork, Start):
            return event.answer(f'Я добавлю смайлы в твоё сообщение'
                                ).keyboard(str_back).attachment('photo-168691465_457246120')

        if self.isstep(Start):
            if event.text:
                return event.answer(
                    self.text_to_smile(await until.checker_text(event.text))
                ).keyboard(str_back)
            else:
                return event.answer('Нужен текст').keyboard(str_back)












