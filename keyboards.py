"""
keyboards.py — Barcha klaviatura va tugmalar
"""
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from i18n import t


# ─── REPLY KEYBOARD (pastki tugmalar) ────────────────────────────
def main_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_download"))],
            [
                KeyboardButton(text=t(lang, "btn_stats")),
                KeyboardButton(text=t(lang, "btn_settings")),
            ],
            [KeyboardButton(text=t(lang, "btn_help"))],
        ],
        resize_keyboard=True,
        input_field_placeholder="🔗 Havola yuboring...",
    )


def cancel_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "btn_main"))]],
        resize_keyboard=True,
    )


# ─── INLINE: TIL TANLASH ─────────────────────────────────────────
def lang_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek",  callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ],
    ])


# ─── INLINE: SIFAT TANLASH ───────────────────────────────────────
def quality_inline_kb(lang: str, prefix: str = "qset") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t(lang, "q_144"),   callback_data=f"{prefix}_144")],
        [InlineKeyboardButton(text=t(lang, "q_360"),   callback_data=f"{prefix}_360")],
        [InlineKeyboardButton(text=t(lang, "q_480"),   callback_data=f"{prefix}_480")],
        [InlineKeyboardButton(text=t(lang, "q_720"),   callback_data=f"{prefix}_720")],
        [InlineKeyboardButton(text=t(lang, "q_1080"),  callback_data=f"{prefix}_1080")],
        [InlineKeyboardButton(text=t(lang, "q_best"),  callback_data=f"{prefix}_best")],
        [InlineKeyboardButton(text=t(lang, "q_audio"), callback_data=f"{prefix}_audio")],
    ]
    if prefix == "qset":
        rows.append([
            InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="settings_main")
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── INLINE: SOZLAMALAR MENYUSI ──────────────────────────────────
def settings_inline_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_lang"), callback_data="settings_lang")],
    ])


# ─── INLINE: ADMIN PANEL ─────────────────────────────────────────
def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Umumiy statistika", callback_data="adm_stats")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar",  callback_data="adm_users_0")],
        [InlineKeyboardButton(text="📢 Xabar yuborish",    callback_data="adm_broadcast")],
    ])


def admin_users_nav_kb(offset: int, total: int, page_size: int = 10) -> InlineKeyboardMarkup:
    buttons = []
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"adm_users_{offset - page_size}"))
    if offset + page_size < total:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"adm_users_{offset + page_size}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_user_action_kb(target_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    ban_text = "✅ Blokdan chiqarish" if is_banned else "🚫 Bloklash"
    ban_data = f"adm_unban_{target_id}" if is_banned else f"adm_ban_{target_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ban_text, callback_data=ban_data)],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_users_0")],
    ])
