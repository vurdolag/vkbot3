# -*- coding: utf-8 -*-
from untils import until, req, Event
from Addon import Addon, middelware, addon_init
from Template import str_back, str_yes, str_no, str_maybe_later
import recompile as rec
import lxml.html
from lxml import etree
import asyncio
import random as rnd
import itertools

_p1 = 'Сложность%b'

keyb = [str_back]
keyb2 = [str_yes, str_no, _p1]
keyb3 = ['Ещё вопрос%g', _p1, str_back]
keyb4 = ['очень простой', 'простой', 'средний', 'сложный', 'очень сложный']


class Qest:
    qestion = {}

    __slots__ = ()


lvl_dict = {
    'очень простой': 1,
    'простой': 2,
    'средний': 3,
    'сложный': 4,
    'очень сложный': 5
     }

_msg1 = 'Хочешь сыграть в Что? Где? Когда?\nНачнем?'
_msg2 = 'Очень простой\nПростой\nСредний\nСложный\nОчень сложный'
_msg3 = 'Выбран {}\n\nНачинаем?'
_msg4 = 'Выбери одно из:\n\nОчень простой\nПростой\nСредний\nСложный\nОчень сложный'
_msg5 = 'Пиши:\nДа - для начала игры\nСложность - для выбора уровня сложности\nНазад - чтобы выйти в меню бота'


@addon_init(['!что где когда', '!чгк'], '❓', False, 1)
class Chgk(Addon):
    __slots__ = 'answer', 'authors', 'comments', 'notices', 'type_q', 'questionid', 'level', 'atta'

    def __init__(self, username, user_id):
        super(Chgk, self).__init__(username, user_id)
        self.answer = ''
        self.authors = ''
        self.comments = ''
        self.notices = ''
        self.type_q = ''
        self.questionid = 0
        self.level = 1
        self.atta = []

    async def get_chgk_random(self, naw=False):
        if not Qest.qestion or naw or not Qest.qestion[self.level]:
            level = {}

            for key in range(1, 6):
                all = []
                res = await req.post(f'https://db.chgk.info/random/complexity{key}/', timeout=15)
                tree = lxml.html.fromstring(res.decode('utf-8'))
                tour = []
                qestion_pack = tree.xpath('//*[@class="random_question"]//@href')
                for i in qestion_pack:
                    if 'tour' in i:
                        tour.append('https://db.chgk.info/' + i + '/xml')

                response = await asyncio.gather(*[asyncio.create_task(req.get(j, timeout=10)) for j in tour])

                for j in response:
                    root = etree.fromstring(j)
                    for appt in root.getchildren():
                        x = {}
                        for elem in appt.getchildren():
                            if elem.text:
                                x[elem.tag] = elem.text
                        if x:
                            all.append(x)
                level[key] = all
            Qest.qestion = level

    async def get_img(self, txt):
        try:
            self.atta += ['https://db.chgk.info/images/db/' + i[6:-1] for i in rec.chgk3.findall(txt)]
        except:
            pass

        return rec.chgk3.sub('', txt)

    async def get(self):
        while True:
            try:
                rnd.shuffle(Qest.qestion[self.level])
                q = Qest.qestion[self.level].pop()
            except:
                await self.get_chgk_random(naw=True)
                rnd.shuffle(Qest.qestion[self.level])
                q = Qest.qestion[self.level].pop()

            self.answer = rec.space.sub(' ', rec.chgk1.sub(' ', q.get('Answer', ''))).strip()

            n_sub = lambda x: rec.n_symbol.sub(' ', x).strip()
            self.authors = n_sub(q.get('Authors', ''))
            self.comments = n_sub(q.get('Comments', ''))
            self.notices = n_sub(q.get('Notices', ''))
            self.type_q = q.get('Type', '')
            self.questionid = q.get('QuestionId', 0)

            out = rec.chgk2.sub(' ', q.get('Question', ''))
            out = rec.space.sub(' ', out)
            if 'раздатка' in out or 'блиц' in out:
                continue
            out = await self.get_img(out)
            return out

    def check(self, a, b):
        size = len(a) + len(b)
        return round(((size - until.distance(a, b)) / size) * 100, 2)

    def prep_answer(self):
        all = []
        out = []
        for i in [i for i in self.answer.lower().split(',')]:
            all += [rec.chgk5.sub('', j)for j in rec.chgk4.findall(i) + [rec.chgk4.sub('', i)]]

        for l in range(1, len(all) + 1):
            out += list(map(" ".join, itertools.combinations(all, l)))

        out.sort(key=lambda x: len(x), reverse=True)
        return out

    async def qest(self, event):
        event.answer(await self.get()).keyboard(*keyb3)
        if self.atta:
            await event.uploads(self.atta)
        return event

    async def ans(self, event, c, txt='✅ П'):
        answer = await self.get_img(self.answer)
        comments = await self.get_img(self.comments)
        notices = await self.get_img(self.notices)

        if self.atta:
            await event.uploads(self.atta)

        return event.answer(f'{txt}равильно!'
                            f'\n\nОтвет: {answer if answer else "-"}' +
                            (f"\n\nКоммент: {comments}" if comments else "") +
                            (f"\n\nЗаметка: {notices}" if notices else "") +
                            f"\n\nCовпадение: {c}% из 75%"
                            ).keyboard(*keyb3)

    @middelware
    async def mainapp(self, event: Event) -> Event:
        await self.get_chgk_random()
        self.atta = []

        if self.isstep(0, 1):
            return event.answer(_msg1).keyboard(*keyb2)

        if event.check('сложность'):
            self.setstep(5)
            return event.answer(_msg2).keyboard(*keyb4)

        if event.check('ещё вопрос'):
            return await self.qest(event)

        if event.check('да'):
            self.setstep(2)
            return await self.qest(event)

        if event.check('нет'):
            self.end()
            return event.answer(str_maybe_later)

        if self.isstep(5):
            s = lvl_dict.get(event.text.lower(), 0)
            if s:
                self.level = s
                self.setstep(2)
                return event.answer(_msg3, event.text).keyboard(*keyb2)
            else:
                return event.answer(_msg4).keyboard(*keyb4, tablet=1)

        if self.isstep(2):
            pers = []
            for j in self.prep_answer():
                j = rec.space.sub(' ', j.strip())
                i = self.check(j, event.text.lower().strip())
                pers.append(int(i))
                if i >= 75:
                    return await self.ans(event, i)

            return await self.ans(event, int(sum(pers)/len(pers)), '❌ Не п')

        return event.answer(_msg5).keyboard(*keyb2)





