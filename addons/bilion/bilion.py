# -*- coding: utf-8 -*-
import random
from untils import req, until, Event
from Sqlbd import Sqlbd
from Addon import Addon, addon_init
from Template import str_error, str_maybe_later, str_menu_out, str_back, str_no, str_yes
import ujson as json
import pickle
from operator import itemgetter

its = until.int_to_smail

with open('addons/bilion/dump_qest', 'rb') as wr:
    baza = pickle.load(wr, encoding="bytes")

_levelkeyb = ['Детё =)%b', 'Стандарт%b', 'Подобный богу%b', str_back]
keyb = ['🔄Пропустить%b', str_back]
keyb2 = [str_yes, str_no, str_back]

_H = 3  # количество подсказок
_L = 3  # жизни


level_str = 'Отлично! Выбери уровень сложности:\n1. Детё =)\n2. Стандарт\n3. Подобный богу'

_msg1 = 'Поиграли и хватит, выходим в главное меню)\nТы набрал{} {} очков{}'
_msg2 = '➖{} очко\n{}'
_msg3 = 'Один вопрос, одна подсказка 😝'
_msg4 = 'Подсказки закончились =('
_msg5 = '{}, хочешь поиграть в "Кто хочет стать миллионером"?\nДА или НЕТ'
_msg6 = '{}, ты выбрал{} уровень сложности: {}\n\nПервый вопрос:\n{}'
_msg7 = '✅ Правильно!\nНачислено ➕{} очка{}\nСледующий вопрос:\n{}'
_msg8 = '{}опытки кончились\nверный ответ - {}, игра окончена 😊\nТы набрал{} {} очков и {}\n\nПовторим? Да или НЕТ'
_msg9 = '{}{}{}ерный ответ - {}{}\nСледующий вопрос:\n{}'


_BD = Sqlbd('bilion')
_BD_USERDATA = Sqlbd('userdata')


@addon_init(['!миллионер'], '🕹', False, 1)
class Bilion(Addon):
    __slots__ = ('level', 'answer', '_QEST_POINT', '_WRONG_ANSWER', 'username',
                 'user_id', '_step', 'helper', 'help_point', 'help_lock')

    def __init__(self, username, user_id):
        super(Bilion, self).__init__(username, user_id)
        self.level = '1'
        self.answer = ''
        self._QEST_POINT = 0
        self._WRONG_ANSWER = 0
        self._step = 0
        self.helper = []
        self.help_point = 0
        self.help_lock = 0

    def upd(self):
        self.end()
        self.level = '1'
        self.answer = ''
        self._QEST_POINT = 0
        self._WRONG_ANSWER = 0
        self._step = 0
        self.help_point = 0

    def score(self):
        s = '\nВаш счёт: ' + its(self._QEST_POINT)
        l = '\nЖизней: ' + its(_L - self._WRONG_ANSWER)
        h = f'\nПодсказок 50/50: ' + its(_H - self.help_point)
        return s + l + h + '\n'

    def help(self, event):
        ind = 0
        temp = []

        print(self.helper)

        for i in self.helper:
            ind += 1
            temp.append([i, str(ind)])
        while True:
            a = temp[random.randint(0, len(self.helper) - 1)]
            if a[0].lower() != self.answer[0]:
                break

        if int(a[1]) < int(self.answer[1]):
            event.keyboard(a[1] + '%b', self.answer[1] + '%b', *keyb)
            return ('Подсказка:\n' + a[1] + '. ' + a[0] + '\n'
                    + self.answer[1] + '. ' + self.answer[0].capitalize())
        else:
            event.keyboard(self.answer[1] + '%b', a[1] + '%b', *keyb)
            return ('Подсказка:\n' + self.answer[1] + '. '
                    + self.answer[0].capitalize() + '\n' + a[1] + '. ' + a[0])

    def get_top(self, p):
        tempdict = {}
        for i in _BD.get_all(key='lvl', val=self.level, sync=True):
            if tempdict.get(i[0], 0) <= i[1]:
                tempdict[i[0]] = i[2]

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
            if s:
                s = s[0][0]
            else:
                s = 'Админ'
            t = f'лучший результат у - {s} {its(b[1])}'

        l = {4: 'Детё', 1: 'Стандарт', 5: 'Подобный богу'}

        return (f'занимаешь {its(ind)} место среди {its(len(point))} участников игры '
                f'на уровне сложности {l.get(int(self.level),"Ошибка")}, {t}')

    def answerkeyb(self, count, event):
        """генерация клавиатуры в
        зависимости от количества
        вариантов"""
        a = [(str(i) + '%b') for i in range(1, count + 1)]
        event.keyboard(*a, '🔄Пропустить%b', '✂ 50/50%b', str_back)

    async def get_qetion(self, event):
        if int(self.level) < 5:
            url = 'https://engine.lifeis.porn/api/millionaire.php'
            val = {'q': self.level}
            print('get qetion')
            response = await req.get(url, params=val)
            response = json.loads(response.decode('utf-8'))['data']

            question = response['question'].replace('\u2063', '')
            answers = random.sample(response['answers'], 4)
            answer = response['answers'][response['id']]

            answ = ''
            ind = 1
            id_answer = 0
            self.answerkeyb(len(answers), event)
            # генерация клавиатуры в зависимости от количества вариантов
            self.helper = answers
            for i in answers:
                if i == answer:
                    id_answer = ind
                answ += '\n' + str(ind) + '. ' + i
                ind += 1
            print('get qetion ok')

        else:
            q = baza[random.randint(0, len(baza)-1)]
            question = q[0]
            answers = random.sample(q[1] + [q[2]], len(q[1]) + 1)

            answer = q[2]
            answ = ''
            ind = 1
            id_answer = 0
            self.answerkeyb(len(answers), event)  # генерация клавиатуры в зависимости от количества вариантов
            self.helper = answers
            for i in answers:
                if i == answer:
                    id_answer = ind
                answ += '\n' + str(ind) + '. ' + i
                ind += 1

        self.answer = [answer.lower(), str(id_answer)]

        data = question + '\n\nВарианты ответа:' + answ
        self._step += 1
        return data

    async def mainapp(self, event: Event) -> Event:
        hide = event.check('ПРОПУСТИТЬ')

        if event.stoper():
            point = self._QEST_POINT
            await _BD.put(self.user_id, self._step, point, self.level)
            self.upd()
            if point:
                if self.isstep(1000):
                    end = ''
                else:
                    end = f' и {self.get_top(point)}'

                return event.answer(_msg1, event.gender("", "а"), its(point), end).keyboard()
            else:
                return event.answer(str_menu_out)

        if event.check('ПОДСКАЗКА', '50/50') and self.step > 2:
            if self.help_point < _H and self.help_lock == 0:
                self.help_lock = 1
                self.help_point += 1
                if self._QEST_POINT >= 1:
                    self._QEST_POINT -= 1
                    return event.answer(_msg2, its(1), self.help(event))
                else:
                    return event.answer(self.help(event))

            elif self.help_lock == 1:
                return event.answer(_msg3)

            else:
                self.answerkeyb(4, event)
                return event.answer(_msg4)

        if self.isstep(0, 1):
            return event.answer(_msg5, self.username).keyboard(*keyb2)

        if self.isstep(1, 2):
            if event.check('ДА'):
                return event.answer(level_str).keyboard(*_levelkeyb)
            else:
                self.upd()
                return event.answer(str_maybe_later).keyboard()

        if self.isstep(2):
            if event.check('детё', 'дете', '1'):
                self.level = '4'

            elif event.check('стандарт', '2'):
                self.level = '1'

            elif event.check('подобный богу', '3'):
                self.level = '5'

            else:
                return event.answer(str_error).keyboard(*_levelkeyb)

            self.setstep(3)
            # клава генерится в get_qetion()
            return event.answer(_msg6, self.username, event.gender("", "а"),
                                event.text, await self.get_qetion(event))

        if self.isstep(3):
            if event.check(*self.answer):
                self.help_lock = 0
                self._QEST_POINT += 3
                # клава генерится в get_qetion()
                return event.answer(_msg7, its(3), self.score(), await self.get_qetion(event))

            else:
                self.help_lock = 0
                if self._WRONG_ANSWER >= _L - 1:
                    self.setstep(1000)
                    # запись результата в бд
                    await _BD.put(self.user_id, self._step, self._QEST_POINT, self.level)
                    head = '🚫 Неправильно, п'
                    if hide:
                        head = 'П'

                    return event.answer(_msg8, head, self.answer[0], event.gender("", "а"),
                                        its(self._QEST_POINT), self.get_top(self._QEST_POINT)
                                        ).keyboard(*keyb2)

                else:
                    if self._QEST_POINT >= 3:
                        self._QEST_POINT -= 3
                        d = f'➖{its(3)} очка,'
                    else:
                        d = ''

                    self._WRONG_ANSWER += 1
                    # клава генерится в get_qetion()
                    h = '🚫 Неправильно, '
                    if hide:
                        h = ''

                    if not d and not h:
                        z = 'В'
                    else:
                        z = ' в'

                    return event.answer(_msg9, h, d, z, self.answer[0],
                                        self.score(), await self.get_qetion(event))

        if self.isstep(1000):
            if event.check('ДА'):
                self.upd()
                self.setstep(2)
                return event.answer(level_str).keyboard(*_levelkeyb)  # выбор клавы

            else:
                self.upd()
                return event.answer(str_maybe_later).keyboard()


