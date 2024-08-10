from io import BufferedWriter, BytesIO
import re
import asyncio
import sys
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from tiktok_downloader import VideoInfo, tikwm, ttdownloader, tikdown, mdown, snaptik, Tikmate
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import config


dp = Dispatcher()


WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = 80

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = config.WEBHOOK_SECRET
BASE_WEBHOOK_URL = config.BASE_WEBHOOK_URL


def download(link: str):
    download_funcs = [
        VideoInfo.service,
        tikwm,
        ttdownloader,
        tikdown,
        mdown,
        snaptik,
        Tikmate
    ]

    for download_func in download_funcs:
        try:
            d = download_func(link)
            if d:
                data = d[0].download()
                if data is not None:
                    return data
        except Exception:
            pass


@dp.message()
async def message_handler(message: types.Message):
    if message.text is None:
        await message.answer('This is not a text message')
        return

    tiktok_link = re.search(r'https://vt.tiktok.com/.+/', message.text)
    if tiktok_link is None:
        await message.answer('This is not a TikTok link')
        return

    await message.answer('Downloading...')

    loop = asyncio.get_event_loop()
    data: BytesIO | BufferedWriter | None = await loop.run_in_executor(None, download, tiktok_link.group(0))
    if data is None:
        await message.answer('Failed to download the video')
        return

    filename = 'video.mp4'

    if isinstance(data, bytes):
        await message.answer_video(types.BufferedInputFile(data, filename=filename))
    elif isinstance(data, BytesIO):
        await message.answer_video(types.BufferedInputFile(data.getvalue(), filename=filename))
    elif isinstance(data, BufferedWriter):
        temp = BytesIO()
        data.write(temp.getbuffer())
        await message.answer_video(types.BufferedInputFile(temp.getvalue(), filename=filename))


def main() -> None:
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
