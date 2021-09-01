# -*- coding: utf-8 -*-
import time
import ujson as json
from untils import req
import recompile as rec
from Addon import Addon, middelware, addon_init
from Template import str_back, str_error

# сервис для определения погоды: http://openweathermap.org/api


NotWork = 0
Start = 1


@addon_init(['!ПОГОДА', 'ПГД'], '🌦', True, 3)
class Weather(Addon):
    __slots__ = ()

    async def get_weather(self, city, days=0):
        code = "51efafdf1655fead325d49e4b46ba03e"
        code = 'fe198ba65970ed3877578f728f33e0f9'

        #'https://api.openweathermap.org/data/2.5/forecast/daily?q=%D0%B4%D1%83%D0%B1%D0%BD%D0%B0&lang=ru&appid=51efafdf1655fead325d49e4b46ba03e&cnt=9'

        city = city.capitalize()
        days = int(days)

        if days == 0:
            url = f"http://api.openweathermap.org/data/2.5/weather?APPID={code}&lang=ru&q={city}"
        else:
            url = f"http://api.openweathermap.org/data/2.5/forecast/daily?APPID={code}&lang=ru&q={city}&cnt={days + 1}"

        response = await req.get(url, timeout=30)
        response = json.loads(response.decode('utf-8'))

        if "cod" in response and response["cod"] == '404':
            return "Город не найден!"

        if days != 0:
            answer = f"{city}. Погода.\n\n"

            for i in range(1, len(response["list"])):
                day = response["list"][i]
                temperature = day["temp"]["day"] - 273
                humidity = day["humidity"]
                description = day["weather"][0]["description"]
                wind = day["speed"]
                cloud = day["clouds"]
                date = time.strftime("%Y-%m-%d", time.gmtime(day["dt"]))

                answer += (f'{date}:\n'
                                   f'{description[0].upper()}{description[1:]}\n'
                                   f'Температура: {round(temperature, 2)} °C\n'
                                   f'Влажность: {humidity} %\n'
                                   f'Облачность: {cloud} %\n'
                                   f'Скорость ветра: {wind} м/с\n\n')

            return answer

        else:
            result = response

            description = result["weather"][0]["description"]
            temperature = result["main"]["temp"] - 273
            humidity = result["main"]["humidity"]
            wind = result["wind"]["speed"]
            cloud = result["clouds"]["all"]

            answer = (f'{city}. Текущая погода.\n'
                              f'{description[0].upper()}{description[1:]}\n'
                              f'Температура: {round(temperature, 2)} °C\n'
                              f'Влажность: {humidity} %\n'
                              f'Облачность: {cloud} %\n'
                              f'Скорость ветра: {wind} м/с')
            return answer

    async def get(self, event):
        try:
            days = int(rec.d.sub('', event.text).strip())
            city = rec.n_ruw.sub('', event.text).strip()

        except:
            days = 0
            city = event.text

        if days > 14:
            return event.answer('Максимум на 14 дней').keyboard(str_back)

        try:
            return event.answer(await self.get_weather(city, days)).keyboard(str_back)

        except Exception as ex:
            print(ex)
            return event.answer(str_error).keyboard(str_back)

    @middelware
    async def mainapp(self, event):
        if event.from_comment:
            event.text = ' '.join(event.text.split()[1:])
            return await self.get(event)

        if not event.text:
            return event.answer('Я могу выполнить команду, только если написать буквами название города...'
                                ).keyboard()

        if self.isstep(NotWork, Start):
            return event.answer(f'{self.username}, чтобы узнать погоду на сегодня, '
                                f'напиши название города.\n\n'
                                'Можно узнать погоду на несколько дней, для этого напиши '
                                'после города количество дней.\n\n'
                                'Пример:\nМосква 7'
                                ).keyboard(str_back)

        if self.isstep(Start):
            await self.get(event)
            return event.keyboard(str_back)









