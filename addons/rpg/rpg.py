from untils import Event, Button
from PIL import Image
from io import BytesIO
from Addon import Addon, middelware, addon_init

list_button = [
    Button('↖', type_button=Button.CALLBACK, payload='6'),
    Button('⬆', type_button=Button.CALLBACK, payload='5'),
    Button('↗', type_button=Button.CALLBACK, payload='4'),

    Button('⬅', type_button=Button.CALLBACK, payload='7'),
    Button('⏺', type_button=Button.CALLBACK, payload='8'),
    Button('➡', type_button=Button.CALLBACK, payload='3'),

    Button('↙', type_button=Button.CALLBACK, payload='0'),
    Button('⬇', type_button=Button.CALLBACK, payload='1'),
    Button('↘', type_button=Button.CALLBACK, payload='2'),

    Button('Назад', type_button=Button.CALLBACK, payload='Назад'),
]


class Point:
    __slots__ = ('x', 'y', 'size')

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20

    def move(self, x, y):
        self.x += x
        self.y += y


@addon_init(['!RPG'], '', False, 0)
class RPG(Addon):
    __slots__ = ('point', 'img')

    def __init__(self, username='', user_id=0):
        super(RPG, self).__init__(username, user_id)
        self.point = Point(200, 200)
        self.img = Image.new('RGB', (400, 500), (255, 255, 255))

    def move(self, event: Event):
        s = 20

        if event.check("0"):
            self.point.x -= s
            self.point.y += s

        elif event.check("1"):
            self.point.y += s

        elif event.check("2"):
            self.point.x += s
            self.point.y += s

        elif event.check("3"):
            self.point.x += s

        elif event.check("4"):
            self.point.x += s
            self.point.y -= s

        elif event.check("5"):
            self.point.y -= s

        elif event.check("6"):
            self.point.x -= s
            self.point.y -= s

        elif event.check("7"):
            self.point.x -= s

    def to_byte(self, img):
        stream = BytesIO()
        img.save(stream, format="JPEG", quality=60)
        stream.seek(0)
        img = stream.read()
        return img

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if not event.support_callback:
            return event.answer('Сейчас игра может работать только официальном приложение вконтакте')

        event.keyboard(*list_button, tablet=3)

        if self.isstep(0, 1):
            self.img = Image.new('RGB', (400, 500), (255, 255, 255))
            await event.uploads(self.to_byte(self.img))
            return event.answer("RPG")

        if self.isstep(1):
            self.move(event)
            point_img = Image.new("RGB", (self.point.size, self.point.size), (0, 0, 0))
            self.img.paste(point_img, (self.point.x, self.point.y), )

            await event.uploads(self.to_byte(self.img))
            return event.answer("RPG")




