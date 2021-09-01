from untils import Event, until, logs
from Sqlbd import Sqlbd
from typing import List, Dict, Optional
from Template import str_menu_out
import ujson as json
import os
import re
import importlib.util


def middelware(func):
    async def wrapper(self, event: Event) -> Event:
        if event.stoper():
            self.end(event)
            return event.answer(str_menu_out).keyboard()
        return await func(self, event)

    return wrapper


addon_dict: Dict[str, tuple] = {}


def addon_init(commands: List[str], icon: str, in_comment: bool, menu_type: int):
    def wrapper(cls):
        name = str(cls).split('.')[-1][:-2].upper()
        addon_dict[name] = (tuple([x.lower() for x in commands]), name, cls,
                            icon, in_comment, menu_type)
        return cls
    return wrapper


def addon_load():
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            path = os.path.join(root, file)
            if not '.py' in path or '.pyc' in path or '__' in path or '.pyd' in path:
                continue
            with open(path, encoding='utf-8') as f:
                file = f.read()

            if re.findall(r'@addon_init\(', file):
                name = path.split('\\')[-1].split('.')[0].capitalize()

                spec = importlib.util.spec_from_file_location(name, path)
                foo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(foo)


_bd_condition = Sqlbd('condition')


class Condition:
    __slots__ = ()

    def get_condition(self, ids) -> dict:
        ans = _bd_condition.get(ids, sync=True)
        if ans:
            try:
                print(ans[0][1])
                v = ans[0][1]
                s = json.loads(v.replace("'", '"'))
                return s
            except:
                logs()
                return {}
        else:
            _bd_condition.put(ids, "{}", sync=True)
            return {}

    def set_condition(self, ids,
                      condition_params,
                      value,
                      update=True,
                      return_value=None):
        condition_dict = self.get_condition(ids)
        x = condition_dict.get(condition_params)
        if update or x is None:
            condition_dict[condition_params] = value
            self.save_condition(ids, condition_dict)
            return return_value if not return_value is None else value
        else:
            return x

    def save_condition(self, ids, dict_state):
        _bd_condition.up(ids, json=json.dumps(dict_state), sync=True)


class Addon(Condition, until):
    """
    Общий класс
    """
    __slots__ = "step", "user_id", "username", 'lock'

    def __init__(self, username: str = '', user_id: int = 0):
        self.username = username
        self.user_id = user_id
        self.step = 0
        self.lock = 0

    def isstep(self, val: int, new_step_if_true: int = -1) -> bool:
        step_bool = val == self.step
        if step_bool and new_step_if_true != -1:
            self.step = new_step_if_true

        return step_bool

    def end(self, event: Optional[Event] = None):
        self.step = 0

    def setstep(self, val: int):
        self.step = val

    async def mainapp(self, event: Event) -> Event:
        return event.answer(event.text)  # простой эхо бот
