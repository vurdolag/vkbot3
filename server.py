# -*- coding: utf8 -*-

async def main(_):
    social = None
    admin_loop = VkLoop(config.admin, until.get_user_token(), is_user=True)
    for group_id, token in config.token.items():
        social = VkClass(group_id, token, Bot.route, admin_loop=admin_loop)

    Global.cover = CoverCreator([
        193674464,
        30688695,
        168691465,
    ], social)
    Global.start_task(Global.cover.mainapp())

    for id_token, token in config.token_telegram.items():
        Telegram(id_token, token, Bot.route)

    if config.subscribe:
        Global.start_task(Global.time_sender(Bot.route))

if __name__ == '__main__':
    from untils import VkClass, VkLoop, Telegram, Server, Global, until
    from MainBot import Bot
    from cover.Cover import CoverCreator
    import config

    Server(Bot.route).add(main).start()
