from untils import Event, until
from Addon import Addon, middelware, addon_init
from Template import str_back
import random as rnd
from asyncio import sleep
from typing import Dict, Optional
from asyncio import create_task


_win = ['doc17626786_581316037',
        'doc180420411_437105505',
        'doc515095586_582185652',
        'doc363679046_442422674',
        'doc75817738_582527223',
        'doc303613637_518324647',
        'doc151643704_532101706',
        'doc14066552_137335517',
        'doc258816641_553907889',
        'doc444394016_495850818',
        'doc572132687_560125324',
        'doc205532613_437437398',
        'doc160334667_455901350',
        'doc512104357_570596977',
        'doc474899960_587297267',
        'doc226420670_583482978',
        'doc466073640_551007853',
        'doc622999024_582495769',
        ]


def you_win():
    return rnd.choice(_win)


class Board:
    empty = 0
    ship = 1
    not_open = -1
    ship_dead = -2
    miss = -3

    __slots__ = ()


class Game:
    __slots__ = ('ships', 'size_x', 'size_y', 'my_board', 'enemy_board',
                 'count_dead', 'coord_my_ships', 'moves', 'd_ships')

    def __init__(self):
        self.ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.size_x = 10
        self.size_y = 10
        self.my_board = self.create_board(Board.empty)
        self.enemy_board = self.create_board(Board.not_open)

        self.count_dead = 0
        self.coord_my_ships = []
        self.moves = set()
        self.d_ships = []
        self.random_spawn_ship()

    def create_board(self, p: int):
        board = []
        for _ in range(self.size_y):
            line = []
            for _ in range(self.size_x):
                line.append(p)
            board.append(line)
        return board

    def rnd_coord(self):
        return rnd.randint(0, self.size_x - 1), rnd.randint(0, self.size_y - 1)

    def correct(self, coord: tuple) -> tuple:
        x, y = coord
        x = 0 if x < 0 else x
        y = 0 if y < 0 else y
        x = self.size_x - 1 if x >= self.size_x else x
        y = self.size_y - 1 if y >= self.size_y else y
        return x, y

    def get_rnd_coord(self, len_ship, pos):
        if pos:
            return rnd.randint(0, self.size_x - len_ship - 1), rnd.randint(0, self.size_y - 1)
        else:
            return rnd.randint(0, self.size_x - 1), rnd.randint(0, self.size_y - len_ship - 1)

    def get_enemy(self, coord) -> int:
        return self.enemy_board[coord[1]][coord[0]]

    def get_my(self, coord) -> int:
        return self.my_board[coord[1]][coord[0]]

    def write_my(self, coord, val):
        self.my_board[coord[1]][coord[0]] = val

    def write_enemy(self, coord, val):
        self.enemy_board[coord[1]][coord[0]] = val

    def write_my_ship(self, coord: tuple):
        x, y = coord
        self.write_my((x, y), Board.ship)
        for y, x in [(y, x),
                     (y, x - 1),
                     (y - 1, x - 1),
                     (y - 1, x),
                     (y - 1, x + 1),
                     (y, x + 1),
                     (y + 1, x + 1),
                     (y + 1, x),
                     (y + 1, x - 1)]:
            i = (x, y)
            if i not in self.coord_my_ships:
                self.coord_my_ships.append(i)

    def write_enemy_ship(self, coord: tuple):
        self.write_enemy(coord, Board.ship)

    def write_my_dead(self, coord: tuple):
        self.write_my(coord,  Board.ship_dead)

    def write_enemy_dead(self, coord: tuple):
        self.write_enemy(coord, Board.ship_dead)

    def write_my_miss(self, coord: tuple):
        self.write_my(coord, Board.miss)

    def write_enemy_miss(self, coord: tuple):
        self.write_enemy(coord, Board.miss)

    def is_my_ship(self, coord: tuple) -> bool:
        return self.get_my(coord) == Board.ship

    def is_dead_my(self, coord: tuple) -> bool:
        return self.get_my(coord) == Board.ship_dead

    def is_dead_enemy(self, coord):
        return self.get_enemy(coord) == Board.ship_dead

    def write_ship_on_board(self, coord: tuple, len_ship: int, pos: bool):
        x, y = coord
        for i in range(len_ship):
            self.write_my_ship((x, y))

            if pos:
                x += 1
            else:
                y += 1

    def check_pos(self, coord: tuple, len_ship: int, pos: bool) -> bool:
        x, y = coord
        for _ in range(len_ship):
            if (x, y) in self.coord_my_ships:
                return False
            if pos:
                x += 1
            else:
                y += 1

        return True

    def random_spawn_ship(self):
        for len_ship in self.ships:
            while True:
                # True horizontal else vertical
                pos = rnd.random() < 0.5
                coord = self.get_rnd_coord(len_ship, pos)
                if coord in self.coord_my_ships or not self.check_pos(coord, len_ship, pos):
                    continue

                self.write_ship_on_board(coord, len_ship, pos)
                self.d_ships.append([coord, len_ship, pos])
                break

    def manual_spawn_ship(self):
        pass

    def rend(self, x):
        s = ''
        if x == Board.empty:
            s = '⬜'
        elif x == Board.ship:
            s = '⬛'
        elif x == Board.not_open:
            s = '▫'
        elif x == Board.ship_dead:
            s = "💥"
        elif x == Board.miss:
            s = "❌"
        return s

    def rend_board(self):
        s = ''
        for i, y in enumerate(self.my_board):
            s += until.int_to_smail(i)
            for x in y:
                s += self.rend(x)
            s += '\n'

        s += '⬜' + ''.join([until.int_to_smail(i) for i in range(10)]) + '\n'

        for i, y in enumerate(self.enemy_board):
            s += until.int_to_smail(i)
            for x in y:
                s += self.rend(x)
            s += '\n'

        return s

    def c_cursor(self, coord, pos, val=1):
        x, y = coord
        return [(x - val, y), (x, y - val), (x + val, y), (x, y + val)][pos]

    def check_dead(self, coord: tuple) -> int:
        for pos in range(4):
            i = coord
            for _ in range(4):
                i = self.c_cursor(i, pos)
                i = self.correct(i)

                if self.is_my_ship(i) and i != coord:
                    return False

                if self.get_my(i) == Board.empty or self.get_my(i) == Board.miss:
                    break

        return True

    def check_win(self):
        return self.count_dead == sum(self.ships)

    def move(self, coord) -> (int, bool):
        if self.is_my_ship(coord):
            self.count_dead += 1
            b = self.check_dead(coord)
            return Board.ship_dead, b
        else:
            return Board.miss, False


def open_dead(g: Game, coord, l=None):
    x, y = coord
    if l is None:
        l = []
    for y, x in [(y, x),
                 (y, x - 1),
                 (y - 1, x - 1),
                 (y - 1, x),
                 (y - 1, x + 1),
                 (y, x + 1),
                 (y + 1, x + 1),
                 (y + 1, x),
                 (y + 1, x - 1)]:
        i = x, y
        i = g.correct(i)
        if g.is_dead_enemy(i) and i not in l:
            l.append(i)
            open_dead(g, i, l)
        elif g.get_enemy(i) == Board.not_open:
            g.moves.add(i)
            g.write_enemy(i, Board.empty)


_session = {}

_in_game = {}


keyb = ["!старт бот%b", '!старт человек%b', str_back]

keyb_in_game = ["!стоп%b", str_back]


class Ai(Game):
    __slots__ = ('ai_last_good_move', 'ai_last_miss', 'ai_pos', 'count_good_move', 'rout')

    def __init__(self, rout):
        super(Ai, self).__init__()

        self.ai_last_good_move = ()
        self.ai_last_miss = ()
        self.ai_pos = -1
        self.count_good_move = 0

        self.rout = rout

    def get_ai_coord(self):
        coord = self.rnd_coord()
        while coord in self.moves:
            coord = self.rnd_coord()
        return coord

    def correct_ai_coord(self, s, pos):
        if pos > 0:
            for j in range(1, 3):
                coord = self.c_cursor(s, pos, j)
                coord = self.correct(coord)
                if coord not in self.moves:
                    return coord, pos

        for j in range(1, 3):
            p = []
            for i in range(4):
                coord = self.c_cursor(s, i, j)
                coord = self.correct(coord)
                if coord not in self.moves:
                    p.append((coord, i))
            if p:
                return rnd.choice(p)

        return self.get_ai_coord(), -1

    async def ai_move(self, event, player: Game):
        if self.ai_last_good_move:
            if self.count_good_move < 2:
                self.ai_pos = -1
            coord, self.ai_pos = self.correct_ai_coord(self.ai_last_good_move, self.ai_pos)
        else:
            coord = self.get_ai_coord()
        v, b = self.rout.move(player, self, coord)

        m = 'Бот промахнулся твой ход\n'
        d = 'Бот попал, его ход\n'

        msg = m
        if v == Board.ship_dead:
            while True:
                msg = d if v == Board.ship_dead else m

                await event.answer(player.rend_board() + msg).send(nonkeyb=True)
                await sleep(1)

                if player.check_win():
                    await self.rout.disconnect()
                    return event.answer("Ха-ха бот тебя обыграл!\nЧтобы "
                                        "попробовать ещё !старт бот").keyboard(*keyb)

                if v == Board.ship_dead:
                    if not b:
                        self.count_good_move += 1
                        self.ai_last_good_move = coord
                    else:
                        self.count_good_move = 0
                        self.ai_last_good_move = ()
                else:
                    if self.count_good_move > 1:
                        self.ai_pos = (self.ai_pos + 2) % 4
                        coord = self.c_cursor(coord, self.ai_pos, self.count_good_move - 1)
                        self.ai_last_good_move = coord

                    self.ai_last_miss = coord
                    msg = m
                    break

                if not b:
                    coord, self.ai_pos = self.correct_ai_coord(coord, self.ai_pos)
                else:
                    self.count_good_move = 0
                    self.ai_pos = -1
                    coord = self.get_ai_coord()

                v, b = self.rout.move(player, self, coord)

        await event.answer(player.rend_board() + msg).keyboard(None).send(nonkeyb=True)

        return Event(0)


@addon_init(['!МОРСКОЙ БОЙ'], '💥', False, 1)
class SeaBattle(Addon):
    __slots__ = ('session', 'in_game', 'player1', 'player2', 'ai', 'ids', 'my_step', 'con')

    def __init__(self, username, user_id):
        super(SeaBattle, self).__init__(username, user_id)
        self.session: Dict[tuple, SeaBattle] = _session
        self.in_game = _in_game
        self.player1: Optional[Game] = None
        self.player2: Optional[Ai, Game] = None
        self.ai: bool = False
        self.ids: tuple = ()
        self.my_step: bool = True

        self.con: Optional[SeaBattle] = None

    async def disconnect_msg(self, event):
        await self.send_another_player(event, "Другой игрок отключился от игры", keyb)

    def move(self, g1: Game, g2: Game, coord: tuple) -> (int, bool):
        a, b = g1.move(coord)
        g2.moves.add(coord)
        if a == Board.ship_dead:
            g1.write_my_dead(coord)
            g2.write_enemy_dead(coord)
        if a == Board.miss:
            g1.write_my_miss(coord)
            g2.write_enemy_miss(coord)

        if b:
            open_dead(g2, coord)

        return a, b

    async def send(self, event, msg1, msg2, nonkeyb=True, is_miss=True):
        await self.send_another_player(event, msg2, is_miss=is_miss)
        await event.answer(msg1).send(nonkeyb=nonkeyb)

        if self.player2.check_win():
            await self.disconnect()
            await self.send_another_player(event, "Другой игрок победил(", keyb)
            event.attachment(you_win())
            return event.answer(f"Ура ты победи{event.gender('л', 'ла')}!").keyboard(*keyb)

        if self.player1.check_win():
            await self.disconnect()
            event.attachment(you_win())
            await self.send_another_player(event, "Ура победа!", keyb)
            event.attachment('')
            return event.answer(f"Увы фортуна сегодня не твоей стороне "
                                f"ты проигра{event.gender('л', 'ла')}(((").keyboard(*keyb)

        return Event(0)

    async def send_another_player(self, event: Event, msg, keyboard: list = None, is_miss=True):
        self.my_step = not is_miss
        if not self.ai and self.con:
            self.con.my_step = is_miss
            group, user_id = self.in_game.get(self.ids)
            is_keyb = False
            if keyboard:
                is_keyb = True
                event.keyboard(*keyboard)
            await event.answer(msg).send(nonkeyb=is_keyb, group=group, peer_id=user_id)

    async def check_and_work(self, event):
        i = event.text.split()
        event.keyboard(*keyb_in_game)
        if len(i) != 2:
            return event.answer('Нужно 2 числа')
        try:
            coord = int(i[1]), int(i[0])
            coord = self.player1.correct(coord)
        except TypeError:
            return event.answer("Нужны числа")

        if not self.my_step:
            return event.answer(f"Сейчас ход твоего соперника, "
                                f"если не хочешь ждать команда !отключиться").keyboard('!стоп')

        cell = self.player1.get_enemy(coord)
        if cell == Board.ship_dead or cell == Board.miss:
            return event.answer(f"Ты уже сюда стреля{event.gender('л', 'ла')}")

        return await self.do(event, coord)

    async def do(self, event: Event, coord) -> Event:
        v, b = self.move(self.player2, self.player1, coord)

        s = self.player1.rend_board()
        s2 = self.player2.rend_board() if not self.ai else ''

        g = event.gender("л", "ла")
        m0 = f"{s}Промаза{g}, ход противника...\n"
        m1 = f'Ура ты потопи{g} корабль врага, твой ход\n'
        m2 = f'Ура! попа{g}, твой ход\n'
        p0 = f'{s2}Противник промахнулся, твой ход'
        p1 = f'{s2}Противник подбил твой корабль, его ход'

        msg = m1 if b else m2

        if v == Board.miss:
            await self.send(event, m0, p0)
        else:
            return await self.send(event, s + msg, p1, is_miss=False)

        await sleep(0.3)

        if self.ai:
            event = await self.player2.ai_move(event, self.player1)
            self.my_step = True
            return event

        return event

    async def connect(self, event: Event) -> Event:
        ids = (event.group_id, event.user_id)
        self.ids = ids

        if self.session:
            s = rnd.choice(list(self.session.keys()))
            p = self.session[s]

            del self.session[s]

            p.player2 = self.player1
            self.player2 = p.player1

            self.in_game[s] = ids
            self.in_game[ids] = s

            group, user_id = p.ids

            p.my_step = False
            self.my_step = True

            self.con = p
            p.con = self

            await event.answer("Подключился игрок, он делает первый ход"
                               ).keyboard(*keyb_in_game).send(peer_id=user_id, group=group)

            return event.answer("Подключились к игроку, делай первый ход"
                                ).keyboard(*keyb_in_game)

        else:
            self.my_step = False
            self.session[ids] = self
            return event.answer("Нет доступных игроков, ждем когда кто-то подключится"
                                ).keyboard(*keyb_in_game)

    async def disconnect(self):
        if self.in_game.get(self.ids):
            del self.in_game[self.ids]
        if self.session.get(self.ids):
            del self.session[self.ids]

        if self.con and self.in_game.get(self.con.ids):
            del self.in_game[self.con.ids]
        if self.con and self.session.get(self.con.ids):
            del self.session[self.con.ids]

        self.ids = ()
        self.my_step = True
        self.ai = False

        self.setstep(1)

        if self.con:
            self.con.ids = ()
            self.con.step = 1
            self.con.con = None
            self.con.my_step = True
            self.con = None

    def end(self, event: Optional[Event] = None):
        self.step = 0
        create_task(self.disconnect_msg(event))
        create_task(self.disconnect())

    @middelware
    async def mainapp(self, event: Event) -> Event:
        if event.check('!старт бот'):
            self.setstep(2)
            self.player1 = Game()
            s = self.player1.rend_board() + 'Твой ход, начинай)'

            self.player2 = Ai(self)
            self.ai = True
            self.my_step = True
            return event.answer(s)

        if event.check('!старт человек'):
            self.setstep(2)
            self.player1 = Game()
            s = self.player1.rend_board()
            await event.answer(s).send()

            return await self.connect(event)

        if event.check('!стоп'):
            await self.disconnect_msg(event)
            await self.disconnect()
            return event.answer("Отключились от игры").keyboard(*keyb)

        if self.isstep(0, 1):
            return event.answer('Морской бой').keyboard(*keyb, tablet=1)

        if self.isstep(2):
            return await self.check_and_work(event)

        return event.answer('Чтобы выйти !назад').keyboard(*keyb)









