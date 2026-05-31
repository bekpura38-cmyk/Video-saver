"""
bot.py — Asosiy fayl. Barcha handlerlar shu yerda.
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from typing import Callable, Awaitable, Any
from aiogram.types import TelegramObject

import database as db
from downloader import download_video, is_valid_url, QUALITY_LABELS
from i18n import t, PLATFORM_EMOJI
from keyboards import (
    main_reply_kb, cancel_reply_kb,
    lang_inline_kb, quality_inline_kb, settings_inline_kb,
    admin_main_kb, admin_users_nav_kb, admin_user_action_kb,
)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class DL(StatesGroup):
    waiting_url = State()
    choosing_quality = State()

class Broadcast(StatesGroup):
    waiting_text = State()


def user_lang(user_id: int) -> str:
    u = db.get_user(user_id)
    return u["lang"] if u else "uz"

def user_quality(user_id: int) -> str:
    u = db.get_user(user_id)
    return u["quality"] if u else "720"

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def short_url(url: str) -> str:
    return url[:50] + "…" if len(url) > 50 else url


class RegisterMiddleware:
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: dict[str, Any],
    ) -> Any:
        uid = event.from_user.id
        db.upsert_user(uid, event.from_user.username, event.from_user.full_name)
        if db.is_banned(uid) and not is_admin(uid):
            lang = user_lang(uid)
            await event.answer(t(lang, "banned"))
            return
        return await handler(event, data)


@dp.message(Command("start"))
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    lang = user_lang(msg.from_user.id)
    name = msg.from_user.first_name or "Foydalanuvchi"
    await msg.answer(t(lang, "welcome", name=name), reply_markup=main_reply_kb(lang))

@dp.message(Command("help"))
async def cmd_help(msg: types.Message):
    lang = user_lang(msg.from_user.id)
    await msg.answer(t(lang, "help"), parse_mode="Markdown", reply_markup=main_reply_kb(lang))

@dp.message(Command("settings"))
async def cmd_settings(msg: types.Message):
    lang = user_lang(msg.from_user.id)
    await msg.answer(t(lang, "settings_title"), parse_mode="Markdown", reply_markup=settings_inline_kb(lang))

@dp.message(Command("mystats"))
async def cmd_mystats(msg: types.Message):
    lang = user_lang(msg.from_user.id)
    stats = db.get_user_stats(msg.from_user.id)
    if stats["total"] == 0:
