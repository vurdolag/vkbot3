# -*- coding: utf-8 -*-
import qrcode
from Addon import Addon, middelware, addon_init
from Template import str_back, str_error
import io

NotWork = 0
Start = 1


@addon_init(['!QRCODE', '!КОД'], '💠', True, 3)
class Qr(Addon):
    __slots__ = ()

    async def qrcode_gen(self, event):
        qr = qrcode.QRCode()
        qr.add_data(event.text)
        qr.make()

        img = qr.make_image(fill_color="black", back_color="white")
        byte_io = io.BytesIO()
        img.save(byte_io, 'PNG')
        await event.uploads(byte_io.getvalue())
        byte_io.close()
        return event

    @middelware
    async def mainapp(self, event):
        if self.isstep(NotWork, Start):
            return event.answer(f'{self.username}, пришли текст или ссылку, и я сгенерирую QRcode.\n\n'
                                f'Например, такой:'
                                ).keyboard(str_back).attachment('photo-168691465_457243345')

        if self.isstep(Start):
            if not event.text:
                return event.answer(f'Я могу сделать QRcode только из текста... пришли сообщение,'
                                    f' которое содержит текст или ссылку').keyboard(str_back)

            try:
                await self.qrcode_gen(event)
                return event.answer('Вот:').keyboard(str_back)
            except:
                return event.answer(str_error).keyboard(str_back)










