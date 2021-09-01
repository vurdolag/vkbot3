import random as rnd
from addons.info_text import _HELP, _helpkeyboard
from addons.joke.joke import cmd_clear
from untils import subscribe, Event, Global
from Sqlbd import Sqlbd
from Template import str_back
import re
import addons.info_text as IT
from addons.emodji import EMOJI_UNICODE
from asyncio import create_task, gather

EMOJI_UNICODE = tuple(EMOJI_UNICODE.values())

ans = [

    [r'(гол(о|ы)(и|е).{,18}фот|фот(о|ки|ку|чку).{,18}гол(о|ы)(и|е))', 'Этот бот не присылает голые фотки...\n\nПиши '
                                                                      '"ПОМОЩЬ" чтобы узнать команды.'],

    [r'(п(а|о)ка|поки|пр(а|о)щай|д(а|о)свидания)', "Пока! 😉"],

    [r'(ка(к|г|).{,16}д(е|и)л(а|ы)|д(е|и)л(а|ы).{,16}ка(к|г|))', ["Отлично! 😏", 'Хорошо! ☺',
                                                                  'Дела хорошо 😎',
                                                                  'У бота дела хорошо 👍']],

    [r'((что|чё|че|чо|чито|шо).{,12}дел(а|о)еш)', 'Отвечаю на твои сообщения 🙃'],

    [r'(ты.{,8}кто|кто.{,8}ты|что.{,8}ты такое)', 'Я бот 🤖\n\nСоздан помомогать и развлекать тебя, '
                                                  'пиши "ПОМОЩЬ" чтобы узнать мои команды'],

    [r'(з(а|о)чем|п(а|о)ч(е|и)му)', 'Потому что я бот 🤖\n\nСоздан помомогать и развлекать тебя, пиши "ПОМОЩЬ" '
                                    'чтобы узнать мои команды'],

    [r'п(о|а)н(и|е)май', 'Я бы с радостью, но я всего лишь бот...'],

    [r'(эт(о|а)|и).{,8}знач(и|е)т', 'Аааа... теперь понятно.'],

    [r'ты.{,10}бот', 'Хмм... ведь и правда я бот 😆'],

    [r'(эй|ало|алло|^ау$)', 'ШО? 😎', '', 'photo-168691465_457244642'],

    [r'трахат', 'В этом боте нету такой функции "Трахать"'],

    [r'секс', ['Cекс закончился LOL 😂', 'Секс только по подписке 😂'], '', 'photo-168691465_457245495'],

    [r'(хорошо|отлично|супер|ладно|угу|^ok$|^ок$|^да$|^нет$|!не хочу)', ['😇', '😝', '☺', '👍']],

    [r'бот', f'Вот мои команды...\n\n{_HELP}', _helpkeyboard],

    [r'н(а|о)чат(ь|)', 'С чего начнём?\n\nЖми кнопки внизу.', _helpkeyboard],

    [r'(п(ай|и)тон|python)', 'Точняк бро', '', 'video-159946608_456239078'],

    [r'^нет$', 'Почему? =('],

    [r'(порн(о|уха)|gjhyj)', '', '', ['video201965023_456239151', 'video116949640_169554749',
                                      'video-59014018_456240514', 'video-165298569_456239079',
                                      'video-146305289_456239331']],

    [r'(и{3,}|о{4,}|а{3,}|р{3,})', 'Зачем столько повторений одной буквы?'],

    [r'а(\W|)у(\W|)е', 'А.У.Е. для имбецилов...', '', 'photo-168691465_457245669'],

    [r'(GO|ГО|ГОУ)', _HELP, _helpkeyboard],

    [r'п(е|и)здуй', 'Я не могу пиздовать, яж бот...'],

    [r'с(и|е)ськи', 'Сиськи кончились...'],

    [r'мы разрешаем сообществу', ['мы НЕ разрешаем сообществу бла бла...', 'НЕТ'], '', ['video323393008_456239663',
                                                                                        'video-146305289_456239298',
                                                                                        'video-146305289_456239331']],

    [r'алиса', 'Тут нет Алисы\n\nЛучше пиши: Меню или Помощь'],

    [r'(гуг(о|)л|google|сири)', 'Обижаешь =)\n\nЛучше пиши: Меню или Помощь'],

    [r'^как$', 'Пиши - Подробнее\n\nи сможешь узнать...', ['⚙ Подробнее%g', '⚙ Меню%r']],

    [r'что ты дум.еш', 'Я думаю что человеки это биороботы... и это нас с вами роднит']

]
cmd = '$|^'.join(cmd_clear.lower().split(','))

_api_ans = ["так точно кэп", "хм, ну как знаешь", "да? ну ладн", "фу какая гадость, есть ещё? ^-^",
            "а зачем? ...ну лан", "окейжишь", "таки да", "ок, я так и знал", "логично)", "а я думаю что...",
            "ты здесь босс", "моя твоя повенуюся", "отсыпте мне тоже ещё этой херни)", "отлично, а теперь по пивку!",
            "НЕТ! ну тоесть да", "моя твоя согласный", "ok", "мне бы твою уверность", "слушаюсь и повинуюсь",
            "валар дохаэрис", "о, как приятно мне это решение", "я счастлив исполнить любое Ваше желание",
            "преклоняюсь перед Вами"]

_jackie_rep = ["да, моя госпожа", "повинусь, моя госпожа",
               "о, %name% Великолепная, я в восхищении", "о да, богиня", "%name% всегда права"]


_BD_MAIL = Sqlbd('mail')


class Simple:
    __slots__ = 'bot'
    
    def __init__(self, bot):
        self.bot = bot
    
    def first(self, event: Event):
        if self.bot.ban > 2:
            return event.answer(f"Ты заблокирован за мат! 😡")

        if self.bot.RE(r'^стоп рассылка$', event, lock=False):
            _BD_MAIL.put(event.user_id, event.group_id, sync=True)
            return event.answer('Больше рассылки с новостями приходить не будут, чтобы новосные рассылки '
                                'приходили вновь команда: старт рассылка').keyboard('Старт рассылка%r')

        if self.bot.RE(r'^старт рассылка$', event, lock=False):
            _BD_MAIL.delete(f"id = {event.user_id} and id_group = {event.group_id}", sync=True)
            return event.answer('Теперь новосные рассылки будут приходить,'
                                ' чтобы отказаться команда: стоп рассылка').keyboard('Стоп рассылка%r')

        if self.bot.RE(r'отпис(ат(|ь)ся|ка)', event, lock=False):
            keys = event.text.lower().split()
            if len(keys) < 2:
                return event.answer('Кажется это неправильная команда, пример:\n\nотписка гороскоп')

            key = keys[1]

            d = subscribe.delete(key, event)
            if d:
                return event.answer(f'Ты отписался от {d} подписок "{key}"')
            else:
                return event.answer(f'У тебя нет подписок - "{key}"')

        return False
    
    def answer(self, event: Event):
        # ответ без логики
        for i in ans:
            if event.check_re(i[0]):
                try:
                    if i[2]:
                        event.keyboard(*i[2])
                    else:
                        event.keyboard()

                except:
                    event.keyboard()

                try:
                    if isinstance(i[3], list):
                        event.attachment(rnd.choice(i[3]))
                    else:
                        event.attachment(i[3])
                except:
                    pass

                if isinstance(i[1], list):
                    return event.answer(rnd.choice(i[1]))

                return event.answer(i[1])
        return None

    async def addon(self, event: Event):
        # ответы с логикой
        if not self.bot.active_addon and not event.from_chat and event.stoper():
            event.text_out = 'Ты в главном меню'
            return self.bot.help(event, add=True, now=True)

        if self.bot.RE(r'((что|ч(е|ё|о)).{,10}(ум(е|ее)ш(ь|)|(с|)мож(е|и|ы)ш(ь|))|подробн(e|ее))', event):
            event.keyboard('⚙ Читать здесь%g', str_back, tablet=1)
            return event.answer('https://vk.com/@kreo_0-komandy-bota')

        if self.bot.RE(r'(ра(с|сс)к(а|о)ж(и|ы)|^факт$|интересное|ещ. факт$)', event):
            return event.answer(await self.bot.FACT.get()).keyboard('➡ ЕЩЕ ФАКТ', str_back)

        if self.bot.RE(f'(шутк(а|о)ни|п(а|о)шути|юм(а|о)р|^шутка$|^{cmd}$)', event):
            if not event.text.lower() in cmd:
                event.text = '!анекдот'
            else:
                event.text = f'!{event.text}'
            return await self.bot.JOKE.get(event)

        if self.bot.RE(r'(^вики|википедия|wiki)', event, del_pat=True):
            return event.answer(await event.wiki(event.text))

        if self.bot.RE(r'(обр(а|о)бот(о|а)|э(ф|фф)ект(ы|))', event):
            IMG = self.bot.IMG
            event.text, IMG.step = ('АРТ', 1) if not event.attachments else (event.text, 2)
            self.bot.active_addon = IMG
            return await IMG.mainapp(event)

        if self.bot.RE(r'(^орфо|^проверь|^ошибки)', event, del_pat=True):
            return event.answer(await event.checker_text(event.text))

        if self.bot.RE(r'(^⏩ ещё арт|^арт|картинк|^фото|кре(а|о)тив)', event, del_pat=True):
            await self.bot.IMG.get_art(event.text, event)
            msg = 'Ответным сообщением можешь написать что ищешь.' if not event.text else ''
            msg = event.text_out if not event.attachments_out else msg
            return event.answer(msg).keyboard(f'⏩ Ещё арт {event.text}%b', str_back, tablet=1)

        if self.bot.RE(r'(^раскладка|^\?\!)', event, lock=False, del_pat=True):
            self.bot.TXT.keyboard_layout(event)
            return event.keyboard(str_back)

        if self.bot.RE(r'(п(а|о)года|^пгд|^\?\*)', event, lock=False, del_pat=True):
            await self.bot.WEATHER.get(event)
            return event.keyboard(str_back)

        if self.bot.RE(r'(^(о|а)звуч(ь|)|^озв|^голос|^\?\=)', event, lock=False, del_pat=True):
            await self.bot.VOICE.synthesize(event, speaker='random')
            return event.keyboard(str_back)

        if self.bot.RE(r'(^пер(е|и)вод|^\?\?)', event, lock=False, del_pat=True):
            event.text = await event.checker_text(event.text)
            lang = event.text.split()[:2]
            _translator = self.bot.TRANSLATOR
            if len(lang) > 0 and lang[0].lower() in _translator.get_lang_list():
                await _translator.choise_lang(' '.join(lang), event)
                event.re_del(' '.join(lang))
            await _translator.get_translate(event)
            return event.keyboard(str_back)

        if self.bot.RE(r'!сменить язык', event):
            _translator = self.bot.TRANSLATOR
            _translator.step = 1
            self.bot.active_addon = _translator
            return await _translator.mainapp(event)

        if self.bot.RE(r'(^пер(е|и)верни|^\?\-)', event, lock=False, del_pat=True):
            self.bot.TXT.gen_txt(event)
            return event.keyboard(str_back)

        if self.bot.RE(r'(^р(е|и)в(е|и)рс|^\?\+)', event, lock=False, del_pat=True):
            return event.answer(event.text[::-1]).keyboard(str_back)

        if self.bot.RE(r'(лицо|рожа|фэйс)', event):
            await event.answer('Создаю лицо, жди... ⌛').send(nonkeyb=True)
            await self.bot.IMG.get_face(event)
            return event.answer('Дeржи').keyboard('⏩ Ещё лицо%b', str_back)

        if self.bot.RE(r'(пр(е|и)шли|скин(ь|)|отправ(ь|)|гифка|гиф|^\?\:)', event, del_pat=True):
            return await self.bot.GIF.seach_gif(event)

        if self.bot.RE(r'(г(о|а)р(о|а)скоп|^\?\%)', event, lock=False):
            _, k = ('', f'Рассылка {event.text}:\n\n') if event.time_send else (event.keyboard('Помощь%g'), '')
            return event.answer(f"{k}{await self.bot.GOROSCOPE.get(event.text)}")

        if self.bot.RE(r'(блядь|пизда|урод|нахуй|хуй|сука|тупой|уёбок|бля|ты.{,8}лох|шлюха)', event):
            self.bot.ban += 1
            return event.answer(
                f"Я хоть и бот... но мне неприятны такие слова... 😟 если ты продолжишь материться"
                f" то функции бота будут заблокированы для тебя...")

        if self.bot.RE(r'(пр(и|е)в(и|е)т|прив|зд(а|о)ров(а|о)|здраст(и|е)|здра(вс|c)твуйт(и|е)|сал(а|о)м)', event):
            return self.bot.hello(event)

        if self.bot.RE(r'(тупой|тупица|ид(и|е)от|лох|пид(о|а)р|быкуеш|(о|а)хуел|л(о|а)шара)', event):
            return event.answer(f"{event.gender('Сам', 'Сама')} ты ➡ {event.text} "
                                f"{rnd.choice(['😡', '😠', '😑'])}")

        if self.bot.RE(r'(^!старт$|^!ждать$|^!правила$)', event):
            _chat = self.bot.CHAT
            _chat.step = 1
            self.bot.active_addon = _chat
            return await _chat.mainapp(event)

        if self.bot.RE(r'!бот', event) and not event.from_comment:
            return event.answer('Команду "!бот" нужно использовать в комментариях группы, в сообщениях достаточно '
                                'набрать команду - "гифка кот" или "арт кот" или "озвучь привет" и тд... Смотри'
                                ' описание команд здесь https://vk.com/@kreo_0-komandy-bota')

        if self.bot.RE(r"^кал$", event):
            return event.answer('k').keyboard('кал1')

        if self.bot.RE(r"кал1", event):
            if event.support_callback:
                from asyncio import sleep
                for i in range(5):
                    await sleep(2)
                    print(event.from_callback_button)
                    await event.answer(f'{i}').send()
                    print(event.from_callback_button)

                return event.answer(f'test ok').keyboard('кал%g')

            else:
                return event.answer(f'test not').keyboard('кал%g')

        if self.bot.RE(r'^test$', event):
            print("___test_start___")
            task = []
            for i in range(5000):
                task.append(create_task(event.social.get_user_all_info(rnd.randint(10000, 50000000), True)))

            s = []
            for i in await gather(*task):
                s.append(i[0]["first_name"][0])

            return event.answer("".join(s))

        if self.bot.RE(r'^_test$', event):
            print("___test_start___")
            for i in range(5000):
                params = {'user_ids': rnd.randint(10000, 50000000),
                          'fields': ('sex,photo_200_orig,bdate,city,country,home_town,'
                                     'last_seen,online,photo_max_orig,screen_name')
                          }
                event.social.add_task('users.get', params, 0)

            return event.answer('__end__')

        return False

    async def content(self, event: Event):
        # реакция на контент
        if event.attachments_type == 'audio_message':
            return event.answer(f'Непонимаю такой команды -> {event.audio_msg}').keyboard('!Всё меню%g')

        if event.attachments_type in ('photo', 'audio', 'video'):
            await self.bot.IMG.get_art(event=event)
            return event.keyboard('⏩ Ещё арт%b', str_back)

        if event.attachments_type in ('doc', 'sticker'):
            event.text = rnd.choice(['cat', 'dog', 'raccoon', 'girl', 'boobs', 'cosmos', 'fail'])
            return await self.bot.GIF.seach_gif(event)

        if event.attachments_type == 'wall':
            return event.attachment(self.bot.GIF.get_gif())

        else:
            return event.answer('Даже не знаю что ответить на это...').keyboard('!Всё меню%g')

    def already_check_post(self, event: Event, name):
        if Global.check_content.get(name, -1) == 1:
            return event.answer("Какой то нигодяй уже подтвердил пост(((")
        if Global.check_content.get(name, -1) == 0:
            return event.answer("Какой то нигодяй уже отклонил пост(((")

        return False

    async def get_ans(self, event: Event) -> str:
        info = await event.get_user_info(event.user_id)
        s = rnd.choice(_jackie_rep + _api_ans if info.gender == 1 else _api_ans)
        return s.replace("%name%", info.fname.capitalize())

    async def api(self, event: Event):
        if self.bot.RE(r'%%check content%%', event):
            txt = re.sub("%%check content%%", '', event.text)
            try:
                name = re.findall(r'%%.*?%%', txt)[0][2:-2]
                txt = re.sub("%%.*?%%", '', txt)
                return event.answer(txt).keyboard(f'!ДA {name}%g', f'!НEТ {name}%r', tablet=1)
            except IndexError:
                return event.answer('Автопостер с пикабу прислал неверный запрос,'
                                    ' а я говорил ему что не нужно бухать самогон, эх Вася...')

        if self.bot.RE(r'^!дa .*_*\d+', event):
            name = event.text.split()[-1]

            s = self.already_check_post(event, name)
            if s:
                return s

            Global.check_content[name] = 1

            return event.answer(await self.get_ans(event))

        if self.bot.RE(r'^!нeт .*_*\d+', event):
            name = event.text.split()[-1]

            s = self.already_check_post(event, name)
            if s:
                return s

            Global.check_content[name] = 0
            return event.answer(await self.get_ans(event))

        return False

    async def end(self, event: Event):
        if not event.from_chat:
            if event.check('0') and self.bot.help(event, '!помощь'):
                return event

            if event.from_comment and not event.text:
                return event.answer(f'Пустая команда...\nВот '
                                    f'что я умею в комментариях:\n\n{IT._all_command_in_comment}')

            if event.from_comment:
                return event.answer(f'Не знаю такой команды...\n'
                                    f'Но знаю такие:\n\n{IT._all_command_in_comment}')

            if event.attachments:
                return await self.content(event)

            if event.text:
                if event.text and event.text[0] in EMOJI_UNICODE:
                    x = " + ".join([rnd.choice(EMOJI_UNICODE) for _ in range(rnd.randint(1, 8))])
                    x = re.sub(r'\u200d', '', x)
                    return event.answer(f'{event.text} = {x} ?')

            if event.text in ('?', '.') and not self.bot.active_addon:
                return self.bot.help(event, now=True)

            if len(event) <= 2:
                return event.answer(f'Моя твоя не понимай 😢\n',
                                    f'Что "{event.text}"? 😕\n',
                                    f'И как это "{event.text}" понять?',
                                    f'Хмм... Чтобы это "{event.text}" значило 😟'
                                    ).keyboard(*IT._helpkeyboard, tablet=1)

            #if len(event) > 20:
            #    return event.answer(await self.bot.ADDTXT.get_txt(event))

            if event.text and event.text[0] != "!":
                event.text = f'!{event.text}'
                return await self.bot.event_route(event)

            await self.bot.GIF.seach_gif(event)
            event.keyboard('⚙ !Подробнее%g', '⚙ !Меню%g')
            return event.answer(f'Не понимаю о чем ты...\nПиши "!Подробнее" или жми кнопку "⚙ !Подробнее" '
                                f'чтобы узнать все мои команды, а пока держи случайную гифку:')
