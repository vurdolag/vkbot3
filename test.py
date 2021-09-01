import tracemalloc
import os
import linecache


def display_top(snapshot, key_type='lineno', limit=10):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB"
              % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))



def view_top():
    snapshot = tracemalloc.take_snapshot()
    display_top(snapshot)


tracemalloc.start()


import asyncio
async def ticer():
    while 1:
        await asyncio.sleep(30)
        view_top()



async def main(_8_):
    #Global.start_task(Global.saver_user_dict())

    social = ''
    admin_loop = VkLoop(config.admin, until.get_user_token())
    VkClass(174587092, '6c30a85b9085b8dcb062fd0077f757ae24374e529ef4ee550dcf7f5b7ca7089038a4b4adaa9d4ae2d70a8',
            Bot.route, admin_loop=admin_loop)

    #for group_id, token in config.token.items():
    #    social = VkClass(group_id, token, Bot.route, admin_loop=admin_loop)

    #Global.start_task(ticer())

    #Global.cover = CoverCreator([
    #    174587092
    #], social)
    #Global.start_task(Global.cover.mainapp())

    #Telegram(99991396624487, '1396624487:AAEpQnk_blZxqjSQBmvWISO8CMcFonzbFN0', Bot.route)

    #for id_token, token in config.token_telegram.values():
    #    Telegram(id_token, token, Bot.route)

    #if config.subscribe:
    #    Global.start_task(Global.time_sender(Bot.route))

    await gather(*Global.loop_tasks)

if __name__ == '__main__':
    from aiohttp import ClientSession
    from untils import VkClass, VkLoop, req, Telegram, Server, Global, until, logs
    from MainBot import Bot
    from Sqlbd import Sqlbd
    from Models import UserDataBD
    from cover.Cover import CoverCreator
    import config

    from asyncio import gather, run


    #Server(Bot.route).add(main).start()

    run(main(0))
