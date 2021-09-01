import addons.info_text as IT
from untils import Event
from Addon import addon_dict


_add_comment = ''
_GAME = ['', []]
_USEFUL = ['', []]
_UNTILS = ['', []]
_ALL = ['', []]
a, b, c, d = 0, 0, 0, 0
for i in addon_dict.values():
    if i[4]:
        _add_comment += '\n' + ' | '.join(i[0])
    if i[5] == 1:
        a += 1
        _GAME[0] += f'\n{i[3]} {a}. {i[0][0].capitalize()}'
        _GAME[1].append([a, i[0][0]])
    if i[5] == 2:
        b += 1
        _USEFUL[0] += f'\n{i[3]} {b}. {i[0][0].capitalize()}'
        _USEFUL[1].append([b, i[0][0]])
    if i[5] == 3:
        c += 1
        _UNTILS[0] += f'\n{i[3]} {c}. {i[0][0].capitalize()}'
        _UNTILS[1].append([c, i[0][0]])
    d += 1
    if i[5] != 0:
        _ALL[0] += f'\n{i[3]} {d}. {i[0][0].capitalize()}'
        _ALL[1].append([d, i[0][0]])

keyb_game = [
     '🎮 !Викторина%b',
     '🌪 !Акинатор%b',
     '💣 !Сапер%b',
     '💥 !Морской бой%b',
     '❓ !Чгк%b',
     '❌ !Крестики-нолики%b',
     '🕹 !Миллионер%b',
     '😵 !Виселица%b'
             ]
keyb_useful = [
       '🎨 !Фото Арт%b',
       '📢 !Озвучь текст%b',
       '🌠 !Гороскоп%b',
       '🔍 !Гифка%b',
       '❓ !Факт%b',
       '🗣 !Анонимный чат%b',
       '😂 !Анекдот%b',
       '🙃 !Переверни текст%b']
keyb_untils = ['🇬🇧 !Переводчик%b',
               '💭 !Напомни%b',
               '🔢 !Калькулятор%b',
               '🌦 !Погода%b',
               '💠 !QRcode%b',
               '👥 !Википедия%b',
               '🎮 !Игры', '😂 !Развлечения']
keyb_about = ['⚙ !Отзыв%b',
              '⚙ !Подробнее%b',
              '⚙ !Бот в комментариях%b',
              '⚙ !Статистика%b']
keyb_bot_in_comment_command_about = ['⚙ !Все команды%b', '⚙ !Бот в комментариях%b']

key_back = '⬅ !Назад'


class Menu:
    __slots__ = 'step'

    def __init__(self):
        self.step = '!помощь'

    def menu(self, event: Event, lst: list, keyb: list,
             about_str='Что выберешь? 👇', keyb_tablet=2, add=False) -> Event:

        h = '' if event.support_keyb_inline else '\n\n⬅ 0. Назад'
        x = f'{about_str}\n{lst[0]}'
        if add:
            x = f'{event.text_out}\n\n{x}'
        return event.answer(f'{x}{h}').keyboard(*keyb, key_back, tablet=keyb_tablet)

    def help(self, event: Event, bot, add=False) -> Event:
        bot.reviews = False
        if bot.first_message == -1:
            bot.first_message += 1

        h = "Что выберешь? 👇" if event.support_keyb_inline else IT._HELP

        if event.from_comment:
            h = IT._all_command_in_comment
            bot.reset()

        if add:
            h = f'{event.text_out}\n\n{h}'

        event.keyboard(*IT._helpkeyboard, tablet=1 if event.support_keyb_inline else 2)
        return event.answer(h)

    def int_to_command(self, command_list: list) -> dict:
        command = {0: '!помошь'}
        for i in command_list[1]:
            command[i[0]] = i[1]
        return command

    def mainapp(self, message: str, event: Event, bot, add: bool, now=False) -> Event:
        if bot.ex_match(message, '/start', '/старт', lock=False):
            message = '!помошь'

        if bot.ex_match(message, '!ЧИТАТЬ ЗДЕСЬ', lock=False):
            event.keyboard('🔧 !Добавить%g', key_back, tablet=1)
            return event.answer(IT._bot_in_message_command_about)

        if bot.ex_match(message, '!ПОДРОБНЕЕ', '!КОМАНДЫ', lock=False):
            event.keyboard('⚙ !Читать здесь%g', key_back, tablet=1)
            return event.answer('https://vk.com/@kreo_0-komandy-bota')

        if bot.ex_match(message, '!ДОБАВИТЬ', '!ОТЗЫВ', lock=False):
            bot.reviews = True
            return event.answer(f"Если ты не {event.gender('нашел', 'нашла')} нужной функции в боте,"
                                f" {event.gender('нашел', 'нашла')} ошибку или просто хочешь оставить отзыв, "
                                f"пришли ответным сообщением, что ты {event.gender('искал', 'искала')} "
                                f"или описание ошибки."
                                ).keyboard('🚫 !Не хочу%r', key_back, tablet=1)

        if bot.ex_match(message, '!КОММЕНТАРИИ', '!БОТ В КОММЕНТАРИЯХ', lock=False):
            event.keyboard('⚙ !Все команды%b', key_back, tablet=1)
            event.attachment(['doc-30688695_533019183', 'doc-30688695_533025884'])
            return event.answer(IT._bot_in_comment)

        if bot.ex_match(message, '!ВСЕ КОМАНДЫ', lock=False):
            event.keyboard('⚙ !Описание%b', key_back, tablet=1)
            return event.answer(IT._all_command_in_comment)

        if bot.ex_match(message, '!ОПИСАНИЕ', lock=False):
            event.keyboard('⚙ !Все команды%b', '⚙ !Бот в комментариях%b', key_back, tablet=1)
            return event.answer(IT._bot_in_comment_command_about)

        if bot.ex_match(message, '!ПОМОЩЬ', lock=False) or now:
            bot.int_to_command = {0: '!ПОМОЩЬ', 1: '!ИГРЫ', 2: '!РАЗВЛЕЧЕНИЯ',
                                  3: '!ПОЛЕЗНОЕ', 4: '!ВСЁ МЕНЮ', 5: '!О БОТЕ'}
            return self.help(event, bot, add)

        if bot.ex_match(message, '!МЕНЮ', '!ВСЁ МЕНЮ', '!ВСЕ МЕНЮ', lock=False) or now:
            self.step = '!ПОМОЩЬ'
            bot.int_to_command = self.int_to_command(_ALL)
            return self.menu(event, _ALL, ['⚙ !ПОДРОБНЕЕ'], about_str='Напиши цифру 👇', add=add)

        if bot.ex_match(message, '!ИГРЫ', lock=False):
            self.step = '!ИГРЫ'
            bot.int_to_command = self.int_to_command(_GAME)
            return self.menu(event, _GAME, keyb_game, add=add)

        if bot.ex_match(message, '!РАЗВЛЕЧЕНИЯ', lock=False):
            self.step = '!РАЗВЛЕЧЕНИЯ'
            bot.int_to_command = self.int_to_command(_USEFUL)
            return self.menu(event, _USEFUL, keyb_useful, add=add)

        if bot.ex_match(message, '!ПОЛЕЗНОЕ', '!ПОЛЕЗНО', lock=False):
            self.step = '!ПОЛЕЗНОЕ'
            bot.int_to_command = self.int_to_command(_UNTILS)
            return self.menu(event, _UNTILS, keyb_untils, add=add)

        if bot.ex_match(message, '!О БОТЕ', lock=False):
            self.step = '!О БОТЕ'
            bot.int_to_command = {0: '!ПОМОЩЬ', 1: '!ОТЗЫВ', 2: '!ПОДРОБНЕЕ',
                                  3: '!КОММЕНТАРИИ', 4: '!СТАТИСТИКА'}
            h = (f'⚙ 1. !Отзыв - оставить отзыв\n' 
                 f'⚙ 2. !Подробнее - узнать описание всех команд\n' 
                 f'⚙ 3. !Бот в комментариях\n'
                 f'⚙ 4. !Статистика - твоя статистика активности в группе')
            return self.menu(event, [' '], keyb_about, about_str=h, keyb_tablet=1, add=add)

        return None




