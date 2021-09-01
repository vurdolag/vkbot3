import asyncio
import sqlite3
from dataclasses import dataclass

from recompile import double_comma
from untils import logs
from typing import Union, Any
from dataclasses import dataclass


import config


def async_cover_bd(func):
    def wrapper(self, *args, **kwargs):
        if kwargs.get('sync'):
            del kwargs['sync']
            return func(self, *args, **kwargs)

        event_loop = asyncio.get_event_loop()
        return event_loop.run_in_executor(None, func, self, *args, kwargs)

    return wrapper


def cover_bd(func):
    @async_cover_bd
    def wrapper(self, *args, **kwargs):
        if isinstance(args, dict):
            kwargs = args
            args = ()
        if args and isinstance(args[-1], dict):
            kwargs = args[-1]
            args = args[:-1]

        connection = sqlite3.connect(self.path)
        result = False
        try:
            if len(args) == 1 and not self.return_obj is None and isinstance(args[0], self.return_obj):
                args = list(args[0].__dict__.values())

            result = func(self, connection, *args, **kwargs)

            if isinstance(result, list) and not self.return_obj is None:
                result = [self.return_obj(*i) for i in result]

        except sqlite3.IntegrityError as ex:
            print(ex, func.__name__, *args)
        except:
            logs.bd()
        connection.close()
        return result

    return wrapper


_bd_dict = {}


def init(cls):
    command = []
    for key, val in cls.__dict__.get('__annotations__', {}).items():
        _type = ''

        if val == int:
            _type = 'INTEGER'
        if val == str:
            _type = 'TEXT'

        command.append(f'"{key}" {_type}')

    _bd_dict[cls.__name__] = ','.join(command)

    return dataclass(cls)


class Sqlbd:
    __slots__ = 'tabs', 'path', 'connection', 'return_obj'

    def __init__(self, tabs: Union[str, Any], return_obj=None):
        self.connection = None

        if not isinstance(tabs, str):
            self.tabs = tabs.__name__
            self.return_obj = tabs
        else:
            self.tabs = tabs
            self.return_obj = return_obj

        self.path = config.bd_path

        if not self._check(sync=True):
            self.create_tabs(sync=True)

    def _simple_contains(self, item):
        ans = self.get(item, sync=True)
        if ans:
            a = ans[0].id if self.return_obj else ans[0][0]
            if isinstance(a, str) and not isinstance(item, str):
                item = str(item)
            if not isinstance(a, str) and isinstance(item, str):
                a = str(a)

            return item == a

        else:
            return False

    def __contains__(self, item):
        if self.return_obj and isinstance(item, self.return_obj) and hasattr(item, 'id'):
            return self._simple_contains(item.id)

        else:
            return self._simple_contains(item)

    def _commit(self, conn, q):
        cursor = conn.cursor()
        cursor.execute(q)
        conn.commit()
        return cursor

    def _get(self, conn, q):
        cursor = conn.cursor()
        cursor.execute(q)
        return cursor

    @cover_bd
    def _check(self, conn):
        try:
            self._get(conn, f'SELECT * FROM {self.tabs}')
            return True
        except:
            return False

    @cover_bd
    def create_tabs(self, conn):
        q = config.bd_tabs.get(self.tabs)
        if not q:
            q = _bd_dict.get(self.tabs)

        if q:
            self._commit(conn, f'CREATE TABLE "{self.tabs}" ({q});')
            print('Create tab', self.tabs)

        else:
            raise Exception(f'Create tab ERROR {self.tabs}')

    @cover_bd
    def get(self, conn, _id, item='*', row='id'):
        q = f'SELECT {item} FROM {self.tabs} where {row} = "{_id}";'
        return self._get(conn, q).fetchall()

    @cover_bd
    def get_all(self, conn, key=None, val=None, item='*'):
        v = '' if key is None and val is None else f'where {key} = "{val}"'
        q = f'SELECT {item} FROM {self.tabs} {v};'
        return self._get(conn, q).fetchall()

    @cover_bd
    def get_between(self, conn, key, val1, val2, item='*'):
        q = f'SELECT {item} FROM {self.tabs} WHERE {key} BETWEEN {val1} AND {val2};'
        return self._get(conn, q).fetchall()

    @cover_bd
    def put(self, conn, *args):
        x = '('
        for i in args:
            if isinstance(i, str):
                i = double_comma.sub("'", i)
                x += f'"{i}", '
            else:
                x += f'{i}, '
        x = x[:-2] + ')'

        q = f"INSERT INTO {self.tabs} VALUES {x};"
        self._commit(conn, q)
        return True

    @cover_bd
    def up(self, conn, _id, param='', row='id', **kwargs):
        if param and isinstance(param, dict):
            kwargs = param

        k = []
        for key, val in kwargs.items():
            val = double_comma.sub("'", str(val))
            k.append(f'{key} = "{val}"')

        q = f'UPDATE {self.tabs} SET {",".join(k)} WHERE {row} = "{_id}"'
        self._commit(conn, q)
        return True

    @cover_bd
    def delete(self, conn, command):
        q = f'DELETE FROM {self.tabs} WHERE {command};'
        return self._commit(conn, q).rowcount

    @cover_bd
    def castom(self, conn, code):
        return self._commit(conn, code)
