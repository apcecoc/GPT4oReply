import aiohttp
import asyncio
from telethon.tl.types import Message
from .. import loader, utils

__version__ = (1, 0, 3)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀ 
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2024
#           https://t.me/apcecoc
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://example.com/api_icon.png
# meta banner: https://example.com/api_banner.jpg
# meta developer: @apcecoc
# scope: hikka_only
# scope: hikka_min 1.2.10

@loader.tds
class GPT4oReplyMod(loader.Module):
    """Модуль для генерации ответов на сообщения с использованием GPT-4o API"""

    strings = {
        "name": "GPT4oReply",
        "error": "❌ <b>Не удалось сгенерировать ответ. Попробуйте позже.</b>",
        "invalid_message": "❌ <b>Пожалуйста, ответьте на действительное сообщение.</b>",
    }

    @loader.command(ru_doc="Сгенерировать ответ на сообщение")
    async def gpt4oreply(self, message: Message):
        """Генерировать ответ на указанное сообщение"""
        if not message.is_reply:
            await utils.answer(message, self.strings("invalid_message"))
            return

        reply_message = await message.get_reply_message()
        user_message = reply_message.raw_text

        if not user_message:
            await utils.answer(message, self.strings("invalid_message"))
            return

        api_url = "https://api.paxsenix.biz.id/ai/gpt4o"
        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Стиль написания максимально схожий и похожий на человека, чтобы не было заметно, "
                        "что ты нейросеть. Максимальная реалистичность. В меру можно использовать при необходимости "
                        "сленговые слова и нецензурную брань, но в меру. "
                        f"Придумай ответ на это сообщение: {user_message}"
                    ),
                }
            ]
        }

        async def animate_processing():
            dots = ""
            while not animation_done:
                dots = dots + "." if len(dots) < 4 else ""
                await utils.answer(message, dots)
                await asyncio.sleep(0.5)

        animation_done = False
        try:
            # Запускаем анимацию в отдельной задаче
            animation_task = asyncio.create_task(animate_processing())

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("ok", False):
                            generated_reply = data.get("message", "❌ <b>API не вернуло корректный ответ.</b>")
                            animation_done = True  # Завершаем анимацию
                            animation_task.cancel()
                            await utils.answer(message, generated_reply)
                        else:
                            animation_done = True
                            animation_task.cancel()
                            await utils.answer(message, self.strings("error"))
                    else:
                        animation_done = True
                        animation_task.cancel()
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            animation_done = True
            animation_task.cancel()
            await utils.answer(message, self.strings("error"))
            raise e
