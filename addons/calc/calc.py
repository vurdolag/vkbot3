# -*- coding: utf-8 -*-
import math
from Addon import Addon, middelware, addon_init
from untils import Event
from Template import str_back

keyb = ['Инфо%g', str_back]


# Глобальные переменные
class Data:
    __slots__ = ("Q", "W")

    def __init__(self):
        self.Q = []  # Operands
        self.W = []  # Operators


# Скелен для операций в калькуляторе
class Function:
    __slots__ = ("sign", "function", "priority", "arguments", "description", "display")

    def __init__(self, sign, function, description, arguments, priority, display=True):
        self.sign = sign
        self.function = function
        self.arguments = arguments
        self.priority = priority
        self.description = description

        self.display = display

    def clone_no_priority(self):
        return Function(self.sign, self.function, self.description, self.arguments, 0, False)

    def __call__(self, *args):
        return self.function(*args)

    def __repr__(self):
        return self.sign


def fix_error(x):
    """Исправляет погрешность при работе с PI(чуть-чуть)"""

    return round(x, 10)


def process(data, action):
    """Выполняет верхнюю операцию в стаке и возвращаем результат в стэк"""
    if not action.function:
        return True

    # Если для операции не хватает аргументов или значение не подходит - выдаём ошибку
    try:
        # Берём нужное кол-во аргументов для операции
        if action.arguments == 1:
            a = data.Q.pop()

            data.Q.append(action(a))

        elif action.arguments == 2:
            b = data.Q.pop()
            a = data.Q.pop()

            data.Q.append(action(a, b))

        return True

    except (TypeError, ValueError):
        return None


def do_bracket(data):
    """Выполняет верхнюю операцию в стэке и возвращаем результат в стэк"""
    action = FUNCTIONS["+"]

    while data.W and action.sign != "(":
        action = data.W.pop()

        if process(data, action) is None:
            return False

    return True


def is_float(s):
    """Выполняеn верхнюю операцию в стаке и возвращаем результат в стэк"""
    try:
        float(s)
    except ValueError:
        return False

    if "+" in s or "-" in s:
        return False

    return True


# Главая функция - проверяет аргументы, выводит помощь, если надо, или считает

def calc(args):

    if not args:
        return "Нечего считать! Пожалуйста, укажите выражение!"

    if args.lower() == "инфо":
        result = ""

        for k, v in FUNCTIONS.items():
            if not v.display:
                continue

            temp = "\"" + v.sign + "\" - " + v.description + "\n\n"

            result += temp

        return result

    # обворачиваем выражение в скобки, чтобы в результате получать только число
    exp = "(" + " ".join(args) + ")"

    # инициируем данные для решения
    data = Data()

    current_exp = ""
    prev_type = ""

    # проходим по выражению посимвольно
    for i in range(len(exp)):

        # пропускаем пробелы
        if exp[i] == " ":
            continue

        # pi - это число(3.14...)
        if current_exp == "pi":
            data.Q.append(math.pi)

            prev_type = ""
            current_exp = ""

        # проверяем, если у нас собралось число, а новый
        # символ - не число, значит мы получили число
        elif is_float(current_exp) and not is_float(exp[i]) and not exp[i] == ".":
            data.Q.append(float(current_exp))

            prev_type = "numb"
            current_exp = ""

        # добавляет новый символ в несобранный элемент
        current_exp += exp[i]

        # если мы собрали какое-то выражение
        # начинаем его обрабатывать
        if current_exp in FUNCTIONS:

            # если у нас идут несколько выражение подряд и это не
            # скобки - пропускаем вычисление выражения на данный момент
            # откладываем их напотом (симулируем скобки)
            if (prev_type and current_exp and
                        prev_type is not "numb" and
                        prev_type is not ")" and
                        current_exp not in "()"):

                # если то с чем мы разбираемся - это минус или плюс (унарные, т.е. не 0 - 1, а - 1),
                # то добавляем ноль, чтобы стэк мог их обработать и добавляем операцию в стэк
                # с нулевым приоритетом, чтобы сразу превратить их из 0 - 1 в - 1
                if current_exp in "-+":
                    data.Q.append(0)

                    data.W.append(FUNCTIONS[current_exp].clone_no_priority())

                # иначе - просто добавляем выражение в стэк
                else:
                    data.W.append(FUNCTIONS[current_exp])

                # выражение обработано, идём дальше
                prev_type = current_exp
                current_exp = ""
                continue

            # если мы дошли до закрывающе скобки - решаем её всю
            if current_exp == ")":
                if not do_bracket(data):
                    return "Ошибка в разборе выражения!"

            # если мы встретили выражение - проверяем
            # нужно ли решить всё перед ним.
            # за это отвечает приоритет.
            # чем он выше - тем позднее он будет вычислен
            else:
                while data.W and 0 <= data.W[-1].priority <= FUNCTIONS[current_exp].priority:
                    action = data.W.pop()
                    if process(data, action) is None:
                        return "Ошибка в разборе выражения!"

                # добавляем новое выражение после того, как обработали стэк
                data.W.append(FUNCTIONS[current_exp])

            # закончили с текушим выражением
            prev_type = current_exp
            current_exp = ""

    # если в резульате у нас не одно число - или в программе ошибка, ливо в выражении
    if len(data.Q) != 1:
        return "Ошибка в разборе выражения!"

    else:
        return f"Ответ: {data.Q.pop()}"


# Все операции у калькулятора
FUNCTIONS = []

# Functions(2 operands):
FUNCTIONS.append(Function(sign="+",
                          function=lambda x, y: x + y,
                          description="Сложение 5+2=7",
                          arguments=2,
                          priority=3))

FUNCTIONS.append(Function(sign="-",
                          function=lambda x, y: x - y,
                          description="Вычитание 5-2=3",
                          arguments=2,
                          priority=3))

FUNCTIONS.append(Function(sign="*",
                          function=lambda x, y: x * y,
                          description="Умножение 5*2=10",
                          arguments=2,
                          priority=2))

FUNCTIONS.append(Function(sign="/",
                          function=lambda x, y: x / y,
                          description="Деление 5/2=2.5",
                          arguments=2,
                          priority=2))

FUNCTIONS.append(Function(sign="mod",
                          function=lambda x, y: x % y,
                          description="Остаток деления 5 mod 2=1",
                          arguments=2,
                          priority=2))

FUNCTIONS.append(Function(sign="div",
                          function=lambda x, y: x // y,
                          description="Целочисленное деление 5 div 2=2",
                          arguments=2,
                          priority=2))

FUNCTIONS.append(Function(sign="log",
                          function=lambda x, y: math.log(y, x),
                          description="Логарифм 2 log 4=2",
                          arguments=2,
                          priority=2))

FUNCTIONS.append(Function(sign="^",
                          function=lambda x, y: x ** y,
                          description="Степень 3^2=9",
                          arguments=2,
                          priority=1))
#
# Functions 1 operand
FUNCTIONS.append(Function(sign="sin",
                          function=lambda x: fix_error(math.sin(x)),
                          description="Синус sin(pi/6)=0.5",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="cos",
                          function=lambda x: fix_error(math.cos(x)),
                          description="Косинус cos(pi/3) = 0.5",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="tg",
                          function=lambda x: fix_error(math.tan(x)),
                          description="Тангенс tg(pi/4)=1",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="ctg",
                          function=lambda x: fix_error(1 / math.tan(x)),
                          description="Котангенс ctg(pi/4)=1",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="arcsin",
                          function=lambda x: fix_error(math.asin(x)),
                          description="Арксинус arcsin 0.5=0.52",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="arccos",
                          function=lambda x: fix_error(math.acos(x)),
                          description="Арккосинус arccos 0.5=1.04",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="arctg",
                          function=lambda x: fix_error(math.atan(x)),
                          description="Арктангенс arctg 0.5=0.46",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="arcctg",
                          function=lambda x: fix_error(math.pi / 2 - math.atan(x)),
                          description="Арккотангенс arcctg 0.5=1.10",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="sqrt",
                          function=lambda x: math.sqrt(x),
                          description="Корень sqrt 9=3",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="abs",
                          function=lambda x: math.fabs(x),
                          description="Модуль abs -9=9",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function(sign="!",
                          function=lambda x: math.factorial(x),
                          description="Факториал !4 = 24",
                          arguments=1,
                          priority=1))

FUNCTIONS.append(Function("(", None, "Скобка для приоритета", 0, -1))
FUNCTIONS.append(Function(")", None, "Скобка для приоритета", 0, 50))

FUNCTIONS = {func.sign: func for func in FUNCTIONS}

NotWork = 0
Start = 1


_msg1 = ('{}, я калькулятор, могу посчитать почти что угодно!\n\n'
         'Пример: 5!-(2+8)/2*4^3\n\nЧтобы узнать подробнее о командах - ИНФО')


@addon_init(['!калькулятор', '!калк'], '🔢', True, 3)
class Calcs(Addon):
    __slots__ = ()

    @middelware
    async def mainapp(self, event: Event):
        if self.isstep(NotWork, Start):
            return event.answer(_msg1, self.username).keyboard(*keyb)

        if self.isstep(Start):
            result = calc(event.text)
            return event.answer(result if not result.endswith('.0') else result[:-2]).keyboard(*keyb)






























