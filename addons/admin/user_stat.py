from untils import Global
from Addon import Addon, addon_init, middelware
from Template import str_back
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

keyb = ['!Правила начисления очков%b', str_back]


@addon_init(['стат', '!статистика', '!правила начисления очков'], '', False, 0)
class Statistic(Addon):
    __slots__ = ()

    def draw_text(self, draw, coor, text, fnt):
        Global.cover.draw_outline(draw, coor[0], coor[1],
                                  text, "#000000", fnt, "center", int(65 / 4))
        draw.text(coor, text, fill="#ffffff", font=fnt,
                  align="center", spacing=int(65 / 4))

    @middelware
    async def mainapp(self, event):
        if event.check('!правила начисления очков'):
            return event.answer('5 - за комментарий\n'
                                '5 - за лайк в первые 10 минут после публикации поста\n'
                                '3 - за лайк с 10 до 30 минут\n'
                                '1 - за лайк после 30 минут\n'
                                '1 - за лайк комментария другого юзера\n'
                                '1 - за каждые 3 лайка твоего комментария\n'
                                'Учитываются только участники группы, самолайки не считаются =)'
                                ).keyboard(str_back)

        if event.from_telegram:
            return event.answer('В телеге статистика не работает').keyboard(str_back)

        if not Global.cover:
            return event.answer('К этой группе статистика активности не подключена.')

        stat = Global.cover.groups_wal_stat
        stat = stat.get(f'-{event.group_id}', '')

        if stat:
            event.keyboard(*keyb,  tablet=1)

            if not await event.is_member():
                return event.answer('Статистика активности доступна только подписчикам сообщеста =)')

            stat = await Global.cover.get_max_user_stat(stat, f'-{event.group_id}')
            data = stat[:10] + [[str(event.user_id), 0]]

            img = Image.open('addons/admin/1.jpg')
            draw = ImageDraw.Draw(img)
            fnt = ImageFont.truetype('cover/GothaProBol.otf', 24)
            avatar = await Global.cover.get_avatar_and_name(data)
            flag = True
            cr = 0

            for j, i in enumerate(avatar[:10]):
                if i[0] == str(event.user_id):
                    txt = f'{j + 1}. Ты - {i[1]}'
                    flag = False
                else:
                    txt = f'{j + 1}. {i[2]} - {i[1]}'

                av = Image.open(i[3])
                av = av.resize((60, 60), Image.ANTIALIAS)
                av = Global.cover.add_corners(av, 10)
                img.paste(av, (50, j * 70 + 40), av)
                self.draw_text(draw, (50 + 70, j * 70 + 60), txt, fnt)
                cr += 1

            if flag:
                msg = f'{len(stat)}. Ты'
                for j, i in enumerate(stat):
                    if i[0] == str(event.user_id) or j == len(stat)-1:
                        if j != len(stat)-1:
                            msg = f'{j+1}. Ты - {i[1]}'

                        self.draw_text(draw, (50, 10 * 70 + 70), '* * * * * * * * * * * * * * *', fnt)
                        av = Image.open(avatar[-1][3])
                        width = av.size[0]  # Определяем ширину
                        height = av.size[1]

                        if width > height:
                            z = width - height
                            pos = (z // 2, 0, width - z // 2, height)
                            av = av.crop(pos)
                        if width < height:
                            z = height - width
                            pos = (0, z // 2, width, height - z // 2)
                            av = av.crop(pos)

                        av = av.resize((60, 60), Image.ANTIALIAS)
                        av = Global.cover.add_corners(av, 45)
                        img.paste(av, (50, 11 * 70 + 40), av)
                        self.draw_text(draw, (50 + 70, 11 * 70 + 60), msg, fnt)
                        cr += 2

            img = img.crop((0, 0, img.size[0], 70 * cr + 50))

            stream = BytesIO()
            img.save(stream, format="JPEG", quality=75)
            stream.seek(0)
            img = stream.read()

            await event.uploads(img)
            return event

        else:
            return event.answer('К этой группе статистика активности не подключена.').keyboard(str_back)
