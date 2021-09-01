# -*- coding: utf8 -*-
from textdistance import damerau_levenshtein as dist
from aiohttp import FormData, web, client_exceptions, ClientSession
from asyncio import CancelledError, TimeoutError
import aiohttp_jinja2
import jinja2
import random as rnd
import ujson as json
from Template import str_help
import vk_api
import asyncio
import time
import config
import recompile as re
import re as regex
import io
import traceback
import sys
import base64
from datetime import datetime
from tzlocal import get_localzone
from time import strftime, localtime
from fake_useragent import UserAgent
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, List, Union, Coroutine, Dict, Tuple

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


UNI = Union[int, float, str]

TIME_ZONE = 10800


def get_local_time_offset():
    tz = get_localzone()
    d = datetime.now(tz)
    utc_offset = d.utcoffset().total_seconds()
    if utc_offset != tz:
        return TIME_ZONE - utc_offset
    else:
        return TIME_ZONE


TIME_OFFSET = get_local_time_offset()


def get_proxy():
    p = rnd.choice(config.proxy)
    return f'http://{p}' if not 'http://' in p else p


class TimeBuffer:
    __slots__ = '_time_buffer_dict', 'key_prefix'

    def __init__(self, key_prefix: str = ''):
        self.key_prefix = key_prefix
        self._time_buffer_dict = {}

    async def _time_buffer(self, key, time_s):
        key = self.key_prefix + key
        val = self._time_buffer_dict.get(key)
        if not val:
            count, acc_time = 0, 0
        else:
            count, acc_time = self._time_buffer_dict.get(key)

        count += 1
        acc_time += time_s, 2

        self._time_buffer_dict[key] = (count, acc_time)

        await asyncio.sleep(acc_time)

        count, acc_time = self._time_buffer_dict[key]

        count -= 1
        if count - 1 < 0:
            acc_time = 0
            count = 0

        self._time_buffer_dict[key] = (count, acc_time)

    def __call__(self, key, time_s) -> Coroutine:
        return self._time_buffer(key, time_s)

    def __getattr__(self, item):
        return lambda time_s: self._time_buffer(item, time_s)


time_buffer = TimeBuffer()


class Logger:
    """
    logging errors with full traceback

    logs = Logger()

    try:
        your code
    except:
        logs() # write error path ./logs/log.txt
        logs.name_log_file()  # write error path ./logs/name_log_file.txt

    logs("any_msg")  # write msg path ./logs/log.txt
    logs.name_log_file("any_msg")  # write msg path ./logs/name_log_file.txt
    """

    __slots__ = 'level', '_path'

    def __init__(self, _level=None, path='logs'):
        self.level = _level
        self._path = path

    def __getattr__(self, item):
        return lambda string='': self._logs(string, item + '.txt')

    def __call__(self, *args, **kwargs):
        self._logs(*args, **kwargs)

    def cool_trace(self, trace):
        t = trace.split('\n')
        out = []
        temp = ''
        path = sys.path[0].replace('\\', '/')
        for i in t:
            i = i.replace('\\', '/')
            if 'Traceback (most recent call last)' in i:
                continue
            if 'File "' in i and '", line ' in i:
                if path in i:
                    i = re.log1.findall(i)[0]
                    i = re.log2.sub('', i)
                temp += i + ' ->'
            else:
                temp += ' ' + i.strip()
                out.append(temp.strip())
                temp = ''

        return '\t' + '\n\t'.join(out)

    def get_title(self):
        return f'> {strftime("%y-%m-%d %H:%M:%S", localtime(time.time() + TIME_OFFSET))} =>'

    def _logs(self, strings: str = '', name: str = 'logs_error.txt'):
        """
        Логер и отлов ошибок, печатает полный трейсбек
        :param strings:
        :param name:
        """
        path = f'{self._path}/{name}'
        log_string = ''

        if strings:
            log_string = f'{self.get_title()} {strings}\n'

        else:
            a = sys.exc_info()
            if a and a[0] is KeyboardInterrupt or a[0] is CancelledError:
                pass
            else:
                trace = f'ERROR!\n{self.cool_trace(traceback.format_exc())}\n'
                log_string = f'{self.get_title()} {trace}'
                print(trace)

        with open(path, 'a', encoding='utf-8') as f:
            f.write(log_string)

    def log(self, string, name='log.txt'):
        self._logs(string, name)


logs = Logger()


from Sqlbd import Sqlbd
from Models import UserDataBD


def async_timer(func):
    async def wrapper(*arg, **kw):
        t1 = time.time()
        res = await func(*arg, **kw)
        print(round(time.time() - t1, 5), func.__name__)
        return res

    return wrapper


def timer(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        print(time.time() - t1, func.__name__)
        return res

    return wrapper


def smart_re(q: str) -> regex.compile:
    c = Global.re_dict.get(q)
    if not c:
        c = regex.compile(q)
        Global.re_dict[q] = c
    return c


def smart_re_tuple(q: tuple, full=False) -> regex.compile:
    c = Global.re_dict.get(q)
    if not c:
        if full:
            c = regex.compile(f'(^{"$|^".join(q)}$)'.lower())
        else:
            c = regex.compile(f'({"|".join(q)})'.lower())
        Global.re_dict[q] = c
    return c


class req:
    session = None

    __slots__ = ()

    @staticmethod
    async def init_session():
        if req.session is None:
            req.session = ClientSession()

    @staticmethod
    async def get(url: str, params: dict = None, data=None, headers=None, timeout=30, proxy=None) -> bytes:
        await req.init_session()

        async with await req.session.get(url, params=params, data=data, headers=headers, timeout=timeout,
                                         proxy=proxy) as res:
            resp = await res.read()
        return resp

    @staticmethod
    async def post(url: str, params: dict = None, data=None, headers=None, timeout=30, proxy=None) -> bytes:
        await req.init_session()
        async with await req.session.post(url, params=params, data=data, headers=headers, timeout=timeout,
                                          proxy=proxy) as res:
            resp = await res.read()
        return resp


bd_time_send = Sqlbd('time_send')


class subscribe:
    __slots__ = ()

    @staticmethod
    def create(key, event, command, keyboard='', t=0, global_t=0):
        if not t and not global_t:
            t = (time.time() + TIME_OFFSET) % (3600 * 24) - 300

        if keyboard:
            if not isinstance(keyboard, list):
                keyboard = list(keyboard)
            keyboard = '&'.join(keyboard)
        return bd_time_send.put(key, event.group_id, event.user_id, t,
                                command, keyboard, global_t, sync=True)

    @staticmethod
    def delete(key, event):
        return bd_time_send.delete(f'type_key = "{key}" AND user_id = '
                                   f'{event.user_id} AND group_id = {event.group_id}', sync=True)


class Global:
    re_dict: dict = {}
    user: dict = {}
    check_content = {}
    social_tmp: dict = {}
    loop_tasks: list = []
    iam_token: str = ''
    iam_token_last_update: int = 0

    from cover.Cover import CoverCreator
    cover: CoverCreator = None

    __slots__ = ()

    @staticmethod
    def start_task(coro):
        Global.loop_tasks.append(asyncio.create_task(coro))

    @staticmethod
    async def time_sender(event_processing):
        t_send = time.time()
        while True:
            await asyncio.sleep(30)
            try:
                tim = time.time()
                if tim - t_send > 120:
                    t = (tim + 3600 * 3) % (3600 * 24)
                    tim -= t_send
                    t_send = time.time()
                    data_time_send = await bd_time_send.get_between('time', t, t + tim)
                    global_time_send = await bd_time_send.get_between('global_time', t_send, t_send + tim)
                    keyb = [str_help]
                    if data_time_send:
                        for dat in data_time_send:
                            event = Event(dat[2], dat[4])
                            try:
                                event.social = Global.social_tmp[dat[1]]
                                print(dat)
                            except:
                                continue
                            event.group_id = dat[1]
                            event.time_send = True
                            if await event.messages_allowed():
                                if dat[5]:
                                    keyb = dat[5].split('&') + keyb
                                event.keyboard(*keyb, f'Отписаться {dat[0]}%r', tablet=1)
                                Global.start_task(event_processing(event))
                            else:
                                del event

                    if global_time_send:
                        for dat in global_time_send:
                            event = Event(dat[2])
                            try:
                                event.social = Global.social_tmp[dat[1]]
                                print(dat)
                            except:
                                continue
                            event.group_id = dat[1]
                            if await event.messages_allowed():
                                if dat[5]:
                                    keyb = dat[5].split('&') + keyb
                                txt = re.n_symbol.sub('\n', dat[4])
                                await event.answer(txt).keyboard(*keyb).send()
                            del event
            except:
                logs()

    @staticmethod
    def clear_task_list():
        for task in Global.loop_tasks:
            if task.done():
                Global.loop_tasks.remove(task)


class until:
    _last_time = time.time()

    __slots__ = ()

    @staticmethod
    def get_user_token() -> str:
        print('get user token')
        vk_session = vk_api.VkApi(config.user_login, config.user_pass, app_id=config.user_app_id)
        vk_session.auth()
        token = vk_session.token['access_token']
        return token

    @staticmethod
    def distance(a: str, b: str) -> int:
        return dist(a, b)

    @staticmethod
    def stoper(msg: str) -> bool:
        return msg.upper().strip() in ['↪НАЗАД В МЕНЮ', '⬅ НАЗАД', '!НАЗАД В МЕНЮ', 'НАЗАД В МЕНЮ', '/СТОП',
                                       '/В МЕНЮ', '/НАЗАД',
                                       '/НАЗАТ', '!НАЗАД',
                                       '!НАЗАТ', 'НАЗАД',
                                       'НАЗАТ']

    @staticmethod
    def re_del(r: str, txt: str):
        x = smart_re(r).sub('', txt.lower())
        return re.space.sub(' ', x).strip()

    @staticmethod
    def int_to_smail(x: int) -> str:
        x = str(x)
        smail = {'0': '0⃣',
                 '1': '1⃣',
                 '2': '2⃣',
                 '3': '3⃣',
                 '4': '4⃣',
                 '5': '5⃣',
                 '6': '6⃣',
                 '7': '7⃣',
                 '8': '8⃣',
                 '9': '9⃣'}
        out_int = ''
        for i in x:
            if i == '-':
                continue
            out_int += smail.get(i, '')

        if out_int:
            return out_int
        else:
            return x

    @staticmethod
    async def ya_dict(txt: str, lang='ru-ru') -> str:
        url = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'

        params = {'key': config.ya_dict,
                  'text': txt,
                  'lang': lang}
        try:
            response = await req.get(url, params=params)
            response = json.loads(response)
            return response

        except Exception as ex:
            print(ex)
            return 'Ошибка запроса на сервер, поробуй позже'

    @staticmethod
    async def wiki(text: str, ind=0) -> str:
        url = (f'https://ru.wikipedia.org//w/api.php?action=query&format=json&'
               f'prop=extracts&titles={await until.checker_text(text)}&exintro=1&utf8=1')
        try:
            res = await req.get(url)
            result = json.loads(res)['query']["pages"]
            result = result[list(result.keys())[0]]['extract']
            if not result:
                if ind:
                    return 'Ничего не нашел'
                else:
                    return await until.wiki(await until.translate(text, 'ru-en'), 1)

            result = re.wiki.sub('', ''.join('\n'.join(result.split('</p><p>'))))
            out = ''
            tmp = ''
            for string in result.split('\n'):
                if len(tmp + string) > 550:
                    out += tmp + ' ' * (550 - len(tmp))
                    tmp = ''
                    tmp += string + '\n'
                else:
                    tmp += string + '\n'
            return out + tmp[:-1]

        except:
            return 'Ничего не нашел...'

    @staticmethod
    async def checker_text(text: str) -> str:
        url = ('https://speller.yandex.net/services/spellservice.json/checkText?'
               f'text={text}')
        try:
            res = await req.get(url)
            result = json.loads(res)
            if result:
                ind = 0
                tmp = ''
                for word in result:
                    tmp += text[ind:word['pos']] + word['s'][0]
                    ind = word['pos'] + word['len']
                tmp += text[ind:]
                return tmp

            else:
                return text
        except:
            logs()
            return text

    @staticmethod
    async def _translate(txt: str, langs='en-ru', r=True) -> str:
        print('yandex translate')

        url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'

        iam_token = await until.get_iam_token()

        lang = langs.split('-')

        data = {
            "sourceLanguageCode": lang[0],
            "targetLanguageCode": lang[1],
            "texts": [txt],
            "folderId": "b1gb9k5cliueoqc4sg0t",
        }
        data = json.dumps(data)

        headers = {"Authorization": f"Bearer {iam_token}"}

        try:
            response = await req.post(url, headers=headers, data=data)
            response = json.loads(response)

            out = ''
            for i in response.get('translations', []):
                out += i.get('text', '') + ' '

            text = re.space.sub(' ', out).lower().capitalize()

            if not text and txt and r:
                Global.iam_token = await until.get_iam_token()
                text = await until._translate(txt, langs, False)

            return text

        except:
            logs()
            return 'Ошибка запроса на сервер, поробуй позже'

    @staticmethod
    async def translate(txt: str, langs='en-ru') -> str:
        try:
            head = {
                'User-Agent': UserAgent().chrome,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'DNT': '1'}

            async with ClientSession() as session:
                async with await session.post(
                        'https://fasttranslator.herokuapp.com/api/v1/text/to/text',
                        params={'source': txt, 'lang': langs},
                        proxy=get_proxy(),
                        headers=head) as res:
                    resp = await res.json()

            until._last_time = time.time()

            msg = resp.get('data')
            assert resp.get('status') == 200 and msg
            return msg

        except:
            logs()
            return await until._translate(txt, langs)

    @staticmethod
    async def get_iam_token() -> str:
        if not Global.iam_token or time.time() - Global.iam_token_last_update > 60 * 60 * 3:
            try:
                params = {"yandexPassportOauthToken": config.ya_moderation}
                res = await req.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', params=params)
                json_data = json.loads(res)
                return json_data.get('iamToken', '')
            except:
                logs()
                return ''
        else:
            return Global.iam_token

    @staticmethod
    async def moderation_img(img: bytes, r=1) -> dict:
        try:
            img = base64.b64encode(img).decode('utf-8')
            data = {
                "folderId": "b1gb9k5cliueoqc4sg0t",
                "analyze_specs": [{
                    "content": img,
                    "features": [{
                        "type": "CLASSIFICATION",
                        "classificationConfig": {
                            "model": "moderation"
                        }
                    }]
                }]
            }
            data = json.dumps(data)

            iam_token = await until.get_iam_token()

            res = await req.post('https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze',
                                 headers={"Authorization": f"Bearer {iam_token}"},
                                 data=data)

            res = json.loads(res)
            res = res['results'][0]['results'][0]['classification']['properties']
            d = {}
            for i in res:
                d[i['name']] = i['probability']
            return d

        except:
            logs()
            until.iam_token = await until.get_iam_token()
            if r == 1:
                return await until.moderation_img(img, r=0)
            return {}

    @staticmethod
    async def voice_to_text(voice_link: str) -> str:
        try:
            voice = await req.get(voice_link)
            iam_token = await until.get_iam_token()

            params = {
                'topic': 'general',
                "folderId": "b1gb9k5cliueoqc4sg0t",
                'lang': 'ru-RU'}
            headers = {"Authorization": f"Bearer {iam_token}"}
            res = await req.post('https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
                                 data=voice, headers=headers, params=params)
            res = json.loads(res)
            return res.get('result', '').lower()

        except:
            logs()
            return ''


bd_user = Sqlbd('userdata', UserDataBD)


class Event(until):
    __slots__ = (
        'user_id', '_text', 'text_out', 'attachments', 'attachments_out', 'name', 'last_name',
        'template', 'message_id', 'keyboards', 'sex', 'from_comment', 'from_telegram',
        'keyb_one_time', 'support_callback', 'support_keyb', 'support_keyb_inline',
        'owner_id', 'post_id', 'group_id', 'audio_msg', 'from_callback_button',
        'social', 'peer_id', 'time_send', 'from_chat', 'from_api', 'attachments_type',
        'from_user', 'empty', 'is_stop', 'is_can_edit_prev_msg', 'event_id'
    )

    def __init__(self, user_id, message='', attachments=None, message_id=0, post_id=0, owner_id=0):
        self.user_id: int = user_id
        self._text: str = message
        self.text_out: str = ''
        self.audio_msg: str = ''
        self.attachments: list = attachments
        self.attachments_out: str = ''
        self.message_id: int = message_id
        self.keyboards: str = ''
        self.template: str = ''
        self.sex: int = 0
        self.event_id: str = ''

        self.from_comment: bool = False
        self.from_chat: bool = False
        self.from_api: bool = False
        self.time_send: bool = False
        self.from_telegram: bool = False
        self.from_user: bool = False
        self.from_callback_button: bool = False

        self.attachments_type = self.atta_type()
        self.support_keyb: bool = True
        self.support_keyb_inline: bool = False
        self.support_callback: bool = False
        self.keyb_one_time: bool = False
        self.owner_id: int = owner_id
        self.post_id: int = post_id
        self.group_id: int = 0
        self.social: Optional[VkClass, Telegram] = None
        self.peer_id: int = self.user_id
        self.name: str = 'user_name'
        self.last_name: str = ''

        self.empty = True
        self.is_stop = False
        self.is_can_edit_prev_msg = True

    def __str__(self):
        return self.text

    def __add__(self, some_item):
        self.text_out += str(some_item)
        return self

    def __len__(self):
        return len(self._text) + len(self.text_out) + len(self.attachments_out)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    def answer(self, *args):
        if len(args) > 1:
            try:
                if not isinstance(args[0], str):
                    raise ValueError(f'First arg need be "str" got {type(args[0])}')
                self.text_out = args[0].format(*args[1:])
            except:
                logs()
        else:
            self.text_out = args[0]

        return self

    def answer_add(self, txt: str):
        self.text_out += txt
        return self

    def keyboard(self, *args, tablet=2, non_keyb=False):
        if not self.support_keyb or non_keyb or self.from_chat or self.from_comment:
            return self

        if not args:
            args = tuple([str_help])
        elif args[0] is None:
            return self

        keyb = VkKeyboards(
            one_time=not self.support_keyb_inline if not self.keyb_one_time else False,
            inline=self.support_keyb_inline
        )

        for ind, button in enumerate(args, 1):
            if not button:
                continue

            elif isinstance(button, str):
                keyb.add_button_from_string(
                    button,
                    button_type=Button.CALLBACK if self.support_callback else Button.TEXT,
                    payload=button
                )

            elif isinstance(button, Button):
                keyb.add_button_from_button(button)

            else:
                raise TypeError(f"BUTTON TYPE ERROR: {button}")

            if ind % tablet == 0 and ind != 0 and ind < len(args):
                keyb.add_line()

        if self.from_telegram:
            keyb.as_telegram()

        self.keyboards = keyb.get_keyboard()
        return self

    def attachment(self, atta: Union[str, List[str]]):
        if not isinstance(atta, list):
            atta = [atta]
        self.attachments_out = atta
        return self

    def atta_type(self):
        if self.attachments and not self.from_telegram:
            if not isinstance(self.attachments, list):
                self.attachments = [self.attachments]
            return self.attachments[0].get('type', '')

    def gender(self, arg1: str, arg2: str) -> str:
        return arg1 if int(self.sex) in (2, 0) else arg2

    def inline_keyb(self, arg1: str, arg2: str) -> str:
        return arg1 if self.support_keyb_inline else arg2

    def client_info(self, info: dict):
        self.support_keyb = info.get('keyboard', False)
        self.support_keyb_inline = info.get('inline_keyboard', False)
        self.support_callback = 'callback' in info.get('button_actions', [])

    def ids(self) -> str:
        h = 'from_api_' if self.from_api else ''
        return f'{h}{self.group_id}_{self.user_id}_{self.peer_id}'

    def set_typing(self, user_id=''):
        if (not self.from_comment and not self.from_api
                and not self.time_send and not self.from_telegram):
            self.social.set_typing(self, user_id)
        return self

    async def send(self, nonkeyb: bool = False, peer_id: int = 0, group: int = 0):
        if self.from_api:
            return self

        old_keyb = self.keyboards
        old_peer_id = self.peer_id

        if nonkeyb:
            self.keyboards = ''

        if peer_id:
            self.peer_id = peer_id

        if group:
            _group_id = self.group_id
            self.group_id = int(group)
            await Global.social_tmp[self.group_id].send(self)
            self.group_id = _group_id

        else:
            await self.social.send(self)

        self.text_out = ''
        self.keyboards = old_keyb
        self.peer_id = old_peer_id

        return self

    def get_user_info(self, user_id=0) -> Coroutine:
        if not self.from_telegram or self.from_api:
            return self.social.get_user_info(user_id if user_id else self.user_id)
        else:
            return self.social.get_user_info(self)

    def get_photo(self) -> Coroutine:
        return self.social.async_get_photo(self)

    async def uploads(self, path, type='photo', ret=False, caption='', telegram=''):
        """
        upload attach
        @param path:
        @param type:
        @param ret: if True return result else return Event
        @param caption:
        @param telegram:
        @return:
        """
        out = await self.social.uploads(path, self, type, caption, telegram)
        if ret:
            return out
        else:
            self.attachments_out = out
            return self

    def get_short_link(self, link: str) -> Coroutine:
        return self.social.get_short_link(link)

    def messages_allowed(self, user_id='', group_id='') -> Coroutine:
        return self.social.messages_allowed(self, user_id, group_id)

    def is_member(self, ids='') -> Coroutine:
        return self.social.is_member(self, ids)

    def search_doc(self, q: str = '', t: str = 'gif') -> Coroutine:
        return self.social.search_doc(q if q else self._text, t)

    def search_img(self, q: str = '') -> Coroutine:
        return self.social.search_img(q if q else self._text)

    def check(self, *args: str, full=False) -> bool:
        return len(smart_re_tuple(args, full).findall(self.text.lower())) != 0

    def check_re(self, pattern: str) -> bool:
        x = smart_re(pattern.lower()).findall(self.text.lower())
        return len(x) != 0

    def stoper(self) -> bool:
        self.is_stop = self.check('!НАЗАД В МЕНЮ', '!НАЗАД', '!НАЗАТ')
        return self.is_stop

    def re_del(self, pattern: str, txt: str = ''):
        x = self.text.lower() if not txt else txt.lower()
        self.text = smart_re(pattern).sub('', x).strip()
        return self

    async def save_user_info(self) -> List[UserDataBD]:
        user_info = await self.get_user_info(self.user_id)
        await bd_user.put(user_info)
        return [user_info]


class VkLoop:
    max_task: int = 24
    url: str = 'https://api.vk.com/method/'
    v_api: str = '5.130'

    __slots__ = ('owner_id', 'token', 'loop_is_start', 'name_id', 'tasks', 'response', 'is_user')

    def __init__(self, owner_id, token, is_user=False):
        self.owner_id: int = owner_id
        self.token: str = token

        self.loop_is_start: bool = False

        self.is_user = is_user

        self.name_id: int = 1
        self.tasks: List[str] = []
        self.response: Dict[int, dict] = {}

    def create_execute_code(self, task: List[str]) -> str:
        """Генератор кода VKScript для метода execute"""
        code = ['return [']
        for i in task:
            code.append(i)
        code.append('];')

        return ''.join(code)

    async def task_loop(self):
        """Запуск группы задач в execute_task() после достижения
        определённого времени после получения задачи или
        количества активных задач в task"""
        time_sleep = 0.34 if self.is_user else 0.05

        iter_count = 100

        while iter_count > 0:
            await asyncio.sleep(time_sleep)

            while self.tasks:
                code = self.create_execute_code(self.tasks[:self.max_task])
                self.tasks = self.tasks[self.max_task:]
                Global.start_task(self.execute_task(code))
                iter_count = 100
                await asyncio.sleep(time_sleep)

            iter_count -= 1

        self.loop_is_start = False

    async def error_catch(self, res: bytes, code: str = 'None'):
        try:
            res = json.loads(res)
        except:
            logs(f'json decode error: {res.decode("utf-8")}')
            return []

        execute_errors = res.get('execute_errors', 0)
        errors = res.get('error', 0)
        resp = res.get('response', [])

        if execute_errors:
            print(res)
            logs(f'execute_errors --> code ->{code}, error -> {res}')

        if errors:
            print(res)
            logs(f'errors --> code ->{code}, error -> {res}')
            await self.captcha(errors, code)

        return resp

    async def execute_task(self, code: str, add_params: dict = None) -> None:
        """Метод одновременной отправки группы задач с помощью execute"""
        try:
            params = {'v': self.v_api, 'access_token': self.token}

            if not add_params is None:
                params.update(add_params)

            res = await req.post('https://api.vk.com/method/execute', params=params, data={'code': code})
            resp = await self.error_catch(res, code)

            if resp:
                for i in resp:
                    if i[1] == 0:
                        continue
                    else:
                        self.response[i[1]] = i[0]
        except:
            logs()

    async def captcha(self, errors: dict, code: str) -> bool:
        if errors.get('error_msg', 0) == 'Captcha needed':
            logs(f'Captcha find')

            captcha_sid = errors['captcha_sid']
            captcha_img = errors['captcha_img']

            url = 'https://rucaptcha.com/in.php'

            data = await req.get(captcha_img)

            data = base64.b64encode(data).decode("utf-8")
            for _ in range(10):
                response = await req.post(url,
                                          params={'key': config.captcha,
                                                  'method': 'base64',
                                                  'json': 1,
                                                  'body': data})

                response = json.loads(response)
                ids = response.get('request', 0)
                url = 'https://rucaptcha.com/res.php'
                captcha_key = ''

                for _ in range(12):
                    await asyncio.sleep(5)
                    res = await req.get(url, params={'key': config.captcha,
                                                     'action': 'get',
                                                     'id': ids,
                                                     'json': 1}, data=data)
                    res = json.loads(res)
                    if res.get('status', -1) == 1:
                        captcha_key = res['request']
                        break

                if captcha_key:
                    add = {'captcha_sid': captcha_sid,
                           'captcha_key': captcha_key}

                    logs('Capcha ok')
                    Global.start_task(self.execute_task(code, add))
                    break
            return True

    def start_loop(self):
        '''Метод инициализации очереди задач'''
        if not self.loop_is_start:
            self.loop_is_start = True
            Global.start_task(self.task_loop())

    def add_task(self, method: str, params: dict, name: int):
        self.start_loop()
        new_task = f'[API.{method}({params}),{name}],'
        self.tasks.append(new_task)

    async def get_responses(self, method: str, params: dict, timers: float = 0.1) -> dict:
        """
        Ожидание ответа в self.response
        """

        self.start_loop()

        self.name_id += 1
        name = self.name_id
        self.add_task(method, params, name)

        for _ in range(600):
            await asyncio.sleep(timers)
            res = self.response.get(name)
            if not res is None:
                del self.response[name]
                return res

        logs(f'get response error:\n{method} {name} {timers}\n{params}')
        return {}


class VkClass:
    __slots__ = ('token', 'group', 'index', 'edit_message_id_dict',
                 'event_processing', 'loop', 'admin_loop')

    def __init__(self, group, token, event_processing, loop: VkLoop = None, admin_loop: VkLoop = None):
        self.group: int = group
        self.token: str = token
        self.event_processing = event_processing
        self.edit_message_id_dict: Dict[int, Tuple[int, bool]] = {}

        if loop is None:
            self.loop: VkLoop = VkLoop(self.group, self.token)
        else:
            self.loop: VkLoop = loop

        self.admin_loop: VkLoop = admin_loop

        Global.social_tmp[group] = self
        Global.start_task(self.get_event_from_group())

    def add_task(self, method: str, params: Dict[str, UNI], is_user: bool = False):
        if is_user:
            if self.admin_loop is None:
                raise Exception('Need init admin loop')
            self.admin_loop.add_task(method, params, 0)
        else:
            self.loop.add_task(method, params, 0)

    def set_typing(self, event: Event, user_id):
        params = {'user_id': event.user_id if not user_id else user_id, 'type': 'typing'}
        self.add_task('messages.setActivity', params)

    def set_group_online(self):
        self.add_task('groups.enableOnline', {'group_id': self.group})

    async def is_member(self, event: Event, ids='') -> int:
        # return 0 or 1
        out = await self.get_response('groups.isMember',
                                      {'group_id': self.group,
                                       'user_id': ids if ids else event.user_id})
        return out if out else 0

    async def is_members(self, group, ids: list) -> Dict[int, int]:
        # return {user_id: 0 or 1, ...}
        task = []
        for i in range(0, len(ids), 500):
            _id = ids[i:i + 500]
            task.append(asyncio.create_task(self.get_response('groups.isMember',
                                                              {'group_id': abs(int(group)),
                                                               'user_ids': ','.join(_id)})))
        res = await asyncio.gather(*task)

        out = []
        [out.extend(x) for x in res]

        return {str(i['user_id']): i["member"] for i in out}

    async def create_post(self, owner_id: int, msg: str,  atta: str) -> bool:
        params = {'owner_id': owner_id,
                  'message': msg,
                  'attachments': atta}

        v = await self.get_response('wall.post', params, True)
        print(v)

        #self.add_task('wall.post', params, True)
        return True

    def init_long_poll(self) -> Coroutine:
        """Получение инфо LongPoll сервера"""
        return self.get_response('groups.getLongPollServer', {'group_id': self.group})

    def init_user_long_poll(self) -> Coroutine:
        return self.get_response('messages.getLongPollServer', {'lp_version': 3, 'need_pts': 0}, True)

    async def get_event_from_group(self):
        while True:
            data = await self.init_long_poll()
            while True:
                try:
                    params = {'act': 'a_check', 'key': data["key"], 'ts': data["ts"], 'wait': 25}
                    res = await req.get(data["server"], params, timeout=60)  # <-- запрос
                    resp = json.loads(res)

                    if resp.get('failed'):
                        logs.long_pull(str(resp))
                        break

                    data['ts'] = resp['ts']
                    updates = resp['updates']

                    for update in updates:
                        #print(update)
                        event = self.update_pars(update)
                        if not event.empty:
                            Global.start_task(self.event_processing(event))

                except KeyError:
                    break

                except client_exceptions.ClientOSError:
                    logs('client_exceptions.ClientOSError')
                    break

                except client_exceptions.ServerDisconnectedError:
                    logs('ServerDisconnectedError')
                    break

                except CancelledError:
                    logs('CancelledError')
                    break

                except TimeoutError:
                    logs('TimeoutError')
                    break

                except:
                    logs.long_pull()
                    break

            Global.clear_task_list()

    async def get_event_from_user(self):
        # not use
        while True:
            data = await self.init_user_long_poll()

            while True:
                try:
                    params = {
                        'act': 'a_check',
                        'key': data["key"],
                        'ts': data['ts'],
                        'wait': 25,
                        'mode': 8,
                        'version': 3}

                    response = await req.get('https://' + data["server"], params=params, timeout=120)
                    response = json.loads(response)
                    updates = response['updates']

                    if updates:
                        for update in updates:
                            if len(update) >= 5 and update[2] == 33:
                                print(update)
                                event = Event(update[3], update[5])
                                event.social = self
                                event.from_user = True

                                Global.start_task(self.event_processing(event))

                    data['ts'] = response['ts']

                except KeyError:
                    break

                except:
                    logs()
                    break

    def _save_msg_id(self, message_id: int, event: Event):
        if message_id:
            self.edit_message_id_dict[event.peer_id] = (message_id, len(event.attachments_out) > 0)

    def event_action(self, event: Event, event_data: Optional[dict] = None):
        if event.event_id:
            params = {
                'event_id': event.event_id,
                'user_id': event.user_id,
                'peer_id': event.peer_id,
                'event_data': event_data if event_data else {}
            }
            self.add_task('messages.sendMessageEventAnswer', params)

    async def send(self, event: Event) -> bool:
        """Метод добавления в очередь сообщений и комментариев"""
        message = event.text_out
        keyboard = event.keyboards
        attachment = event.attachments_out
        owner_id = event.owner_id
        post_id = event.post_id
        comment_id = event.message_id
        group_id = event.group_id
        peer_id = event.peer_id
        len_message = len(message)

        if not isinstance(attachment, list):
            attachment = [attachment]

        attachment = ','.join(attachment)
        max_len_message = 550

        if not message and not attachment:
            raise ValueError("Empty event message and attachment")

        if not event.from_comment:
            if (event.support_callback
                and event.from_callback_button
                and event.is_can_edit_prev_msg
                and len_message < max_len_message
            ):
                return await self.messages_edit(event)

            for i in range(1 + len_message // max_len_message):  # если сообщение больше 550 символов
                i *= max_len_message  # разбиваем сообщение по 550
                msg = message[i:i + max_len_message]

                keyb = '' if len(msg) == max_len_message else keyboard

                method = 'messages.send'
                params = {'random_id': rnd.randint(0, 100000000),
                          'peer_id': peer_id,
                          'keyboard': keyb,
                          'template': event.template,
                          'message': msg,
                          'attachment': attachment if len(msg) < max_len_message else ''}

                if event.from_user or event.template:
                    del params['keyboard']
                else:
                    del params['template']

                if len(msg) == max_len_message:
                    self.add_task(method, params)

                else:
                    message_id = await self.get_response(method, params)
                    self._save_msg_id(message_id, event)

            self.event_action(event)

            return True

        else:
            for i in range(1 + len_message // max_len_message):
                i *= max_len_message
                msg = message[i:i + max_len_message]
                params = {'owner_id': owner_id,
                          'post_id': post_id,
                          'from_group': group_id,
                          'reply_to_comment': comment_id,
                          'guid': rnd.randint(0, 100000000),
                          'message': msg,
                          'attachment': attachment}
                self.add_task('wall.createComment', params, True)
            return True

    async def messages_edit(self, event: Event) -> bool:
        prev_message = self.edit_message_id_dict.get(event.peer_id)
        if prev_message is None or prev_message[1]:
            event.from_callback_button = False
            await self.send(event)
            return False

        params = {'peer_id': event.peer_id,
                  'keyboard': event.keyboards,
                  'message': event.text_out,
                  'attachment': event.attachments_out,
                  'message_id': prev_message[0]}

        if not await self.get_response('messages.edit', params):
            event.from_callback_button = False
            await self.send(event)

        self._save_msg_id(prev_message[0], event)

        return True

    def only_send(self, id_user: int, msg: str, atta='', keyboard=''):
        params = {'random_id': rnd.randint(0, 1000000000),
                  'peer_id': id_user,
                  'keyboard': keyboard,
                  'message': msg,
                  'attachment': atta}
        self.add_task('messages.send', params)

    async def get_user_info(self, user_id: int) -> UserDataBD:
        params = {'user_ids': user_id,
                  'fields': 'sex,bdate,city,country,home_town,last_seen,online,timezone'}
        r = await self.get_response('users.get', params)
        res = r[0]

        try:
            bday = ' '.join(res['bdate'].split('.')[::-1])
        except:
            bday = 0

        return UserDataBD(user_id,
                          res['first_name'],
                          res['last_name'],
                          res['sex'],
                          int(time.time() + TIME_OFFSET),
                          bday,
                          self.group)

    def get_user_all_info(self, user_id: int, add_fields=True) -> Coroutine:
        params = {'user_ids': user_id}
        if add_fields:
            params.update({'fields': ('sex,photo_200_orig,bdate,city,country,home_town,'
                                      'last_seen,online,photo_max_orig,screen_name')})
        return self.get_response('users.get', params, timers=0.1)

    async def async_get_photo(self, event: Event) -> list:
        if not event.from_comment:
            message_id = event.message_id

            try:
                res = await self.get_response('messages.getById', {'message_ids': message_id})
                res = res['items'][0]['attachments']

            except (KeyError, IndexError):
                logs()
                return []

            p = res if res else event.attachments

        else:
            p = event.attachments

        all_photo = []
        for j in p:
            try:
                w, h, ind, r = 0, 0, 0, 0
                for i in j['photo']['sizes']:
                    if i['width'] > w or i['height'] > h:
                        w, h, r = i['width'], i['height'], ind
                    ind += 1

                j = j['photo']['sizes'][r]['url']
            except (KeyError, IndexError):
                continue

            all_photo.append(j)

        return all_photo

    async def messages_allowed(self, event: Event, user_id='', group_id=''):
        out = await self.get_response('messages.isMessagesFromGroupAllowed',
                                      {'group_id': event.group_id if not group_id else group_id,
                                       'user_id': event.user_id if not user_id else user_id})
        return out.get('is_allowed', 0) if out else 0

    async def __up(self, path, event: Event, a_type: str = 'photo', caption: str = ''
                   ) -> Union[str, tuple]:
        """Метод для авто загрузки медиа на сервер ВК"""
        peer_id = event.user_id
        attach = ''
        method = ''
        type_doc = ''
        params = {}

        i = path

        file = None
        data = FormData()
        try:
            if not isinstance(i, bytes) and isinstance(i, str):
                if i.split(':')[0].lower() in ['http', 'https']:
                    re_re = re.s_format.findall(i.lower())[0]
                    ln = f'temp{re_re}'
                    res = await req.get(i, timeout=60)
                    i = ln

                    file = io.BytesIO(res)
                    if i.split('.')[-1].lower() in ['jpg', 'png', 'bmp']:
                        a_type = 'photo'
                        data.add_field('file',
                                       file,
                                       filename='file.png',
                                       content_type='image/png')

                    elif i.split('.')[-1].lower() in ['mp3', 'gif', 'ogg', 'wav']:
                        a_type = 'doc'
                        data.add_field('file',
                                       file,
                                       filename='file.mp3',
                                       content_type='audio/ogg')

                    elif i.split('.')[-1].lower() in ['mp4']:
                        a_type = 'doc'
                        data.add_field('file',
                                       file,
                                       filename='file.mp4',
                                       content_type='video/mp4')

            else:
                file = io.BytesIO(i)
                if a_type == 'photo':
                    data.add_field('file',
                                   file,
                                   filename='file.png',
                                   content_type='image/png')
                    i = '1.jpg'
                else:
                    data.add_field('file',
                                   file,
                                   filename='file.mp3',
                                   content_type='audio/ogg')
                    i = '1.mp3'

                    # ---

            if a_type == 'photo' and not event.from_comment:
                method = 'photos.getMessagesUploadServer'
                params = {}

            if a_type == 'doc':
                method = 'docs.getMessagesUploadServer'
                if i.split('.')[-1].lower() in ['mp3']:
                    type_doc = 'audio_message'
                else:
                    type_doc = 'doc'

                params = {'type': type_doc,
                          'peer_id': peer_id}

            if event.from_commentand and a_type == 'doc' and type_doc == 'doc':
                method = 'docs.getUploadServer'
                type_doc = 'doc'
                params = {'group_id': config.user_group_id}

            if event.from_comment and a_type == 'photo':
                method = 'photos.getUploadServer'
                params = {'group_id': config.user_group_id,
                          'album_id': config.user_album_id}

                # ----
            upload_url = (await self.get_response(method, params, event.from_comment))['upload_url']

            # ----
            res = await req.post(upload_url, data=data, timeout=60)
            if file:
                file.close()

            response_up = json.loads(res)

            # ----
            if a_type == 'photo' and not event.from_comment:
                method = 'photos.saveMessagesPhoto'
                params = {
                    'photo': response_up['photo'],
                    'server': response_up['server'],
                    'hash': response_up['hash']
                }

            if a_type == 'doc':
                method = 'docs.save'
                params = {
                    'file': response_up['file'],
                    'tags': '#vkreative',
                    'title': event.text,
                    'return_tags': 1
                }

            if event.from_comment and a_type == 'photo':
                method = 'photos.save'
                params = {
                    'album_id': config.user_album_id,
                    'group_id': config.user_group_id,
                    'caption': caption,
                    'photos_list': response_up['photos_list'],
                    'server': response_up['server'],
                    'hash': response_up['hash']
                }

                # ----
            attach_list = await self.get_response(method, params, event.from_comment)
            # ----
            if a_type == 'photo':
                a = attach_list[0]
                attach = f"{a_type}{a['owner_id']}_{a['id']}"

            elif a_type == 'doc' and type_doc == 'doc':
                a = attach_list['doc']
                attach = f"{a_type}{a['owner_id']}_{a['id']}"

            elif a_type == 'doc':
                a = attach_list['audio_message']
                attach = f"{a_type}{a['owner_id']}_{a['id']}", a['link_mp3']

            return attach

        except:
            if file:
                file.close()

            logs()
            return ''

    async def uploads(self, paths, event: Event, type: str = 'photo',
                      caption: str = '', telegram: str = ''):
        up_task = []
        if not isinstance(paths, list):
            paths = [paths]

        for path in paths:
            up_task.append(asyncio.create_task(self.__up(path, event, type, caption)))

        return await asyncio.gather(*up_task)

    async def search_doc(self, q, t='gif'):
        resp = await self.get_response('docs.search', {'q': q, 'count': 500})
        return [f'doc{i["owner_id"]}_{i["id"]}'
                for i in resp.get('items')
                if i['ext'] == t
                ] if resp else []

    async def search_img(self, q):
        resp = await self.get_response('photos.search', {'q': q, 'count': 500}, True)
        return [f'photo{i["owner_id"]}_{i["id"]}'
                for i in resp.get('items')
                if not re.photo_search.findall(i.get('text', '').lower())
                ] if resp else []

    # @async_timer
    async def upload_cover(self, group_id: int, cover_img: bytes, width=1590, height=530):
        try:
            params = {"group_id": group_id,
                      "crop_x": 0,
                      "crop_y": 0,
                      "crop_x2": width,
                      "crop_y2": height
                      }
            method = 'photos.getOwnerCoverPhotoUploadServer'
            upload_url = await self.get_response(method, params, True)

            assert upload_url.get('upload_url'), f'error -> group = {group_id} url_data = {upload_url}'

            file = io.BytesIO(cover_img)
            data = FormData()
            data.add_field('photo', file, filename='photo.jpg', content_type='image/png')

            uploaded_data = await req.post(upload_url["upload_url"], data=data, timeout=60)
            file.close()
            uploaded_data = json.loads(uploaded_data)

            params = {"hash": uploaded_data["hash"],
                      "photo": uploaded_data["photo"],
                      'v': self.loop.v_api, 'access_token': self.admin_loop.token}
            upload_result = await req.get(self.loop.url + 'photos.saveOwnerCoverPhoto', params=params)
            return upload_result.decode('utf-8')

        except:
            logs()
            return False

    async def get_short_link(self, link: str) -> str:
        response = await self.get_response('utils.getShortLink', {'url': link, 'private': 0})
        return response.get('short_url', link)

    def get_wall_user(self, user_id: int, count=100, offset=0, extended=0) -> Coroutine:
        params = {'owner_id': user_id, 'count': count, 'offset': offset, 'extended': extended}
        return self.get_response('wall.get', params, True, 1)

    def get_user_from_like_post(self, owner_id: int, item_id: int,
                                count=1000, type_post='post',
                                extended=0, offset=0) -> Coroutine:
        params = {'owner_id': owner_id, 'item_id': item_id, 'count': count,
                  'type': type_post, 'extended': extended, 'offset': offset}
        return self.get_response('likes.getList', params, True, 0.6)

    def get_user_from_repost_post(self, owner_id: int, item_id: int, count=1000, offset=0) -> Coroutine:
        params = {'owner_id': owner_id, 'item_id': item_id, 'count': count, 'offset': offset}
        return self.get_response('wall.getReposts', params, True, 0.6)

    def get_user_from_comment_post(self, owner_id: int, post_id: int, count=100, offset=0) -> Coroutine:
        params = {'owner_id': owner_id, 'post_id': post_id, 'need_likes': 1, 'extended': 1,
                  'count': count, 'offset': offset, 'thread_items_count': 10}
        return self.get_response('wall.getComments', params, True, 0.6)

    def get_group_user(self, user_id: int) -> Coroutine:
        return self.get_response('groups.get', {'user_id': user_id}, True, 1)

    def get_friend_user(self, user_id: int) -> Coroutine:
        return self.get_response('friends.get', {'user_id': user_id}, True, 1)

    def get_photo_user(self, user_id: int, count=100) -> Coroutine:
        return self.get_response('photos.getAll',
                                 {'owner_id': user_id, 'count': count},
                                 True, 1)

    # ----

    def get_response(self, method: str, params: dict,
                     is_user: bool = False, timers: float = 0.08) -> Coroutine:
        loop = self.admin_loop if is_user else self.loop
        if loop is None:
            raise Exception('Need init loop')
        return loop.get_responses(method, params, timers)

    def group_join_leave(self, update: dict):
        s = f'{update["type"]}, {update["group_id"]}, {update["object"]["user_id"]}, {int(time.time())};\n'
        logs.log_group_join_leave(s)

    def update_pars(self, update: dict) -> Event:
        obj = update['object']
        # print(update)
        if update['type'] == 'message_new':
            msg_obj = obj['message']
            user_id = msg_obj['from_id']
            peer_id = msg_obj['peer_id']
            message_text = msg_obj['text']
            message_id = msg_obj['id']
            attachment = msg_obj.get('attachments', [])
            fwd_message = msg_obj.get('fwd_messages', [])

            if not message_text and fwd_message:
                message_text = fwd_message[0]['text']
                attachment = fwd_message[0]['attachments']

            if message_text and fwd_message:
                attachment = fwd_message[0]['attachments']

            if user_id == peer_id:
                message_text = re.space.sub(' ', message_text)
                event = Event(user_id, message_text, attachment, message_id)

            else:
                # сообщение из чата
                if re.update_re1.search(message_text.lower()):
                    message_text = re.space.sub(' ', re.update_re1.sub('', message_text).strip())
                    event = Event(user_id, message_text, attachment, message_id)
                    event.peer_id = peer_id
                    event.from_chat = True
                else:
                    return Event('')

            event.client_info(obj.get('client_info', []))
            event.group_id = self.group
            event.social = self
            event.empty = False
            return event

        if config.cover and Global.cover:
            Global.cover.pars(update)

        if update['type'] == 'wall_reply_new' and config.work_in_comment:
            user_id = obj.get('from_id', 0)
            message_text = obj.get('text', '')
            if str(user_id) != f'-{self.group}':
                if len(message_text) > 2 and re.update_re3.search(message_text.lower()):
                    message_id = obj['id']
                    attachment = obj.get('attachments', [])
                    post_id = obj['post_id']
                    owner_id = obj['owner_id']
                    message_text = re.space.sub(' ', re.update_re1.sub('', message_text).strip())
                    event = Event(user_id, message_text, attachment, message_id, post_id, owner_id)
                    event.from_comment = True
                    event.support_keyb = False
                    event.group_id = self.group
                    event.social = self
                    event.empty = False
                    return event

        if update['type'] == 'group_join':
            self.group_join_leave(update)

        if update['type'] == 'group_leave':
            self.group_join_leave(update)

        if update['type'] == 'message_event':
            event = Event(obj['user_id'], obj['payload'])
            event.peer_id = obj['peer_id']
            event.event_id = obj['event_id']
            event.message_id = obj['conversation_message_id']
            event.group_id = update['group_id']
            event.support_callback = True
            event.support_keyb_inline = True
            event.support_keyb = True
            event.from_callback_button = True
            event.social = self
            event.empty = False
            return event

        return Event('')


class Telegram:
    __slots__ = ('id_token', 'token', 'url', 'file_url', 'offset_updates',
                 'event_temp_dict', 'proxy', 'last_message_id', 'event_processing')

    def __init__(self, id_token, token, event_processing):
        self.id_token: int = id_token
        self.token: str = token
        self.url = f'https://api.telegram.org/bot{self.token}/'
        self.file_url = f'https://api.telegram.org/file/bot{self.token}/'
        self.offset_updates: int = 0
        self.event_temp_dict = {}
        self.proxy = get_proxy()
        self.event_processing = event_processing

        self.last_message_id = {}

        Global.start_task(self.getUpdates())

    async def get(self, method, params):
        return await req.get(self.url + method, params=params, proxy=self.proxy)

    async def post(self, method, params, data=None):
        return await req.post(self.url + method, params=params, data=data, proxy=self.proxy)

    def pars_update(self, update):
        update_id = update['update_id']
        callback_query = update.get('callback_query', '')
        c = False

        if update.get('message', ''):
            message = update['message']
            user_id = f"9999{message['chat']['id']}"
            text = message.get('text', '')
            message_id = message['message_id']
            atta, atta_type = self.media_pars(message)
            media_id = message.get('media_group_id', update_id)
            name = message['chat'].get('first_name', 'user_name')

        elif callback_query:
            text = callback_query['data']
            user_id = f"9999{callback_query['message']['chat']['id']}"
            message_id = callback_query['message']['message_id']
            atta, atta_type = self.media_pars(callback_query['message'])
            media_id = callback_query['message'].get('media_group_id', update_id)
            name = callback_query['message']['chat'].get('first_name', 'user_name')
            c = True

        else:
            logs.telegaram(f"Pars error:\n{update}\n\n")
            return update_id

        if not self.event_temp_dict.get(media_id):
            event = Event(int(user_id), text)
            event.attachments_type = atta_type
            event.from_telegram = True
            event.attachments = atta
            event.support_callback = True
            event.from_callback_button = c
            event.message_id = message_id
            event.name = name
            event.group_id = self.id_token
            event.social = self
            self.event_temp_dict[media_id] = event

        else:
            self.event_temp_dict[media_id].attachments.append(atta[0])

        return update_id

    def media_pars(self, message: dict):
        if message.get('photo', 0):
            return [message['photo'][-1]['file_id']], 'photo'
        else:
            return [], ''

    async def getUpdates(self):
        _iter = 0.5
        time_sleep = _iter
        while True:
            try:
                r = await self.get('getUpdates', {'offset': self.offset_updates + 1})
                res = json.loads(r)

            except:
                logs()
                await asyncio.sleep(rnd.random())
                self.proxy = get_proxy()
                continue

            updates = res.get('result')
            if updates:
                time_sleep = _iter
                for update in updates:
                    try:
                        self.offset_updates = self.pars_update(update)

                    except:
                        logs()

            for event in self.event_temp_dict.values():
                Global.start_task(self.event_processing(event))

            self.event_temp_dict = {}

            t = round(time_sleep, 1) if time_sleep < 3 else 3
            await asyncio.sleep(t)
            time_sleep += 0.003

    async def init_webhook(self):
        params = {'url': f'https://{config.ip}:{config.port}/{self.token}/'}

        url = f'https://api.telegram.org/bot{self.token}/setWebhook'

        res = await req.post(url, proxy=config.proxy[0], timeout=30)
        res = json.loads(res)
        # print(res)

        res = await req.post(url, params=params, proxy=self.proxy, timeout=30)
        res = json.loads(res)
        # print(res)

    async def get_user_info(self, event: Event) -> UserDataBD:
        return UserDataBD(event.user_id,
                          event.name,
                          event.last_name,
                          0,
                          int(time.time()),
                          0,
                          self.id_token)

    async def create_post(self, owner_id: int, msg: str, atta: str) -> bool:
        return True

    async def editMessageText(self, event: Event):
        params = {
            'chat_id': str(event.peer_id)[4:],
            'message_id': event.message_id,
            'text': event.text_out,
            'reply_markup': event.keyboards}
        res = await self.get('editMessageText', params)

    async def send(self, event: Event):
        method = 'sendMessage'
        x = str(event.peer_id)[4:]

        if self.last_message_id.get(x, '') and event.text_out and event.from_callback_button:
            await self.editMessageText(event)
            return False

        params = {
            'chat_id': str(event.peer_id)[4:],
            'text': event.text_out,
            'reply_markup': event.keyboards}
        res = await self.get(method, params)
        res = json.loads(res)

        if res.get('ok', False) and res.get('result', ''):
            self.last_message_id[x] = res['result']['message_id']
            if not event.text_out:
                del self.last_message_id[x]

    async def async_get_photo(self, event):
        path_file = []
        for file in event.attachments:
            res = await self.get('getFile', params={'file_id': file})
            res = json.loads(res)["result"].get("file_path", "")
            path_file.append(self.file_url + res)

        return path_file

    async def messages_allowed(self, *args):
        return True

    async def uploads(self, paths, event, type='photo', caption='', telegram=''):
        up_task = []
        if not isinstance(paths, list):
            paths = [paths]

        for path in paths:
            up_task.append(asyncio.create_task(self.up(path, event, type, caption, telegram)))

        out = await asyncio.gather(*up_task)

        return out

    async def up(self, paths, event, type='photo', caption='', telegram=''):
        self.last_message_id = {}

        if type == 'file':
            params = {'chat_id': str(event.user_id)[4:], 'caption': caption}
            file = open(paths, 'rb')
            res = await self.post('sendDocument', data={'document': file}, params=params)
            file.close()
            return []

        if not isinstance(paths, bytes) and isinstance(paths, str):
            if paths.split(':')[0].lower() in ['http', 'https']:
                re_re = re.s_format.findall(paths.lower())[0]
                ln = f'temp{re_re}'

                res = await req.get(paths, timeout=60, proxy=self.proxy)

                if ln.split('.')[-1].lower() in ['jpg', 'png', 'bmp']:
                    type = 'photo'
                    paths = res

                elif ln.split('.')[-1].lower() in ['mp3', 'ogg', 'wav']:
                    type = 'audio'
                    paths = res

                elif ln.split('.')[-1].lower() == 'gif':
                    type = 'doc'
                    paths = res

        if telegram:
            type = telegram

        if type == 'photo':
            params = {'chat_id': str(event.user_id)[4:],
                      # 'reply_markup': event.keyboards
                      }
            file = io.BytesIO(paths)
            res = await self.post('sendPhoto', data={'photo': file}, params=params)
            file.close()

        if type == 'audio':
            params = {'chat_id': str(event.user_id)[4:],
                      # 'reply_markup': event.keyboards
                      }
            file = io.BytesIO(paths)
            res = await self.post('sendAudio', data={'audio': file}, params=params)
            file.close()
            return [0, 0]

        if type == 'doc':
            params = {'chat_id': str(event.user_id)[4:],
                      # 'reply_markup': event.keyboards,
                      'width': 400,
                      'height': 400}
            file = io.BytesIO(paths)
            res = await self.post('sendAnimation', data={'animation': file}, params=params)
            file.close()

        return []

    async def get_short_link(self, link):
        return link

    async def search_doc(self, q, t):
        return []

    async def search_img(self, q):
        return []


class Server:
    __slots__ = 'key_api', 'app', 'event_processing', 'temp'

    def __init__(self, event_processing):
        self.key_api = config.key_api
        self.app = self.app_create()
        self.event_processing = event_processing

        self.temp = []

    def app_create(self):
        app = web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

        app['static_root_url'] = '/templates'
        app.router.add_static('/templates', 'templates', name='templates')

        app.add_routes(self.routes())
        return app

    def routes(self):
        return [
            web.post('/event', self.create_event),
            web.get('/hello', self.hello),
            web.get('/bd', self.get_bd),
            web.get('/', self.html),
            web.post('/check', self.check)
        ]

    def start(self):
        web.run_app(self.app,
                    port=config.port,
                    ssl_context=config.ssl_context)

    def add(self, *args):
        for startup in args:
            self.app.on_startup.append(startup)
        return self

    @aiohttp_jinja2.template('hello.html')
    async def hello(self, _):
        pass

    async def create_event(self, request: web.Request):
        try:
            data = await request.content.read()
            data_json = json.loads(data)
        except:
            logs()
            return web.json_response({'error': 'error pars json data'})

        if self.key_api == request.rel_url.query.get('key'):
            try:
                type_event = data_json.get('type_event', '')
                text = data_json.get('text', '')
                user_id = data_json.get('user_id', '')
                group_id = data_json.get('group_id', '')
                send_in_api = data_json.get('send_in_api', 1)
                keyboard = data_json.get('keyboard', False)
                keyboard_inline = data_json.get('keyboard_inline', False)
                atta = data_json.get('attachment', '')

                if type_event == 'check_content':
                    name = data_json.get('name_event', '')
                    Global.check_content[name] = -1

                event = Event(int(user_id), text)
                event.attachments_out = atta
                event.social = Global.social_tmp[int(group_id)]
                event.from_api = int(send_in_api)
                event.group_id = group_id
                event.support_keyb = keyboard
                event.support_keyb_inline = True if keyboard_inline else False

                x = await self.event_processing(event)

                response = "ok"

            except Exception as ex:
                response = {'error': str(ex)}
        else:
            response = {'error': 'error api key'}

        response = {'response': response}
        return web.json_response(response)

    async def check(self, request: web.Request):
        query = request.rel_url.query
        if self.key_api == query.get('key', ''):
            name = query.get('name_event', '')
            if not name:
                response = {'error': 'not name event'}
            else:
                response = {'check': Global.check_content.get(name, -1)}

        else:
            response = {'error': 'error api key'}

        response = {'response': response}
        return web.json_response(response)

    async def get_bd(self, request: web.Request):
        query = request.rel_url.query
        if self.key_api == query.get('key', 0):
            try:
                bd_name = query.get('bd_name', '')
                vals = query.get('vals', '')
                method = query.get('method', '')
                BD = Sqlbd(bd_name)
                logs(f'api BD --> {vals}')
                y = await getattr(BD, method)(*json.loads(vals))

            except Exception as ex:
                y = {'error': str(ex)}

        else:
            y = {'error': 'error api key'}

        return web.json_response({'response': y})

    @aiohttp_jinja2.template('index.html')
    async def html(self, request: web.Request):
        query = request.rel_url.query
        try:
            text = query.get('text', -1)
            if text != -1 and text:
                event = Event(38487286, text)
                event.social = list(Global.social_tmp.values())[0]
                event.from_api = 1
                event.group_id = list(Global.social_tmp.keys())[0]
                event.support_keyb = False

                x = await self.event_processing(event)

                self.temp.append([text, x.text_out])

            return {'messages': self.temp}


        except:
            return web.Response(text='Error')


class Button:
    __slots__ = 'label', 'color', 'type_button', 'payload'

    TEXT = "text"
    CALLBACK = "callback"

    #: Синяя
    PRIMARY = 'primary'

    #: Белая
    DEFAULT = 'default'

    #: Красная
    NEGATIVE = 'negative'

    #: Зелёная
    POSITIVE = 'positive'

    def __init__(self, label, color="default", type_button="text", payload=None):
        self.label = label
        self.color = color
        self.type_button = type_button
        self.payload = payload if payload else label


class VkKeyboards:
    __slots__ = 'one_time', 'inline', 'lines', 'keyboard'

    def __init__(self, one_time=False, inline=False):
        self.one_time = one_time
        self.inline = inline
        self.lines = [[]]

        self.keyboard = {
            'one_time': self.one_time,
            'inline': self.inline,
            'buttons': self.lines
        }

    def get_keyboard(self):
        return json.dumps(self.keyboard)

    def add_button(self, label, color="default", button_type="text", payload=None):
        current_line = self.lines[-1]

        if len(current_line) >= 4:
            raise ValueError('Max 4 buttons on a line')

        color_value = color

        if payload:
            payload = json.dumps(payload)

        current_line.append({
            'color': color_value,
            'action': {
                'type': button_type,
                'payload': payload,
                'label': label,
            }
        })

    def add_button_from_button(self, button: Button):
        self.add_button(
            button.label,
            button.color,
            button.type_button,
            button.payload
        )

    def add_button_from_string(self, s: str, button_type="text", payload=None):
        color = "default"
        label = s
        b = s.split('%')

        if len(b) == 2:
            label = b[0]
            c = b[-1].lower()
            if c == 'g':
                color = "positive"  # зелёная
            elif c == 'r':
                color = "negative"  # красная
            elif c == 'w':
                color = "default"  # белая
            elif c == 'b':
                color = "primary"  # синяя
            else:
                color = "default"

        if payload == s:
            payload = label

        self.add_button(label, color, button_type, payload)

    def add_line(self):
        if len(self.lines) >= 10:
            raise ValueError('Max 10 lines')
        self.lines.append([])

    def as_telegram(self):
        arr = []
        for j in self.lines:
            temp = []
            for j2 in j:
                temp.append({
                    'text': j2["action"]["label"],
                    'callback_data': j2["action"]["label"]
                })
            arr.append(temp)

        self.keyboard = {
            'inline_keyboard': arr,
            'one_time_keyboard': False,
            'resize_keyboard': True
        }


class ImgCreator:
    __slots__ = 'img', 'draw', 'fnt', 'size_x', 'size_y', 'elements'

    def __init__(self, path):
        self.img: Image = Image.open(path)
        self.draw = ImageDraw.Draw(self.img)
        self.fnt = ImageFont.truetype('cover/GothaProBol.otf', 30)
        self.size_x = self.img.size[0]
        self.size_y = self.img.size[1]
        self.elements = {}

    def add(self, key, path: str):
        self.elements[key] = Image.open(path)

    def write(self, key: int, xy: tuple):
        el = self.elements[key]
        self.img.paste(el, xy)

    def write_d(self, d, xy: tuple, c=''):
        self.draw.text(xy, str(d), fill=c, font=self.fnt,
                       align="center", spacing=int(65 / 4))

    def get_img_byte(self):
        buffer = io.BytesIO()
        self.img.save(buffer, 'JPEG')
        buffer.seek(0)
        return buffer.read()
