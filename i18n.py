"""
i18n.py — Barcha tillar uchun tarjimalar
"""

TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        # Asosiy
        "welcome": (
            "👋 Assalomu alaykum, {name}!\n\n"
            "📥 TikTok yoki Instagram havolasini yuboring.\n"
            "Men siz uchun videoni yuklab beraman! 🚀\n\n"
            "📌 Quyidagi tugmalardan foydalaning:\n\n"
            "➕ Bot guruhlarda ham ishlaydi, guruhda ham ishlatmoqchi bo'lsangiz tugmani bosing👇"
        ),
        "help": (
            "📖 *Yordam*\n\n"
            "▶️ *Video yuklab olish:*\n"
            "Havola yuboring → sifat tanlang → tayyor!\n\n"
            "✅ *Qo'llab-quvvatlanadi:*\n"
            "• YouTube (to'liq va Shorts)\n"
            "• TikTok\n"
            "• Instagram (Reels, post)\n\n"
            "⚙️ *Buyruqlar:*\n"
            "/start — Bosh menyu\n"
            "/settings — Sozlamalar\n"
            "/mystats — Mening statistikam\n"
            "/help — Yordam\n\n"
            "💡 Muammo bo'lsa, havolani tekshirib qayta yuboring."
        ),
        "settings_title": "⚙️ *Sozlamalar*",
        "choose_lang": "🌐 Tilni tanlang:",
        "choose_quality": "📊 Standart sifatni tanlang:",
        "lang_saved": "✅ Til saqlandi: O'zbek 🇺🇿",
        "quality_saved": "✅ Standart sifat: *{q}*",
        "send_url": "🔗 Havola yuboring:",
        "fetching": "🔍 Video ma'lumotlari olinmoqda...",
        "downloading": "⏳ Yuklanmoqda...\n\n📊 Sifat: *{q}*",
        "choose_q_for_video": "📊 *Sifatni tanlang:*\n\n🔗 {url}",
        "done": "✅ *Tayyor!*",
        "banned": "🚫 Siz bloklangansiz. Admin bilan bog'laning.",
        "error_url": "❌ To'g'ri havola yuboring!\n_(http yoki https bilan boshlanishi kerak)_",
        "error_download": "❌ Yuklab bo'lmadi.\nHavola noto'g'ri yoki video yopiq bo'lishi mumkin.",
        "error_private": "❌ Bu video yopiq yoki Instagram login talab qiladi.\nFaqat ochiq (public) videolarni yuklab olish mumkin.",
        "error_size": "❌ Video 50MB dan katta.\nPastroq sifat tanlang.",
        "error_generic": "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
        "unknown_cmd": "❗ Noma'lum buyruq kiritildi. Havola kiritishingiz mumkin.",
        "unsupported": "❌ Faqat TikTok va Instagram havolalari qo'llab-quvvatlanadi!\n\n🎵 tiktok.com\n📸 instagram.com",
        "quality_reduced": "✅ Video {q} sifatda yuklandi (hajm katta edi).",
        # Statistika
        "mystats_title": "📊 *Mening statistikam*",
        "mystats_total": "📥 Jami yuklab olindi: *{n}* ta video",
        "mystats_platform": "📱 Platformalar:\n{rows}",
        "mystats_empty": "Hali birorta video yuklab olmadingiz.",
        # Tugmalar
        "btn_download": "📥 Video yuklab olish",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_stats": "📊 Statistika",
        "btn_help": "❓ Yordam",
        "btn_lang": "🌐 Til",
        "btn_quality": "📊 Sifat",
        "btn_back": "⬅️ Orqaga",
        "btn_main": "🏠 Bosh sahifa",
        # Sifatlar
        "q_144": "📱 144p — Juda engil",
        "q_360": "📱 360p — Engil",
        "q_480": "💻 480p — O'rtacha",
        "q_720": "🖥️ 720p — HD",
        "q_1080": "📺 1080p — Full HD",
        "q_best": "⚡ Eng yaxshi",
        "q_audio": "🎵 Faqat audio (MP3)",
    },
    "ru": {
        "welcome": (
            "👋 Привет, {name}!\n\n"
            "📥 Отправь ссылку на TikTok или Instagram.\n"
            "Я скачаю видео для тебя! 🚀\n\n"
            "📌 Используй кнопки ниже:\n\n"
            "➕ Бот работает и в группах, нажми кнопку чтобы добавить в группу👇"
        ),
        "help": (
            "📖 *Помощь*\n\n"
            "▶️ *Скачать видео:*\n"
            "Отправь ссылку → выбери качество → готово!\n\n"
            "✅ *Поддерживается:*\n"
            "• YouTube (видео и Shorts)\n"
            "• TikTok\n"
            "• Instagram (Reels, пост)\n\n"
            "⚙️ *Команды:*\n"
            "/start — Главное меню\n"
            "/settings — Настройки\n"
            "/mystats — Моя статистика\n"
            "/help — Помощь\n\n"
            "💡 При ошибке проверь ссылку и попробуй снова."
        ),
        "settings_title": "⚙️ *Настройки*",
        "choose_lang": "🌐 Выберите язык:",
        "choose_quality": "📊 Выберите качество по умолчанию:",
        "lang_saved": "✅ Язык сохранён: Русский 🇷🇺",
        "quality_saved": "✅ Качество по умолчанию: *{q}*",
        "send_url": "🔗 Отправьте ссылку:",
        "fetching": "🔍 Получаю информацию о видео...",
        "downloading": "⏳ Загружаю...\n\n📊 Качество: *{q}*",
        "choose_q_for_video": "📊 *Выберите качество:*\n\n🔗 {url}",
        "done": "✅ *Готово!*",
        "banned": "🚫 Вы заблокированы. Свяжитесь с администратором.",
        "error_url": "❌ Отправьте корректную ссылку!\n_(должна начинаться с http или https)_",
        "error_download": "❌ Не удалось скачать.\nСсылка неверная или видео закрыто.",
        "error_private": "❌ Видео закрыто или требует авторизации Instagram.\nМожно скачивать только публичные видео.",
        "error_size": "❌ Видео больше 50МБ.\nВыберите качество пониже.",
        "error_generic": "❌ Произошла ошибка. Попробуйте ещё раз.",
        "unknown_cmd": "❗ Неизвестная команда. Вы можете отправить ссылку на видео.",
        "unsupported": "❌ Поддерживаются только TikTok и Instagram!\n\n🎵 tiktok.com\n📸 instagram.com",
        "quality_reduced": "✅ Видео загружено в качестве {q} (файл был слишком большим).",
        "mystats_title": "📊 *Моя статистика*",
        "mystats_total": "📥 Всего скачано: *{n}* видео",
        "mystats_platform": "📱 По платформам:\n{rows}",
        "mystats_empty": "Вы ещё ничего не скачали.",
        "btn_download": "📥 Скачать видео",
        "btn_settings": "⚙️ Настройки",
        "btn_stats": "📊 Статистика",
        "btn_help": "❓ Помощь",
        "btn_lang": "🌐 Язык",
        "btn_quality": "📊 Качество",
        "btn_back": "⬅️ Назад",
        "btn_main": "🏠 Главное меню",
        "q_144": "📱 144p — Мини",
        "q_360": "📱 360p — Лёгкое",
        "q_480": "💻 480p — Среднее",
        "q_720": "🖥️ 720p — HD",
        "q_1080": "📺 1080p — Full HD",
        "q_best": "⚡ Наилучшее",
        "q_audio": "🎵 Только аудио (MP3)",
    },
    "en": {
        "welcome": (
            "👋 Hello, {name}!\n\n"
            "📥 Send a YouTube, TikTok, or Instagram link.\n"
            "I'll download it for you! 🚀\n\n"
            "📌 Use the buttons below:\n\n"
            "➕ Bot works in groups too, press the button to add to a group👇"
        ),
        "help": (
            "📖 *Help*\n\n"
            "▶️ *Download a video:*\n"
            "Send a link → choose quality → done!\n\n"
            "✅ *Supported:*\n"
            "• YouTube (videos & Shorts)\n"
            "• TikTok\n"
            "• Instagram (Reels, posts)\n\n"
            "⚙️ *Commands:*\n"
            "/start — Main menu\n"
            "/settings — Settings\n"
            "/mystats — My statistics\n"
            "/help — Help\n\n"
            "💡 If something fails, check the link and try again."
        ),
        "settings_title": "⚙️ *Settings*",
        "choose_lang": "🌐 Choose a language:",
        "choose_quality": "📊 Choose default quality:",
        "lang_saved": "✅ Language saved: English 🇬🇧",
        "quality_saved": "✅ Default quality: *{q}*",
        "send_url": "🔗 Send a link:",
        "fetching": "🔍 Fetching video info...",
        "downloading": "⏳ Downloading...\n\n📊 Quality: *{q}*",
        "choose_q_for_video": "📊 *Choose quality:*\n\n🔗 {url}",
        "done": "✅ *Done!*",
        "banned": "🚫 You are banned. Contact the administrator.",
        "error_url": "❌ Send a valid link!\n_(must start with http or https)_",
        "error_download": "❌ Download failed.\nInvalid link or video is private.",
        "error_private": "❌ This video is private or requires Instagram login.\nOnly public videos can be downloaded.",
        "error_size": "❌ Video exceeds 50 MB.\nTry a lower quality.",
        "error_generic": "❌ Something went wrong. Please try again.",
        "unknown_cmd": "❗ Unknown command. You can send a video link.",
        "unsupported": "❌ Only TikTok and Instagram links are supported!\n\n🎵 tiktok.com\n📸 instagram.com",
        "quality_reduced": "✅ Video downloaded in {q} quality (file was too large).",
        "mystats_title": "📊 *My Statistics*",
        "mystats_total": "📥 Total downloaded: *{n}* videos",
        "mystats_platform": "📱 By platform:\n{rows}",
        "mystats_empty": "You haven't downloaded anything yet.",
        "btn_download": "📥 Download video",
        "btn_settings": "⚙️ Settings",
        "btn_stats": "📊 Statistics",
        "btn_help": "❓ Help",
        "btn_lang": "🌐 Language",
        "btn_quality": "📊 Quality",
        "btn_back": "⬅️ Back",
        "btn_main": "🏠 Main menu",
        "q_144": "📱 144p — Tiny",
        "q_360": "📱 360p — Light",
        "q_480": "💻 480p — Medium",
        "q_720": "🖥️ 720p — HD",
        "q_1080": "📺 1080p — Full HD",
        "q_best": "⚡ Best available",
        "q_audio": "🎵 Audio only (MP3)",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS["en"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


PLATFORM_EMOJI = {
    "youtube": "▶️ YouTube",
    "tiktok": "🎵 TikTok",
    "instagram": "📸 Instagram",
    "other": "🌐 Other",
}
