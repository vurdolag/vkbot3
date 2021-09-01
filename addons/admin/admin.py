# -*- coding: utf-8 -*-

from untils import Event, Global
import sys
from memory_profiler import memory_usage
import asyncio
import re
import time
from asyncio import create_task, gather
import random
import config
from Template import str_back
from Sqlbd import Sqlbd

keyb = [str_back]


bd_mail = Sqlbd('mail')
bd_userdata = Sqlbd('userdata')


async def admin(event: Event) -> Event:
    msg = event.re_del(r'!админ', event.text.lower()).text
    if event.check('!лист коро'):
        coro = ''
        for i, t in enumerate(Global.loop_tasks):
            if t.done():
                continue
            try:
                x = str(t).split("g coro=<")[-1].split("running a")[0]
                coro += f'{i}. {x}\n'
            except:
                pass

        return event.answer(coro).keyboard()

    if event.check('!память'):
        mem = 0
        bots = 0
        for i in Global.user.values():
            bots += 1
            mem += sys.getsizeof(i)

        return event.answer(f'Объектов бота в кеше: {bots}\n'
                            f'Занято памяти: {mem} байт\n'
                            f'Общее: {memory_usage()[0]} МБ')

    if event.check('!сброс'):
        Global.user = {}
        return event.answer('dict user clear')

    if event.check('!выход'):
        for task in Global.loop_tasks:
            Global.loop_tasks.remove(task)
        exit()

    if event.check('!стат'):
        stat = Global.cover.groups_wal_stat
        out = ''
        for i in stat.keys():
            a = await Global.cover.get_max_user_stat(stat[i], i, 20)
            out += i + '\n'
            for j in a:
                out += f'{j[0]} : {j[1]}\n'

        return event.answer(out)

    if event.check('!сенд'):
        msg = re.sub(r'!админ !сенд', '', event.text, flags=re.IGNORECASE)
        addkeyb = re.findall(r"(?<=,,).+?(?=;)", msg)
        target_group = re.findall(r"(?<=\*g).+?(?=g\*)", msg)
        if target_group:
            target_group = [int(x) for x in target_group]
        else:
            target_group = [x for x in config.token.keys()]

        msg = re.sub(r'\*g.+?g\*', '', msg, flags=re.IGNORECASE)
        msg = re.sub(r',,.+?;', '', msg, flags=re.IGNORECASE)
        msg = f'Рассылка:\n\n{msg}\n\nЧтобы отказаться от рассылок команда: Стоп рассылка'

        attachment = await event.get_photo()

        users = await bd_userdata.get_all()
        black_list = await bd_mail.get_all()

        t1 = time.time()

        event.support_keyb_inline = False
        event.keyboard(*addkeyb, 'Стоп рассылка%r', tablet=1)
        keyb = event.keyboards

        async def get(user, group_id, social):
            await asyncio.sleep(random.random() + 1)
            try:
                a = await social.messages_allowed('', user[0], group_id)
            except:
                print('er', user[0], group_id)
                return 0

            try:
                if a:
                    if not '*test*' in msg or user[0] in config.admin:
                        m = msg.replace("*name*", user[1])
                        e = Event(user[0])
                        e.social = social
                        e.group_id = group_id
                        e.keyboards = keyb
                        if attachment:
                            await e.uploads(attachment)
                        await e.answer(m).send()
                        del e
                    return 1

                else:
                    await bd_mail.put(user[0], group_id)
                    return 0
            except:
                return 0

        task = []
        ind = 0
        for group_id, social in Global.social_tmp.items():
            if group_id not in target_group:
                continue

            for user in users:
                if (user[0], group_id) in black_list or user[0] > 1000000000:
                    continue

                ind += 1

                task.append(create_task(get(user, group_id, social)))  # <-- get
                if ind % 24 == 0:
                    await asyncio.sleep(0.5)

                if ind % 48 == 0:
                    await event.answer(f'{group_id} / {len(users)} / {ind}').send()

        ind = await gather(*task)

        return event.answer(f'Oтправлено {sum(ind)}, время {round(time.time() - t1, 2)}')

    if event.check('!лод'):
        if event.from_telegram:
            return event.answer('None')
        event.social.loop.low_load = not event.social.loop.low_load
        return event.answer(f'Лод: {event.social.loop.low_load}')

    return event.answer('Неверная команда')
