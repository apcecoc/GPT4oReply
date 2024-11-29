import aiohttp
from markdown2 import markdown
from telethon.tl.types import Message
from .. import loader, utils

__version__ = (1, 0, 2)

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
    """Module to generate replies to messages using GPT-4o API"""

    strings = {
        "name": "GPT4oReply",
        "processing": "🤖 <b>Generating a response...</b>",
        "error": "❌ <b>Failed to generate a response. Try again later.</b>",
        "invalid_message": "❌ <b>Please reply to a valid message.</b>",
    }

    def _convert_markdown_to_html(self, text: str) -> str:
        """
        Converts Markdown to HTML using markdown2 library.
        """
        return markdown(text)

    @loader.command(ru_doc="Сгенерировать ответ на сообщение")
    async def gpt4oreply(self, message: Message):
        """Generate a reply to the referenced message"""
        if not message.is_reply:
            await utils.answer(message, self.strings("invalid_message"))
            return

        reply_message = await message.get_reply_message()
        user_message = reply_message.raw_text

        if not user_message:
            await utils.answer(message, self.strings("invalid_message"))
            return

        await utils.answer(message, self.strings("processing"))

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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("ok", False):
                            generated_reply = data.get("message", "❌ <b>API did not return a valid response.</b>")

                            # Convert Markdown to HTML
                            formatted_reply = self._convert_markdown_to_html(generated_reply)

                            await utils.answer(message, formatted_reply)
                        else:
                            await utils.answer(message, self.strings("error"))
                    else:
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            await utils.answer(message, self.strings("error"))
            raise e
