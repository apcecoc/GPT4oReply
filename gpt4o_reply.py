import aiohttp
import asyncio
from telethon.tl.types import Message
from .. import loader, utils

__version__ = (1, 0, 4)

#        █████  ██████   ██████ ███████  ██████  ██████   ██████ 
#       ██   ██ ██   ██ ██      ██      ██      ██    ██ ██      
#       ███████ ██████  ██      █████   ██      ██    ██ ██      
#       ██   ██ ██      ██      ██      ██      ██    ██ ██      
#       ██   ██ ██       ██████ ███████  ██████  ██████   ██████

#              © Copyright 2025
#           https://t.me/apcecoc
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apcecoc
# scope: hikka_only
# scope: hikka_min 1.2.10

@loader.tds
class GPT4oReplyMod(loader.Module):
    """Модуль для генерации ответов на сообщения с использованием GPT-4o API"""

    strings = {
        "name": "GPT4oReply",
        "error": "❌ <b>Не удалось сгенерировать ответ: {error}</b>",
        "invalid_message": "❌ <b>Пожалуйста, ответьте на действительное сообщение.</b>",
        "processing": "⏳ <b>Генерирую ответ</b>{dots}",
    }

    strings_ru = {
        "error": "❌ <b>Не удалось сгенерировать ответ: {error}</b>",
        "invalid_message": "❌ <b>Пожалуйста, ответьте на действительное сообщение.</b>",
        "processing": "⏳ <b>Генерирую ответ</b>{dots}",
        "_cls_doc": "Модуль для генерации ответов на сообщения с использованием GPT-4o API",
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

        api_url = "https://api.paxsenix.biz.id/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_API_KEY",
        }
        payload = {
            "model": "gpt-4o",
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
                await utils.answer(message, self.strings("processing").format(dots=dots))
                await asyncio.sleep(0.5)

        animation_done = False
        try:
            animation_task = asyncio.create_task(animate_processing())

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if not data.get("ok", False):
                            animation_done = True
                            animation_task.cancel()
                            await utils.answer(
                                message,
                                self.strings("error").format(error=data.get("message", "Unknown error")),
                            )
                            return

                        generated_reply = data["choices"][0]["message"]["content"]

                        animation_done = True
                        animation_task.cancel()
                        await utils.answer(message, generated_reply)
                    elif resp.status == 400:
                        data = await resp.json()
                        animation_done = True
                        animation_task.cancel()
                        await utils.answer(
                            message,
                            self.strings("error").format(error=data.get("message", "Bad request")),
                        )
                    elif resp.status == 500:
                        data = await resp.json()
                        animation_done = True
                        animation_task.cancel()
                        await utils.answer(
                            message,
                            self.strings("error").format(error=data.get("message", "Server error")),
                        )
                    else:
                        animation_done = True
                        animation_task.cancel()
                        await utils.answer(
                            message,
                            self.strings("error").format(error=f"HTTP {resp.status}"),
                        )
        except Exception as e:
            animation_done = True
            animation_task.cancel()
            await utils.answer(
                message,
                self.strings("error").format(error=str(e)),
            )