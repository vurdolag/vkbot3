import random as rnd
from untils import until, Event, ImgCreator
from Addon import Addon, middelware, addon_init
from Template import str_back
import time


mine = -2
empty = -1
not_open = 0

NotWork = 0
Start = 1
Diff = 2
InGame = 3

back = [str_back]
keyb = ["!старт%b", "!сложность%b"]


Img = ImgCreator('addons/soper/img/back.jpg')
Img.add(mine, 'addons/soper/img/mine.png')
Img.add(not_open, 'addons/soper/img/empty.png')
Img.add(empty, 'addons/soper/img/not_open.png')


class Game:
    def __init__(self, size_x, size_y, diff):
        self.size_x = size_x
        self.size_y = size_y
        self.diff = diff
        self.mine_board = []
        self.view_board = []
        self.count_mine = 0
        self.step = 0
        self.verb_board = []
        self.need_mine = int(size_x * size_y * diff)
        self.ch = []

    def add_view(self, x, y, val):
        if self.view_board[y][x] == empty:
            self.step += 1
        self.view_board[y][x] = val

    def is_empty_view(self, x, y):
        return self.view_board[y][x] == empty

    def is_mine(self, x, y):
        return self.mine_board[y][x] == 1

    def is_ziro(self, x, y):
        return self.verb_board[y][x] == 0

    def create(self):
        for _ in range(self.size_y):
            temp = []
            for _ in range(self.size_x):
                if rnd.random() < self.diff / 3:
                    temp.append(1)
                    self.count_mine += 1
                else:
                    temp.append(0)
            self.mine_board.append(temp)
            self.view_board.append([empty] * self.size_x)

        if self.count_mine < self.need_mine:
            while True:
                for y in range(self.size_y):
                    for x in range(self.size_x):
                        if self.mine_board[y][x] != 1:
                            if rnd.random() < self.diff / 4:
                                self.mine_board[y][x] = 1
                                self.count_mine += 1
                        if self.count_mine == self.need_mine:
                            return

    def create_board(self):
        self.create()
        for y in range(self.size_y):
            temp = []
            for x in range(self.size_x):
                temp.append(self.get_near(x, y))
            self.verb_board.append(temp)

    def get_near(self, x, y):
        count_mine = 0
        y1 = y - 1 if y - 1 >= 0 else 0
        for line in self.mine_board[y1:y+2]:
            x1 = x - 1 if x - 1 >= 0 else 0
            for xl in line[x1:x+2]:
                count_mine += xl
        return count_mine

    def get_board(self):
        return self.view_board

    def print_bord(self, l):
        s = ''
        for y in l:
            for x in y:
                if x == empty:
                    s += '❓'
                elif x == mine:
                    s += '🙃'
                else:
                    s += until.int_to_smail(x)
            s += '\n'
        return s

    def correct(self, i):
        y, x = i
        y = y if y < self.size_y else self.size_y - 1
        x = x if x < self.size_x else self.size_x - 1
        y = 0 if y < 0 else y
        x = 0 if x < 0 else x
        return y, x

    def open_near_one(self, x, y):
        for i in [(y, x), (y, x - 1), (y - 1, x - 1), (y - 1, x), (y - 1, x + 1),
                  (y, x + 1), (y + 1, x + 1), (y + 1, x), (y + 1, x - 1)]:
            i = self.correct(i)
            if self.is_empty_view(i[1], i[0]):
                self.add_view(i[1], i[0], self.verb_board[i[0]][i[1]])

    def ziro(self, x, y):
        for i in [(y, x - 1), (y - 1, x), (y, x + 1), (y + 1, x)]:
            y, x = self.correct(i)
            if self.is_ziro(x, y):
                if i not in self.ch:
                    self.ch.append(i)
                    self.open_near_one(x, y)
                    self.ziro(x, y)

    def open_board(self):
        for y in range(self.size_y):
            for x in range(self.size_x):
                if self.is_empty_view(x, y):
                    if self.is_mine(x, y):
                        self.add_view(x, y, mine)
                    else:
                        self.add_view(x, y, self.verb_board[y][x])

    def check(self, x, y) -> (bool, bool):
        x, y = y, x
        if self.is_mine(x, y):
            self.add_view(x, y, mine)
            self.open_board()
            return False, False

        count = self.get_near(x, y)
        self.add_view(x, y, count)
        if count == 0:
            self.ch = []
            self.ziro(x, y)

        if self.size_y * self.size_x - self.step == self.count_mine:
            self.open_board()
            return True, False

        return False, True


@addon_init(["!САПЕР", 'САПЁР', 'СОПЕР'], '💣', False, 1)
class Soper(Addon):
    __slots__ = 'game', 'diff', 'size_x', 'size_y', 'board_to_img', 'count_step', 'time_start'

    def __init__(self, username, user_id):
        super(Soper, self).__init__(username, user_id)
        self.game: Game = None
        self.diff = 20
        self.size_x = 8
        self.size_y = 8
        self.board_to_img = False
        self.count_step = 0
        self.time_start = 0

    def to_smail(self, board, event):
        s = ''
        if self.count_step == 0:
            s = 'Напиши два числа через пробел, номер по горизантали и по вертикали\n\n'
        l = '▫' * (self.size_x + 2)
        s += f'Мины {self.game.count_mine}     Ход: {self.count_step}\n▫▫'
        s += ''.join([until.int_to_smail(i) for i in range(self.size_x)]) + f'\n{l}\n'
        for i, y in enumerate(board):
            s += until.int_to_smail(i) + '▫'
            for x in y:
                if x == mine:
                    s += '💣'
                elif x == empty:
                    s += '⬛'
                elif x == not_open:
                    s += '⬜'
                else:
                    s += until.int_to_smail(x)
            s += "\n"

        return event.answer(s)

    async def to_img(self, board, event: Event):
        y = 107
        for j in board:
            x = 19
            for i in j:
                if i <= 0:
                    Img.write(i, (x, y))
                else:
                    Img.write(not_open, (x, y))
                    Img.write_d(i, (x+8, y+5), "#ffffff")
                x += 32
            y += 32
        return await event.uploads(Img.get_img_byte())

    async def rend(self, event: Event, msg='', end_msg=''):
        board = self.game.get_board()
        if self.board_to_img:
            await self.to_img(board, event)
        else:
            self.to_smail(board, event)

        if msg:
            event.text_out = msg + event.text_out
        if end_msg:
            event.text_out += end_msg

        return event.keyboard(*back)

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if event.check("сложность"):
            self.setstep(Diff)
            return event.answer("Введи число от 10 до 100, где 10 самый простой 100 максимально сложный."
                                ).keyboard(*keyb, *back, tablet=1)
        if event.check("старт"):
            self.count_step = 0
            self.time_start = time.time()
            self.setstep(InGame)
            self.game = Game(self.size_x, self.size_y, self.diff/100/2)
            self.game.create_board()
            return await self.rend(event)

        if self.isstep(NotWork, Start):
            return event.answer("Игра сапер.\n!Старт\n!Сложность").keyboard(*keyb, *back, tablet=1)

        if self.isstep(InGame):
            pos = event.text.split()
            if len(pos) != 2:
                return event.answer('Нужно 2 числа через пробед по горизантали и по вертикали, '
                                    'например:\n 5 6 или 1 4...'
                                    ).keyboard(*back, tablet=1)
            try:
                x = int(pos[0])
                y = int(pos[1])
            except:
                return event.answer("Нужны числа через пробел, "
                                    "например:\n 5 6 или 1 4 ..."
                                    ).keyboard(*back, tablet=1)

            win, next_iter = self.game.check(x, y)

            if next_iter:
                self.count_step += 1
                return await self.rend(event)

            elif not next_iter and not self.count_step:
                while True:
                    self.count_step = 0
                    self.time_start = time.time()
                    self.setstep(InGame)
                    self.game = Game(self.size_x, self.size_y, self.diff / 100 / 2)
                    self.game.create_board()
                    _, next_iter = self.game.check(x, y)
                    if next_iter:
                        return await self.rend(event)

            else:
                self.count_step += 1
                if win:
                    msg = f'Ты победи{event.gender("л", "ла")}! Поздравляю!'

                else:
                    msg = f'Ты взорвал{event.gender("ся", "ась")}. Сочувствую...'

                msg += f'\nВремя: {int(time.time() - self.time_start)} секунд\n'

                await self.rend(event, msg)
                return event.keyboard(*keyb, *back, tablet=1)

        if self.isstep(Diff):
            try:
                i = int(event.text)
                if i > 100:
                    i = 100
                if i < 10:
                    i = 10
                self.diff = i

                self.setstep(Start)
                return event.answer(f"Ты выбрал сложность {self.diff}\n!старт - начать игру"
                                    ).keyboard(*keyb, *back, tablet=1)

            except:
                return event.answer("Нужно ввести число").keyboard(*keyb, *back, tablet=1)




