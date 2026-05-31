import asyncio
import logging
import os
from typing import Callable, Awaitable, Any

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject

import database as db
from downloader import download_video, is_valid_url, QUALITY_LABELS, detect_platform
from i18n import t, PLATFORM_EMOJI
from keyboards import (
    main_reply_kb, cancel_reply_kb,
    lang_inline_kb, quality_inline_kb, settings_inline_kb,
    admin_main_kb, admin_users_nav_kb, admin_user_action_kb,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

YOUTUBE_PLATFORMS = {"youtube"}
AUTO_PLATFORMS = {"instagram", "tiktok", "other"}


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
    return url[:45] + "..." if len(url) > 45 else url


class RegisterMiddleware:
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: types.Message,
        data: dict,
    ) -> Any:
        uid = event.from_user.id
        db.upsert_user(uid, event.from_user.username, event.from_user.full_name)
        if db.is_banned(uid) and not is_admin(uid):
            await event.answer(t(user_lang(uid), "banned"))
            return
        return await handler(event, data)


async def do_download_and_send(
    send_to: types.Message | types.CallbackQuery,
    url: str,
    quality: str,
    lang: str,
    uid: int,
    status_msg: types.Message,
):
    label = QUALITY_LABELS.get(quality, quality)
    await status_msg.edit_text(t(lang, "downloading", q=label), parse_mode="Markdown")

    result = await download_video(url, quality)

    if not result.success:
        if result.error == "private":
            await status_msg.edit_text(t(lang, "error_private"))
        elif result.error == "size":
            await status_msg.edit_text(t(lang, "error_size"))
        else:
            await status_msg.edit_text(t(lang, "error_download"))
        db.log_download(uid, url, quality, result.error)
        return

    try:
        caption = t(lang, "done")
        if result.is_audio:
            with open(result.path, "rb") as f:
                await status_msg.answer_audio(f, caption=caption, parse_mode="Markdown")
        else:
            with open(result.path, "rb") as f:
                await status_msg.answer_video(f, caption=caption, parse_mode="Markdown")
        await status_msg.delete()
        db.log_download(uid, url, quality, "ok", result.file_size)
    except Exception as e:
        log.error("Send error: %s", e)
        await status_msg.edit_text(t(lang, "error_size"))
        db.log_download(uid, url, quality, "error")
    finally:
        if result.path and os.path.exists(result.path):
            try:
                os.remove(result.path)
            except Exception:
                pass


@dp.message(Command("start"))
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    lang = user_lang(msg.from_user.id)
    name = msg.from_user.first_name or "Foydalanuvchi"
    bot_info = await bot.get_me()
    add_group_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="➕ Guruhga qo'shish",
            url=f"https://t.me/{bot_info.username}?startgroup=start"
        )]
    ])
    await msg.answer(t(lang, "welcome", name=name), reply_markup=add_group_kb)
    await msg.answer(t(lang, "btn_main"), reply_markup=main_reply_kb(lang))


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
        await msg.answer(t(lang, "mystats_empty"))
        return
    platform_rows = "\n".join(
        f"  {PLATFORM_EMOJI.get(r['platform'], '🌐')} -- {r['cnt']} ta"
        for r in stats["by_platform"]
    )
    text = (
        f"{t(lang, 'mystats_title')}\n\n"
        f"{t(lang, 'mystats_total', n=stats['total'])}\n\n"
        f"{t(lang, 'mystats_platform', rows=platform_rows)}"
    )
    await msg.answer(text, parse_mode="Markdown")


@dp.message(Command("admin"))
async def cmd_admin(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return
    await msg.answer("🔐 *Admin Panel*", parse_mode="Markdown", reply_markup=admin_main_kb())


@dp.message(Command("cancel"))
async def cmd_cancel(msg: types.Message, state: FSMContext):
    await state.clear()
    lang = user_lang(msg.from_user.id)
    await msg.answer("Bekor qilindi.", reply_markup=main_reply_kb(lang))


@dp.message(F.text.in_(["📥 Video yuklab olish", "📥 Скачать видео", "📥 Download video"]))
async def btn_download(msg: types.Message, state: FSMContext):
    lang = user_lang(msg.from_user.id)
    await state.set_state(DL.waiting_url)
    await msg.answer(t(lang, "send_url"), reply_markup=cancel_reply_kb(lang))


@dp.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings"]))
async def btn_settings(msg: types.Message):
    lang = user_lang(msg.from_user.id)
    await msg.answer(t(lang, "settings_title"), parse_mode="Markdown", reply_markup=settings_inline_kb(lang))


@dp.message(F.text.in_(["📊 Statistika", "📊 Статистика", "📊 Statistics"]))
async def btn_stats(msg: types.Message):
    await cmd_mystats(msg)


@dp.message(F.text.in_(["❓ Yordam", "❓ Помощь", "❓ Help"]))
async def btn_help(msg: types.Message):
    await cmd_help(msg)


@dp.message(F.text.in_(["🏠 Bosh sahifa", "🏠 Главное меню", "🏠 Main menu"]))
async def btn_main(msg: types.Message, state: FSMContext):
    await state.clear()
    await cmd_start(msg, state)


async def process_url(msg: types.Message, state: FSMContext, url: str):
    lang = user_lang(msg.from_user.id)
    uid = msg.from_user.id
    platform = detect_platform(url)

    if platform in AUTO_PLATFORMS:
        # Instagram / TikTok — sifat tanlamasdan yukla
        status_msg = await msg.answer(t(lang, "fetching"))
        await do_download_and_send(msg, url, "best", lang, uid, status_msg)
        await state.clear()
    else:
        # YouTube — sifat tanlash
        await state.update_data(pending_url=url)
        await state.set_state(DL.choosing_quality)
        await msg.answer(
            t(lang, "choose_q_for_video", url=short_url(url)),
            parse_mode="Markdown",
            reply_markup=quality_inline_kb(lang, "qdl"),
        )


@dp.message(DL.waiting_url)
async def handle_url_input(msg: types.Message, state: FSMContext):
    lang = user_lang(msg.from_user.id)
    url = (msg.text or "").strip()
    if not is_valid_url(url):
        await msg.answer(t(lang, "error_url"), parse_mode="Markdown")
        return
    await process_url(msg, state, url)


@dp.message(F.text.regexp(r"https?://"))
async def handle_direct_url(msg: types.Message, state: FSMContext):
    url = msg.text.strip()
    await process_url(msg, state, url)


@dp.message()
async def handle_unknown(msg: types.Message):
    lang = user_lang(msg.from_user.id)
    await msg.answer(t(lang, "unknown_cmd"))


@dp.callback_query(F.data.startswith("qdl_"))
async def cb_quality_download(cb: types.CallbackQuery, state: FSMContext):
    quality = cb.data.removeprefix("qdl_")
    data = await state.get_data()
    url = data.get("pending_url")
    uid = cb.from_user.id
    lang = user_lang(uid)
    if not url:
        await cb.answer("URL topilmadi")
        return
    await state.clear()
    await cb.answer()
    await do_download_and_send(cb, url, quality, lang, uid, cb.message)


@dp.callback_query(F.data == "settings_main")
async def cb_settings_main(cb: types.CallbackQuery):
    lang = user_lang(cb.from_user.id)
    await cb.message.edit_text(t(lang, "settings_title"), parse_mode="Markdown", reply_markup=settings_inline_kb(lang))
    await cb.answer()


@dp.callback_query(F.data == "settings_lang")
async def cb_settings_lang(cb: types.CallbackQuery):
    lang = user_lang(cb.from_user.id)
    await cb.message.edit_text(t(lang, "choose_lang"), reply_markup=lang_inline_kb())
    await cb.answer()


@dp.callback_query(F.data == "settings_quality")
async def cb_settings_quality(cb: types.CallbackQuery):
    lang = user_lang(cb.from_user.id)
    await cb.message.edit_text(t(lang, "choose_quality"), reply_markup=quality_inline_kb(lang, "qset"))
    await cb.answer()


@dp.callback_query(F.data.startswith("lang_"))
async def cb_lang(cb: types.CallbackQuery):
    code = cb.data.split("_")[1]
    db.set_user_lang(cb.from_user.id, code)
    await cb.message.edit_text(t(code, "lang_saved"))
    await cb.answer()
    await bot.send_message(cb.from_user.id, t(code, "btn_main"), reply_markup=main_reply_kb(code))


@dp.callback_query(F.data.startswith("qset_"))
async def cb_quality_set(cb: types.CallbackQuery):
    quality = cb.data.removeprefix("qset_")
    db.set_user_quality(cb.from_user.id, quality)
    lang = user_lang(cb.from_user.id)
    label = QUALITY_LABELS.get(quality, quality)
    await cb.message.edit_text(t(lang, "quality_saved", q=label), parse_mode="Markdown")
    await cb.answer()


@dp.callback_query(F.data == "adm_main")
async def adm_main(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    await cb.message.edit_text("🔐 *Admin Panel*", parse_mode="Markdown", reply_markup=admin_main_kb())
    await cb.answer()


@dp.callback_query(F.data == "adm_stats")
async def adm_stats(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    s = db.get_global_stats()
    platform_rows = "\n".join(
        f"  {PLATFORM_EMOJI.get(r['platform'], '🌐')} -- {r['cnt']} ta"
        for r in s["by_platform"]
    ) or "  --"
    quality_rows = "\n".join(
        f"  {QUALITY_LABELS.get(r['quality'], r['quality'])} -- {r['cnt']} ta"
        for r in s["by_quality"]
    ) or "  --"
    text = (
        "📊 *Umumiy statistika*\n\n"
        f"👤 Jami: *{s['total_users']}*\n"
        f"🟢 Bugun faol: *{s['active_today']}*\n\n"
        f"📥 Yuklanmalar: *{s['total_downloads']}*\n"
        f"❌ Xatolar: *{s['errors']}*\n"
        f"💾 Hajm: *{s['total_size_mb']} MB*\n\n"
        f"📱 Platformalar:\n{platform_rows}\n\n"
        f"Sifatlar:\n{quality_rows}"
    )
    back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Orqaga", callback_data="adm_main")]
    ])
    await cb.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb)
    await cb.answer()


@dp.callback_query(F.data.startswith("adm_users_"))
async def adm_users(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    offset = int(cb.data.removeprefix("adm_users_"))
    page_size = 10
    users = db.get_all_users(limit=page_size, offset=offset)
    total = db.get_global_stats()["total_users"]
    if not users:
        await cb.answer("Foydalanuvchi yoq")
        return
    lines = ["👥 *Foydalanuvchilar*\n"]
    for u in users:
        ban_icon = "🚫" if u["is_banned"] else "✅"
        name = u["full_name"] or "--"
        uname = f"@{u['username']}" if u["username"] else "--"
        lines.append(
            f"{ban_icon} `{u['user_id']}` -- {name} ({uname})\n"
            f"   📥 {u['dl_count']} ta | 📅 {u['joined_at'][:10]}"
        )
    await cb.message.edit_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
        reply_markup=admin_users_nav_kb(offset, total, page_size)
    )
    await cb.answer()


@dp.callback_query(F.data.startswith("adm_ban_"))
async def adm_ban(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    target = int(cb.data.removeprefix("adm_ban_"))
    db.ban_user(target, True)
    await cb.answer(f"Bloklandi: {target}")
    await cb.message.edit_text(
        f"🚫 `{target}` bloklandi.",
        parse_mode="Markdown",
        reply_markup=admin_user_action_kb(target, True)
    )


@dp.callback_query(F.data.startswith("adm_unban_"))
async def adm_unban(cb: types.CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    target = int(cb.data.removeprefix("adm_unban_"))
    db.ban_user(target, False)
    await cb.answer(f"Blokdan chiqarildi: {target}")
    await cb.message.edit_text(
        f"✅ `{target}` blokdan chiqarildi.",
        parse_mode="Markdown",
        reply_markup=admin_user_action_kb(target, False)
    )


@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast_start(cb: types.CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    await state.set_state(Broadcast.waiting_text)
    await cb.message.answer("📢 Xabarni kiriting. Bekor qilish: /cancel")
    await cb.answer()


@dp.message(Broadcast.waiting_text)
async def adm_broadcast_send(msg: types.Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    await state.clear()
    user_ids = db.get_active_user_ids()
    sent, failed = 0, 0
    status_msg = await msg.answer(f"📢 Yuborilmoqda... 0/{len(user_ids)}")
    for i, uid in enumerate(user_ids):
        try:
            await bot.send_message(uid, msg.text)
            sent += 1
        except Exception:
            failed += 1
        if (i + 1) % 20 == 0:
            try:
                await status_msg.edit_text(f"📢 {i+1}/{len(user_ids)}")
            except Exception:
                pass
        await asyncio.sleep(0.05)
    await status_msg.edit_text(f"Tugadi! Yuborildi: {sent} | Xato: {failed}")


async def main():
    db.init_db()
    dp.message.middleware(RegisterMiddleware())
    log.info("Bot ishga tushdi | ADMIN_IDS: %s", ADMIN_IDS)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
