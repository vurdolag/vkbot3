# -*- coding: utf-8 -*-
import random as rnd
import recompile as re
from untils import until, Event
from Sqlbd import Sqlbd
from Addon import Addon, addon_init
from Template import str_back, str_yes, str_no, str_menu_out
from operator import itemgetter
import asyncio
import sqlite3

its = until.int_to_smail

_p2 = '🔄 Пропустить%b'

keyb = ['❓ Подсказка%b', _p2, str_back]
keyb2 = [_p2, str_back]
keyb3 = [str_yes, str_no, '❕ ИНФО%b', '✊ Сложность%b', str_back]
keyb4 = [str_back]
keyb5 = ['😀 Легко%g', '😐 Нормально%b', '😡 Сложно%r']

qlevl = {'ЛЕГКО': [60, 10, 10, 1, 0], 'НОРМАЛЬНО': [30, 5, 5, 2, 1], 'СЛОЖНО': [15, 3, 3, 3, 2]}
word_point = {1: 'очко', 2: 'очка', 3: 'очка'}
qest_tasks = []


_msg1 = ('Время вышло, попытки кончились, игра окончена 😊 Ты смог{} набрать {} очков и {}\n\n'
         'Хочешь попробовать ещё?\n✅ ДА или ❌ НЕТ')
_msg2 = '⏰ Время вышло, {}верный ответ - {}{}\nСледующий вопрос:\n{}{}'
_msg3 = 'Поиграли и хватит выходим в главное меню)\n\nТы набрал{} {} очков и {}'
_msg4 = ('{}, хочешь сыграть в викторину?\n\n✅ ДА или ❌ НЕТ\n\n'
         '❕ ИНФО - описание игры\n\n✊ Сложность - выбор сложности игры')
_msg5 = 'Отлично! держи вопрос:\n{}{}'
_msg6 = 'Ну ладно) заходи потом'
_msg7 = ('{}! Тебе нужно отвечать на вопросы, за каждый правильный ответ начисляются очки, за неправильный - '
         'снимаются. На ответ даётся {} секунд, также у тебя есть дополнительных {} подсказок и {} '
         'жизней. Когда потратишь все жизни, игра завершается.\n\nНу что, играем?\n✅ ДА или ❌ НЕТ\n\nСейчас уровень '
         'сложности "{}", выбрать сложность командой - Сложность')
_msg8 = ('Какой уровень сложности выберешь?\n\n'
         '😀 Легко - 60 секунд на ответ, 10 жизней, 10 подсказок, 1 '
         'очко за правильный ответ.\n\n'
         '😐 Нормально - 30 секунд на ответ, 5 жизней, 5 подсказок, 2 '
         'очка за правильный ответ.\n\n'
         '😡 Сложно - 15 секунд на ответ, 3 жизни, 3 подсказоки, 3 '
         'очка за правильный ответ.')
_msg9 = 'Ты выбрал{} уровень сложности - {}\n\nНачнём игру?\n\n✅ ДА или ❌ НЕТ'
_msg10 = 'Тогда начнем, на ответ даётся {} секунд, первый вопрос:\n{}{}'
_msg11 = 'Очень жаль, может в другой раз.'
_msg12 = 'Чтобы согласится или отказаться от игры введи "ДА" или "НЕТ"'
_msg13 = 'Подсказки закончились 😒'
_msg14 = 'Один вопрос, одна подсказка 😝'
_msg15 = '✅ Правильно! Начислено ➕{} {}.{}\nСледующий вопрос:\n{}{}'
_msg16 = '{}опытки кончились, игра окончена 😊\nТы смог{} набрать {} очков и {}\n\nПовторим? Да или НЕТ'
_msg17 = '{}ерный ответ - {}{}\nСледующий вопрос:\n{}{}'

id_doc_logo = 'doc38487286_527864911'


_BD = Sqlbd('qest')
_BD_USERDATA = Sqlbd('userdata')


@addon_init(['!викторина'], '🎮', False, 1)
class Qest(Addon):
    __slots__ = ('_LAST_ANSWER', '_QEST_POINT', '_ADD_HELP', '_WRONG_ANSWER',
                 '_ADD_HELP_LOCK', 'wait', '_L', '_T', '_H', 'level', '_PP', '_WA')

    def __init__(self, username, user_id):
        super(Qest, self).__init__(username, user_id)
        self.lock = 2
        self._LAST_ANSWER = ''
        self._QEST_POINT = 0
        self._ADD_HELP = 0
        self._WRONG_ANSWER = 0
        self._ADD_HELP_LOCK = 0
        self.wait = 0
        self._T = 30
        self._H = 5
        self._L = 5
        self.level = 'НОРМАЛЬНО'
        self._PP = 3
        self._WA = 1

    async def waits(self, event: Event, index_wait: int):
        for task in qest_tasks:
            if task.done():
                qest_tasks.remove(task)

        await asyncio.sleep(self._T)
        if self.wait == index_wait:
            if self._WRONG_ANSWER >= self._H:
                point = self._QEST_POINT
                self.setstep(1000)
                await _BD.put(self.user_id, point)

                await event.answer(_msg1,
                                   event.gender("", "ла"),
                                   its(point),
                                   self.get_top(point)
                                   ).keyboard(*keyb3).send()
                del event

            else:
                last_answer = self._LAST_ANSWER[0]
                answer = self._qest()
                h = ''
                if self._QEST_POINT >= self._PP:
                    h = f'➖{its(self._PP)} {word_point[self._PP]}, '
                    self._QEST_POINT -= self._PP
                self._WRONG_ANSWER += 1
                self._LAST_ANSWER = answer[1]
                qest_tasks.append(asyncio.create_task(self.waits(event, self.wait + 1)))
                self.wait += 1

                await event.answer(_msg2, h,
                                   last_answer,
                                   self.score(),
                                   answer[0],
                                   self.help_qest(answer[1])
                                   ).send()
        else:
            return False

    def upd(self):
        self.end()
        self._LAST_ANSWER = ''
        self._QEST_POINT = 0
        self._ADD_HELP = 0
        self._WRONG_ANSWER = 0
        self._ADD_HELP_LOCK = 0

    def _qest(self) -> list:
        code = f'SELECT * FROM qest WHERE id = {rnd.randint(0, 124410)};'
        connection = sqlite3.connect(f'db/qest.db')
        crsr = connection.cursor()
        crsr.execute(code)
        ans = crsr.fetchall()
        connection.close()
        ans = ans[0]
        return [ans[1], [ans[2]]]

    def score(self) -> str:
        s = '\nСчёт: ' + its(self._QEST_POINT)
        l = '\nЖизней: ' + its(self._L - self._WRONG_ANSWER)
        h = '\nПодсказок: ' + its(self._H - self._ADD_HELP)
        return s + l + h + '\n'

    def get_top(self, p) -> str:
        tempdict = {}
        for i in _BD.get_all(sync=True):
            if tempdict.get(i[0], 0) <= i[1]:
                tempdict[i[0]] = i[1]

        b = sorted(tempdict.items(), key=itemgetter(1), reverse=True)[0]
        tempdict[self.user_id] = p
        point = sorted(tempdict.items(), key=itemgetter(1), reverse=True)

        ind = 0
        for i in point:
            ind += 1
            if i[0] == self.user_id:
                break

        if b[0] == self.user_id:
            t = f'лучший результат пренадлежит тебе {its(b[1])}!'
        else:
            s = _BD_USERDATA.get(b[0], item='fname', sync=True)
            s = s[0][0]
            t = f'лучший результат у - {s} {its(b[1])}'

        return f'занимаешь {its(ind)} место среди {its(len(point))} участников игры, {t}'

    def help_qest(self, answer, level=1) -> str:
        rer = []
        lq = '\n\nПодсказка: ' + answer[0][0]
        if self._ADD_HELP > 10 or self._ADD_HELP_LOCK != 0:
            hq = ''
        else:
            hq = '\n\nЕсли не помогло пиши "подсказка"'

        if len(answer[0]) > 4 or level != 1:
            f = 0
            while f < level:
                r = rnd.randint(0, len(answer[0]) - 2)
                if r not in rer:
                    rer.append(r)
                    f += 1
            ind = 0
            word = ''
            for i in answer[0][1::]:
                if ind in rer:
                    word += i
                elif i == ' ':
                    word += ' '
                else:
                    word += '*'
                ind += 1
            return lq + word + hq

        else:
            return lq + '*' * (len(answer[0]) - 1) + hq

    async def mainapp(self, event: Event) -> Event:
        for task in qest_tasks:
            if task.done():
                qest_tasks.remove(task)

        message = re.quest1.sub('', event.text).upper().strip()

        if event.stoper():
            point = self._QEST_POINT
            self.upd()
            await _BD.put(self.user_id, point)

            if point:
                return event.answer(_msg3,
                                    event.gender("", "а"),
                                    its(point),
                                    self.get_top(point))
            else:
                return event.answer(str_menu_out)

        if self.isstep(0, 1):
            return event.answer(_msg4, self.username).keyboard(*keyb3)

        if self.isstep(1000):
            if event.check('ДА'):
                self.upd()
                self.setstep(2)
                answer = self._qest()
                self._LAST_ANSWER = answer[1]

                qest_tasks.append(asyncio.create_task(self.waits(event, self.wait)))
                return event.answer(_msg5, answer[0], self.help_qest(answer[1])).keyboard(*keyb)

            elif event.check('СЛОЖНОСТЬ', 'ИНФО'):
                self.setstep(1)

            else:
                self.upd()
                return event.answer(_msg6).keyboard()

        if self.isstep(1):
            if event.check('ИНФО', '!ИНФО'):
                event.keyboard(*keyb3).attachment(id_doc_logo)
                return event.answer(_msg7, self.username,
                                    self._T, self._H,
                                    self._L, self.level.lower())

            if event.check('СЛОЖНОСТЬ'):
                return event.answer(_msg8).keyboard(*keyb5)

            if event.check(*qlevl):
                message = re.quest1.sub('', event.text).upper().strip()
                self._T = qlevl[message][0]
                self._H = qlevl[message][1]
                self._L = qlevl[message][2]
                self._PP = qlevl[message][3]
                self._WA = qlevl[message][4]
                self.level = message
                return event.answer(_msg9, event.gender('', 'а'), message.lower()).keyboard(*keyb3)

            if event.check('ДА'):
                self.setstep(2)
                answer = self._qest()
                self._LAST_ANSWER = answer[1]
                qest_tasks.append(asyncio.create_task(self.waits(event, self.wait)))
                return event.answer(_msg10, self._T, answer[0],
                                    self.help_qest(answer[1])).keyboard(*keyb)

            elif event.check('НЕТ'):
                self.upd()
                return event.answer(_msg11).keyboard()

            else:
                return event.answer(_msg12).keyboard(*keyb3)

        if self.isstep(2):
            if event.check('ПОДСКАЗКА'):
                if self._ADD_HELP >= self._L:
                    return event.answer(_msg13).keyboard(*keyb4)

                elif self._ADD_HELP_LOCK == 1:
                    return event.answer(_msg14).keyboard(*keyb2)

                else:
                    self._ADD_HELP_LOCK = 1
                    if self._WA:
                        if self._QEST_POINT >= self._WA:
                            self._QEST_POINT -= self._WA
                            h = f'➖{its(self._WA)} {word_point[self._WA]}'
                        else:
                            h = ''
                    else:
                        h = ''
                    self._ADD_HELP += 1
                    ln = self._LAST_ANSWER
                    out = self.help_qest(ln, level=int(len(ln[0]) // 2))
                    return event.answer(f'{out}\n\n{h}{self.score()}').keyboard(*keyb2)

            qest_tasks.append(asyncio.create_task(self.waits(event, self.wait + 1)))
            self.wait += 1

            hide = event.check('ПРОПУСТИТЬ')

            LAST_ANSWER = []
            for i in self._LAST_ANSWER:
                LAST_ANSWER.append(i.lower())

            if len(message) >= 5:
                if until.distance(message.lower(), ' '.join(LAST_ANSWER)) < 2:
                    message = LAST_ANSWER[0]

            if message.lower() in LAST_ANSWER:
                self._ADD_HELP_LOCK = 0
                self._QEST_POINT += self._PP
                answer = self._qest()
                self._LAST_ANSWER = answer[1]
                return event.answer(_msg15, its(self._PP), word_point[self._PP],
                                    self.score(), answer[0], self.help_qest(answer[1])
                                    ).keyboard(*keyb)
            else:

                self._ADD_HELP_LOCK = 0
                if self._WRONG_ANSWER >= self._H:
                    point = self._QEST_POINT
                    self.setstep(1000)
                    await _BD.put(self.user_id, point)
                    head = '🚫 Неправильно, п'
                    if hide:
                        head = 'П'

                    return event.answer(_msg16, head, event.gender("", "ла"),
                                        its(point), self.get_top(point)
                                        ).keyboard(*keyb3)

                else:
                    head = '🚫 Неправильно, в'
                    if hide:
                        head = 'В'
                    if self._QEST_POINT >= self._PP:
                        self._QEST_POINT -= self._PP
                        head = f'🚫 Неправильно ➖{its(self._PP)} {word_point[self._PP]}, в'
                        if hide:
                            head = f'➖{its(self._PP)} {word_point[self._PP]}, в'
                    self._WRONG_ANSWER += 1
                    last_answer = self._LAST_ANSWER[0]
                    answer = self._qest()
                    self._LAST_ANSWER = answer[1]

                    return event.answer(_msg17, head, last_answer, self.score(),
                                        answer[0], self.help_qest(answer[1])
                                        ).keyboard(*keyb)
