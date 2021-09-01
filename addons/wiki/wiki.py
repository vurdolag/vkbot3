# -*- coding: utf-8 -*-
from untils import Event
from Addon import Addon, middelware, addon_init
from Template import str_back


NotWork = 0
Start = 1


@addon_init(['!ВИКИПЕДИЯ', 'ВИКИ'], '👥', True, 3)
class Wikiinfo(Addon):
    __slots__ = ()

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if event.from_comment:
            event.text = ' '.join(event.text.split()[1:]).upper()
            return event.answer(await event.wiki(await event.checker_text(event.text)))

        if self.isstep(NotWork, Start):
            return event.answer('Что ищешь в Википедии? Напиши слово.').keyboard(str_back)

        if self.isstep(Start):
            return event.answer(await event.wiki(await event.checker_text(event.text))).keyboard(str_back)
