# -*- coding: utf-8 -*-
from untils import until, Event
from Addon import Addon, middelware, addon_init
from Template import str_back

import asyncio
import random as rnd

its = until.int_to_smail
keyb = [str_back]
keyb_dig = ['1', '2', '3', '4', '5', '6', '7', '8', '9', *keyb]

WAYS_TO_WIN = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]


@addon_init(['!КРЕСТИКИ-НОЛИКИ', 'КРЕСТИКИ НОЛИКИ'], '❌', False, 1)
class XO(Addon):
    __slots__ = 'X', 'O', 'EMPTY', 'TIE', 'NUM_SQUARES', 'board', 'computer', 'human', 'turn', 'ind'

    def __init__(self, username, user_id):
        super(XO, self).__init__(username, user_id)
        self.X = "❌"
        self.O = "🔘"
        self.EMPTY = [str(i) for i in range(1, 10)]
        self.TIE = "Ничья"
        self.NUM_SQUARES = 9
        self.board = [str(i) for i in range(1, 10)]
        self.computer = ''
        self.human = ''
        self.turn = self.X
        self.ind = 0

    def upd(self):
        self.board = [str(i) for i in range(1, 10)]
        self.computer = ''
        self.human = ''
        self.turn = self.X

    def display_board(self):
        b = ''
        b += f"\n{its(self.board[0])} | {its(self.board[1])} | {its(self.board[2])}"
        b += f"\n- - - - - - - - - -"
        b += f"\n{its(self.board[3])} | {its(self.board[4])} | {its(self.board[5])}"
        b += f"\n- - - - - - - - - -"
        b += f"\n{its(self.board[6])} | {its(self.board[7])} | {its(self.board[8])}\n"
        return b

    def legal_moves(self, board):
        moves = []
        for square in range(self.NUM_SQUARES):
            if board[square] in self.EMPTY:
                moves.append(square)
        return moves

    def winner(self, board):
        rnd.shuffle(WAYS_TO_WIN)
        for row in WAYS_TO_WIN:
            if board[row[0]] == board[row[1]] == board[row[2]] not in self.EMPTY:
                return board[row[0]]

    def human_move(self, move):
        legal = self.legal_moves(self.board)
        if move not in legal:
            self.ind -= 1
            return 10
        else:
            return move

    def computer_move(self):
        board = self.board[:]
        #BEST_MOVES = (4, 0, 2, 6, 8, 1, 3, 5, 7)
        for ind, move in enumerate(self.legal_moves(board)):
            board[move] = self.human
            if self.winner(board) == self.human:
                print(move)
                return move
            board[move] = str(ind + 1)
        for move in self.legal_moves(board):
            board[move] = self.human
            if self.winner(board) == self.human:
                print(move)
                return move

    def next_turn(self):
        if self.turn == self.X:
            return self.O
        else:
            return self.X

    def congrat_winner(self, the_winner):
        if the_winner == self.computer:
            return "Как я и предсказывал, победа в очередной раз осталась за мной"
        elif the_winner == self.human:
            return "О нет, неужели ты перехитрил меня"
        else:
            return "Ничья"

    async def main(self, event: Event, s=0):
        for i in range(s, 2):
            self.ind += 1
            if self.ind == 9:
                event.answer(self.congrat_winner(self.winner(self.board))).keyboard('Повторить', *keyb)
                self.upd()
                return event

            if not self.winner(self.board):
                if self.turn == self.human:
                    try:
                        txt = int(event.text) - 1
                    except:
                        self.ind -= 1
                        #return event.answer('Непохоже на цифру').keyboard(*keyb)
                        return event.answer('Непохоже на цифру.\n' + self.display_board())

                    move = self.human_move(txt)
                    if move == 10:
                        return event.answer('Смешной человек! Это поле уже занято.\n' + self.display_board())
                        #return event.answer("Смешной человек! Это поле уже занято.").keyboard(*keyb)
                    self.board[move] = self.human
                else:
                    move = self.computer_move()
                    if move == None:
                        event.answer(self.congrat_winner(self.winner(self.board))).keyboard('Повторить%b', *keyb)
                        self.upd()
                        return event
                    else:
                        self.board[move] = self.computer

                self.turn = self.next_turn()
                if not i:
                    if event.from_callback_button and event.support_callback:
                        await event.answer('Твой ход:\n' + self.display_board()).send()
                        #await event.answer('Твой ход:\n' + self.display_board()).send(nonkeyb=True)
                        #event.set_typing()
                        await asyncio.sleep(1)
                else:
                    #await event.answer(f'Я пожалуй выберу {move + 1}').send(nonkeyb=True)
                    #event.set_typing()
                    #await asyncio.sleep(1)
                    #await event.answer('Ход бота:\n' + self.display_board()).send(nonkeyb=True)
                    if event.from_callback_button and event.support_callback:
                        await event.answer('Ход бота:\n' + self.display_board()).send()
                        await asyncio.sleep(1)
                    if self.winner(self.board):
                        event.answer(self.congrat_winner(self.winner(self.board))).keyboard('Повторить', *keyb)
                        self.upd()
                        return event

                    else:
                        return event.answer('Твой ход?:\n' + self.display_board())
                        #return event.keyboard(*keyb).answer('Твой ход?')
            else:
                event.answer(self.congrat_winner(self.winner(self.board))).keyboard('Повторить%b', *keyb)
                self.upd()
                return event

    @middelware
    async def mainapp(self, event: Event):
        if event.check('повторить'):
            self.step = 0

        event.keyboard(*keyb_dig, tablet=3)

        if self.step == 0:
            self.upd()
            self.step = 1
            return event.answer("Хочешь оставить за собой первый ход? ").keyboard('Да%b', 'Нет%b')

        if self.step == 1:
            if event.check('да'):
                self.human = self.X
                self.computer = self.O
                self.step = 2
                return event.answer("Ну что ж, даю тебе фору, играй крестиками\nвыбери цифру от 1 до 9\n" +
                                    self.display_board())
            else:
                self.step = 2
                self.human = self.O
                self.computer = self.X
                #await event.answer('Твоя удаль тебя погубит... Буду начинать я.').send(nonkeyb=True)
                await event.answer('Твоя удаль тебя погубит... Буду начинать я.').send()
                await asyncio.sleep(1)
                event.answer('1')
                await self.main(event, s=1)
                return event

        if self.step == 2:
            await self.main(event)
            return event











