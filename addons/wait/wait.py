# -*- coding: utf-8 -*-
import time
from untils import subscribe, Event
from Addon import Addon, middelware, addon_init
from Template import str_back
import recompile as rec

NotWork = 0
CreateMsg = 1
SetTime = 2

_msg1 = '❗ Опаньки... 😁 ошибка, попробуй повторить, формат ввода времени - день месяц год час минута'


@addon_init(['!НАПОМНИ'], '💭', False, 3)
class Wait(Addon):
    __slots__ = 'time_msg'

    def __init__(self, username, user_id):
        super(Wait, self).__init__(username, user_id)
        self.time_msg = ''

    def msg_send(self, event: Event, tim) -> Event:
        subscribe.create('only_send', event, self.time_msg, global_t=int(time.time()) + tim)

        self.setstep(CreateMsg)
        return event.answer(f'Отлично! Через {event.text} отправлю сообщение - {self.time_msg}\n\n'
                            'Напиши текст следующего напоминания или '
                            '!НАЗАД для того чтобы выйти.')

    def check(self, event: Event) -> Event:
        t = -1

        if event.check('5 минут'):
            t = 60 * 5

        elif event.check('15 МИНУТ'):
            t = 60 * 15

        elif event.check('30 МИНУТ'):
            t = 60 * 30

        elif event.check('1 ЧАС'):
            t = 60 * 60

        try:
            if event.check('час'):
                tim = rec.d.sub('', event.text)
                if tim:
                    t = 60 * 60 * int(tim)

            if event.check('минут'):
                tim = rec.d.sub('', event.text)
                if tim:
                    t = 60 * int(tim)

            if event.check('секунд'):
                tim = rec.d.sub('', event.text)
                if tim:
                    t = int(tim)
        except:
            pass

        if t != -1:
            return self.msg_send(event, t)

    def get_time_str(self, t):
        time_str = '{Эммм такого не должно быть}'

        if t < 3600:
            time_str = f'{t // 60} минут'

        elif 3600 < t < 3600 * 24:
            time_str = (f'{t // 3600} часов '
                        f'{t % 3600 // 60} минут')

        elif t > 3600 * 24:
            time_str = (f'{t // (3600 * 24)} дней '
                        f'{t % (3600 * 24) // 3600} часов '
                        f'{t % (3600 * 24) % 3600 // 60} минут')
        return time_str

    def str_to_time(self, a):
        try:
            b = time.strptime(' '.join(a), '%d %m %y %H %M')
        except:
            b = time.strptime(' '.join(a), '%d %m %Y %H %M')

        return int(time.mktime(b) - time.time()) - 3600 * 3

    def hello(self, event: Event) -> Event:
        if self.isstep(NotWork, CreateMsg):
            return event.answer(f'{self.username}, я напоминалка, могу отравить тебе сообщение, '
                                f'чтобы ты ничего не {event.gender("забыл", "забыла")}. О чем напомнить?\n\n'
                                'Напиши вначале текст напоминания, а следующим cообщением время.\n\n'
                                'Пример: Хватит спать, иди на работу').keyboard(str_back)

        if self.isstep(CreateMsg, SetTime):
            self.time_msg = 'Напоминание:\n\n' + event.text
            return event.answer('Хорошо!\nТеперь укажи время когда напомнить.\n\n'
                                'Пример: 11 11 19 08 30\n\nдень месяц год час минута\n\n'
                                'Или просто час и мунуты чтобы включить напоминание сегодня'
                                ).keyboard('5 МИНУТ%b', '15 МИНУТ%b',
                                           '30 МИНУТ%b', '1 ЧАС%b', str_back)

    @middelware
    async def mainapp(self, event: Event) -> Event:
        message = event.text.upper()

        if self.hello(event):
            return event

        if self.isstep(SetTime):
            event.keyboard(str_back)

            if self.check(event):
                return event

            a = message.split()

            if len(a) == 2:
                g = time.strftime("%d %m %y %H %M", time.localtime()).split()[:3]
                try:
                    b = time.strptime(message, '%H %M')

                except ValueError:
                    return event.answer(_msg1)

                a = (' '.join(g) + ' ' + str(b[3]) + ' ' + str(b[4])).split()

            if len(a) != 5:
                return event.answer(_msg1)

            t = self.str_to_time(a)

            if t < 0:
                return event.answer(f'❗ Опаньки... 😁 ошибка, ты ввел{event.gender("","а")}'
                                    f' дату меньше текущей, в прошлое я напомнить не могу 😟')

            event.text = self.get_time_str(t)

            return self.msg_send(event, t)






















