from Addon import Addon, addon_init, middelware
from untils import Event, get_proxy, logs
from Sqlbd import Sqlbd
from Template import str_back
from Models import DataBD_yam, DataUserBD_yam, Answer_yam, Comment_yam

from addons.fact.fact import Fact

from asyncio import create_task, gather, sleep
from datetime import datetime
import time
import os

from aiohttp import ClientSession
import ujson as json
from fake_useragent import UserAgent
from random import random
import re
from typing import List
from dataclasses import dataclass, field

re_t_scope = re.compile(r'<.*?>')
re_check_input_date = re.compile(r'(\d{1,2}.+\d{1,2}.+\d{4}.*?)+')
re_get_date = re.compile(r'\d+')


_BD = Sqlbd('yam', DataBD_yam)
_BD_USER = Sqlbd('yam_user', DataUserBD_yam)
_BD_ANSWERS = Sqlbd(Answer_yam)
_BD_COMMENT = Sqlbd(Comment_yam)


progress = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']


@dataclass
class Data_yam:
    id: int
    title: str
    url: str
    time: int
    from_type: str


@dataclass
class Question_data_yam:
    question: str
    data: List[Data_yam] = field(default_factory=list)


@dataclass
class ScanerParams:
    count: int
    offset: int
    user_id: str

    def get_dict(self):
        return {
            "n": str(self.count),
            "p": str(self.offset),
            "usrid": self.user_id,
            "urlname": self.user_id,
            "__urlp": "/v2/abrandans"
        }

    def next_offset(self):
        self.offset += self.count


def get_random_header():
    return {
        'User-Agent': UserAgent().chrome,
        'Accept': '*/*',
        'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'DNT': '1'
    }


async def get(url) -> str:
    await sleep(random() / 3 + 0.1)

    async with ClientSession() as session:
        async with await session.get(url,
                                     headers=get_random_header(),
                                     proxy=get_proxy(),
                                     timeout=60,
                                     ) as res:
            response = await res.text()

    return response


async def post(url, params) -> str:
    await sleep(random() + 0.1)

    async with ClientSession() as session:
        async with await session.post(url,
                                      data=params,
                                      headers=get_random_header(),
                                      proxy=get_proxy(),
                                      timeout=60
                                      ) as res:
            response = await res.text()

    return response


class MailQS:
    async def search_mail(self, _q: str, t: int = 0) -> Question_data_yam:
        # t1 = 3600 * 24
        # t2 = 3600 * 24 * 3
        # t3 = 3600 * 24 * 7
        # t4 = 3600 * 24 * 30

        q_data = Question_data_yam(_q)

        _t = f'&zdts=-{t}' if t else ''
        url = (f'https://otvet.mail.ru/go-proxy/answer_json?'
               f'q={_q}&'
               f'num=20&'
               f'sf=0&'
               f'zvstate=3{_t}&'
               f'question_only=1')

        try:
            res = await get(url)
            data = json.loads(res)

            results = data.get('results')
            if not results:
                return q_data

            for x in results:
                data = Data_yam(x['id'], re_t_scope.sub('', x['question']), x['url'], x['time'], 'm')
                q_data.data.append(data)

            return q_data

        except:
            logs.yam_error()
            return q_data

    def get_time_yandex(self, q: dict):
        tt = q.get('created')

        try:
            tt = tt.split('.')[0]
            tt = tt.split('+')[0]
            tt = datetime.strptime(tt, "%Y-%m-%dT%H:%M:%S")
            tm = int((datetime.now(tt.tzinfo) - tt).total_seconds())
        except:
            tm = 0
            logs.yam_error()

        return tm

    async def search_yandex(self, _q: str, t: int = 0) -> Question_data_yam:
        url = ('https://yandex.ru/znatoki/web-api/aggregate/page/qExploreRoute?'
               'eventName=qExploreRoute&'
               f'text={_q}&'
               'tab=questions&'
               'exp_flags=new_quality,full_tag_info')

        q_data = Question_data_yam(_q)
        try:
            res = await get(url)

            data_json = json.loads(res)
            entities_question = data_json['entities'].get('question')

            if not entities_question:
                return q_data

            for x in data_json['result']['questions']['items']:
                try:
                    q = entities_question.get(x['id'])
                    if not q:
                        continue
                except:
                    logs.yam_error()
                    continue

                title = q.get('title')
                slug = q.get('slug')
                tm = self.get_time_yandex(q)

                if not title or not slug or tm > t:
                    continue

                data = Data_yam(x['id'], title, f'https://yandex.ru/q/question/{slug}/', tm, 'y')
                q_data.data.append(data)

        except:
            logs.yam_error()

        return q_data


YANDEX = 0b01
MAIL = 0b10
ALL = 0b11

ANSWER_OPEN = 0
ANSWER_READY = 1
ANSWER_VOTING = 2


MOSRU = 'mosru'


@addon_init(['!findyam', '!checkyam', '!commentyam', '!comentyam'], '', False, 0)
class Yam(Addon):
    __slots__ = 'stop', 'wats_pars', 'str_fact'

    def __init__(self, username, user_id):
        super(Yam, self).__init__(username, user_id)
        self.stop = False
        self.wats_pars = 0
        self.str_fact = ''

    async def progress_bar(self, j, event):
        if j and j % 7 == 0:
            fact_obj = Fact()
            self.str_fact = '\n\n' + await fact_obj.get()
        if j == 100:
            self.str_fact = ''

        await event.answer(f'Поиск {j}% {progress[j % len(progress)]}{self.str_fact}'
                           ).keyboard(str_back).send()

    async def get_questions(self, event, max_time_pars):
        await event.answer(f'Поиск старт...').keyboard(str_back).send()

        parser = MailQS()
        result_pars: List[Question_data_yam] = []

        with open('addons/yam/q.txt', encoding='utf-8') as f:
            qs = set(f.read().split('\n'))

        prev_progress_percent, progress_percent = 0, 0
        for iteration, patter_question in enumerate(qs):
            if not patter_question:
                continue
            if self.stop:
                self.end(event)
                return event.answer('stop')

            iter_task = []
            if self.wats_pars & YANDEX:
                iter_task.append(create_task(parser.search_yandex(patter_question, max_time_pars)))
            if self.wats_pars & MAIL:
                iter_task.append(create_task(parser.search_mail(patter_question, max_time_pars)))

            result_pars.extend(await gather(*iter_task))

            progress_percent = int(100 * (iteration / len(qs)))
            if progress_percent > prev_progress_percent:
                prev_progress_percent = progress_percent
                await self.progress_bar(progress_percent, event)

        await self.progress_bar(progress_percent + 1, event)

        out_string = ''
        temp: List[int] = []
        for q in [i for i in result_pars if i.data]:
            tmp = ''
            for i in q.data:
                try:
                    if i.id in temp:
                        continue

                    await _BD.put(DataBD_yam(q.question, str(i.id) + i.from_type,
                                             i.title, i.url, i.time))
                    temp.append(i.id)
                    tmp += f'\t{i.title} {i.url}\n'
                except:
                    logs.yam_error()
            if tmp:
                out_string += f'> {q.question}\n'
                out_string += tmp
                out_string += '\n'

        path_out = 'addons/yam/result.txt'

        with open(path_out, 'w', encoding='utf-8') as f:
            f.write(out_string)

        await event.uploads(path_out, 'file', caption='result.txt')
        return event.answer('Результат готов!')

    async def save_user_active(self, event: Event):
        await _BD_USER.put(DataUserBD_yam(event.user_id, int(time.time()), event.text))

    async def create_answer_obj(self, val: dict):
        qid = val['qid']
        aid = val['aid']
        answer_count = val['anscnt']
        user_id = val['qusrid']

        count_comment = await self.get_answer_comment_count(qid, aid, user_id)

        qstate = val['qstate']
        state = ANSWER_OPEN
        if qstate == 'R':
            state = ANSWER_READY
        elif qstate == 'V':
            state = ANSWER_VOTING

        return Answer_yam(aid, qid, state, answer_count, count_comment)

    def create_comment_obj(self, comment, time_at, id_question, id_answer) -> Comment_yam:
        id_comment = comment['cmid']
        text = comment['cmtext']
        nick = comment.get('nick', 'None')
        user_id = comment['usrid']
        return Comment_yam(id_comment, id_question, id_answer, time_at, text, nick, user_id)

    async def comment_save(self, comment: Comment_yam):
        if not await _BD_COMMENT.get(comment.id):
            await _BD_COMMENT.put(comment)

    async def comment_check_and_save(self, data, time_at, id_question, id_answer,
                                     user_id) -> List[Comment_yam]:
        comments = []

        if not data.get('comments'):
            return comments

        for comment in data['comments']:
            if int(comment['refid']) == int(id_answer) and int(user_id) != int(comment['usrid']):
                _comments = await self.comment_check_and_save(comment, time_at, id_question,
                                                              id_answer, user_id)
                comments.extend(_comments)

                comment_obj = self.create_comment_obj(comment, time_at, id_question, id_answer)
                comments.append(comment_obj)

                await self.comment_save(comment_obj)

        return comments

    async def get_target_comment(self, event: Event, date: str) -> Event:
        pars_date = re_get_date.findall(date)
        if len(pars_date) in (3, 6):
            for i, val in enumerate(pars_date):
                if len(val) == 1:
                    pars_date[i] = '0' + val

            try:
                ld = time.mktime(time.strptime(' '.join(pars_date[0:3]), '%d %m %Y'))
            except:
                return event.answer('С датой беда...').keyboard(str_back)

            if len(pars_date) == 6:
                try:
                    rd = time.mktime(time.strptime(' '.join(pars_date[3:6]), '%d %m %Y'))
                except:
                    return event.answer('С датой беда...').keyboard(str_back)
            else:
                rd = int(time.time())

            ans: List[Comment_yam] = await _BD_COMMENT.get_between('time_add', ld, rd)
            if ans:
                data_str = ''
                for comment in ans:
                    data_str += (f'https://otvet.mail.ru/answer/{comment.qid}/cid-{comment.id}\n'
                                 f'{comment.nick}\n'
                                 f'{comment.text}\n\n')

                file_name = str(time.time()) + '.txt'
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(data_str)

                await event.uploads(file_name, 'file', caption='result.txt')

                os.remove(file_name)
                return event.answer('Результат готов!')

            else:
                return event.answer('Нет комментариев в заданный промежуток времени!').keyboard(str_back)

        else:
           return event.answer('Циферок маловато...').keyboard(str_back)

    async def pars_comment(self, data, id_question, id_answer, user_id):
        if not data.get('comments'):
            return 0

        time_at = int(data['created_at'])

        comments = await self.comment_check_and_save(data, time_at, id_question, id_answer, user_id)

        return len(comments)

    async def get_answer_comment_count(self, id_question, id_answer, user_id) -> int:
        params = {
            "qid": str(id_question),
            "n": "10",
            "p": "0",
            "sort": "1",
            "__urlp": "/v2/question"
        }
        resp = await post('https://otvet.mail.ru/api/', params)
        data = json.loads(resp)

        return await self.pars_comment(data, id_question, id_answer, user_id)

    async def worker(self, answer: dict, answers_list: list):
        ans: Answer_yam = await self.create_answer_obj(answer)

        bd_ans: List[Answer_yam] = await _BD_ANSWERS.get(ans.id)

        if bd_ans and bd_ans[0].comment_count < ans.comment_count:
            answers_list.append(ans)
            await _BD_ANSWERS.up(ans.id, comment_count=ans.comment_count)

        if not bd_ans and ans:
            await _BD_ANSWERS.put(ans)

    async def get_all_profile_answers_mail(self, event: Event) -> List[Answer_yam]:
        await event.answer(f"Просмотренно ответов:\n0 из ~4500"
                           ).keyboard(str_back).send()

        params = ScanerParams(100, 0, MOSRU)
        answers_list = []

        error_count = 0
        while error_count < 10:
            try:
                resp = await post('https://otvet.mail.ru/api/', params.get_dict())
                params.next_offset()

                data = json.loads(resp)

                assert data and data['status'] == 200

                if not data['answers']:
                    break

                answers = data['answers']

                batch_size = 15
                for i in range(0, len(answers), batch_size):
                    task = []
                    for answer in answers[i:i+batch_size]:
                        task.append(create_task(self.worker(answer, answers_list)))

                    await gather(*task)

                error_count = 0

                await event.answer(f"Просмотренно ответов:\n{params.offset} из ~4500"
                                   ).keyboard(str_back).send()

                await sleep(random() * 3 + 0.3)

            except:
                logs()
                error_count += 1
                await sleep(20)
                continue

        return answers_list

    def end(self, event: Event = None):
        self.setstep(0)
        self.stop = True

    @middelware
    async def mainapp(self, event: Event) -> Event:
        await self.get_answer_comment_count(203787670, 1884138533, 236594960)


        await self.save_user_active(event)

        if not event.from_telegram:
            return event.answer('Только в телеграмм...')

        if event.check('!checkyam'):
            self.setstep(5)
            return event.answer('Что смотреть?').keyboard('Mail', str_back, tablet=1)

        if event.check('!commentyam', '!comentyam'):
            self.setstep(6)
            return event.answer('За какое время?\n\nпример даты:\n09.08.2021 19.08.2021\n'
                                'или:\n'
                                '09.08.2021\n'
                                'если до текуще даты\n\n'
                                'P.S. вместо точки может быть любой символ.').keyboard(str_back)

        if self.isstep(0, 1):
            return event.answer('Что парсить?').keyboard('Yandex', 'Mail',
                                                         'Всё сразу', str_back, tablet=1)

        if self.isstep(1, 2):
            if event.check('Yandex'):
                self.wats_pars = YANDEX
            elif event.check('Mail'):
                self.wats_pars = MAIL
            else:
                self.wats_pars = ALL

            return event.answer('За какой период?').keyboard('3 дня', '5 дней', '7 дней', '30 дней',
                                                             '90 дней', str_back, tablet=1)

        if self.isstep(2):
            t = 0
            if event.check('3 дня'):
                t = 3

            if event.check('5 дней'):
                t = 5

            if event.check('7 дней'):
                t = 7

            if event.check('30 дней'):
                t = 30

            if event.check('90 дней'):
                t = 90

            return await self.get_questions(event, 3600 * 24 * t)

        if self.isstep(5) and event.check('Mail'):
            val = await self.get_all_profile_answers_mail(event)

            a = ''.join([f'https://otvet.mail.ru/question/{i.qid}\n' for i in val])

            if a:
                return event.answer('Новые комментарии в вопросах:\n\n' + a)

            else:
                return event.answer('Новых комментариев нет')

        if self.isstep(6):
            date = re_check_input_date.findall(event.text)
            if date:
                return await self.get_target_comment(event, date[0])

            else:
                return event.answer('дата не верна...').keyboard(str_back)

