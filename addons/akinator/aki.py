from akinator.async_aki import Akinator
from Template import str_yes, str_no, str_back, str_error, str_yes_or_no
from untils import logs, Event
from Addon import Addon, middelware, addon_init

from typing import Optional

keyb = [str_yes, str_no, '🙂Скорее да%b', '🙃Скорее нет%b', '🤔Не знаю%b', str_back]
keyb2 = [str_yes, str_no, str_back]

_msg1 = 'Ххаха я так и знал!\n\nСыграем ещё?\n✅ Да или ❌ Нет'
_msg2 = 'Эх в этот раз не повезло...\n\nСыграем ещё?\n✅ Да или ❌ Нет'
_msg3 = 'Сыграем ещё?\n✅ Да или ❌ Нет'
_msg4 = 'Твой персонаж: {}\n{}\n\nЯ верно угадал?'
_msg5 = 'Ладно в другой раз 🙂'
_msg6 = ('{}, привет! Я - Акинатор, смогу угадать любого персонажа, которого ты загадаешь.\n\n'
         'Спорим? ✅ Да или ❌ Нет')
_msg7 = 'Играем?\n✅ Да или ❌ Нет'
_id_photo_aki = 'photo-168691465_457243048'

HELLO = 0
START = 1
IN_GAME = 2
END = 3


@addon_init(['!акинатор'], '🌪', False, 1)
class Aki(Addon):
    __slots__ = 'lock', 'aki', 'first_aki', 'lng'

    def __init__(self, username, user_id):
        super(Aki, self).__init__(username, user_id)
        self.lock = 0
        self.aki = Akinator()
        self.first_aki = self.set_condition(self.user_id, 'first_aki', 1, False, 0)
        self.lng = 'ru'

    async def get_aki(self, event: Event) -> str:
        if event.check('ДА', '1'):
            txt = 'yes'
        elif event.check('НЕТ', '2'):
            txt = 'no'
        elif event.check('НЕ ЗНАЮ', '3'):
            txt = 'idk'
        elif event.check('СКОРЕЕ ДА', '4'):
            txt = 'probably'
        elif event.check('СКОРЕЕ НЕТ', '5'):
            txt = 'pn'
        else:
            txt = 'no'

        if self.lock == 0:
            self.lock = 1
            try:
                self.lng = 'ru'
                return await self.aki.start_game('ru')
            except:
                try:
                    self.lng = 'en'
                    return await self.translate(await self.aki.start_game("en"))
                except:
                    try:
                        self.lng = 'en'
                        return await self.translate(await self.aki.start_game("en2"))
                    except:
                        return str_error

        try:
            if self.aki.progression <= 80:
                #if txt == "b":
                #    x = await self.aki.back()
                #    return await until.translate(x) if self.lng != 'ru' else x
                #else:
                x = await self.aki.answer(txt)
                return await self.translate(x) if self.lng != 'ru' else x

            else:
                return await self.aki.win()

        except:
            logs()
            self.lock = 0
            return str_error

    def end(self, event: Optional[Event] = None):
        self.step = 0
        self.lock = 0
        self.aki = None

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if self.isstep(HELLO, START):
            event.keyboard(*keyb2).attachment(_id_photo_aki)

            if self.first_aki == 0:
                self.first_aki = 1
                return event.answer(_msg6, self.username)

            else:
                return event.answer(_msg7)

        if self.isstep(START):
            if event.check('ДА'):
                event.set_typing()
                self.aki = Akinator()
                self.setstep(2)
                a = await self.get_aki(event)
                h = 'Отлично!' if self.lng == 'ru' else str_error
                return event.answer('{}\n\n{}', h, a).keyboard(*keyb)

            elif event.check('НЕТ'):
                self.end(event)
                return event.answer(_msg5).keyboard()
            else:
                return event.answer(str_yes_or_no).keyboard(*keyb2)

        if self.isstep(IN_GAME):
            end_answer = await self.get_aki(event)

            if not isinstance(end_answer, str) and isinstance(end_answer, dict):
                url_pix = end_answer.get('absolute_picture_path')
                description = end_answer.get('description', 'Нет описания :(')
                name = end_answer.get('name', 'Нет имени :(')
                if url_pix:
                    await event.uploads(url_pix)
                self.setstep(END)
                self.lock = 0
                aki_msg = await event.translate(description) if self.lng != 'ru' else description

                return event.answer(_msg4, name, aki_msg).keyboard(*keyb2)
            else:
                return event.answer(end_answer).keyboard(*keyb)

        if self.isstep(END, START):
            self.aki = Akinator()
            if event.check('ДА'):
                return event.answer(_msg1).keyboard(*keyb2)

            elif event.check('НЕТ'):
                return event.answer(_msg2).keyboard(*keyb2)

            else:
                return event.answer(_msg3).keyboard(*keyb2)



