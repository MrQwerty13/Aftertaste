"""Tiny cookie-driven translation layer for Aftertaste.

Django's own gettext pipeline is intentionally not used: the original app keeps
the selected language in a cookie and resolves strings at render time. That makes
it trivial for anonymous visitors to switch language without touching the DB.
"""

from __future__ import annotations

THEME_COOKIE = "aftertaste_theme"
LANG_COOKIE = "aftertaste_lang"
ACCENT_COOKIE = "aftertaste_accent"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365

SUPPORTED_LANGS = ("en", "ru")
SUPPORTED_THEMES = ("light", "dark")
DEFAULT_LANG = "en"
DEFAULT_THEME = "light"
DEFAULT_ACCENT_HUE = 95

LEGACY_ACCENT_HUES = {
    "lime": 95,
    "red": 8,
    "blue": 217,
    "amber": 38,
    "teal": 170,
}

STRINGS: dict[str, dict[str, str]] = {
    # Chrome
    "nav.home": {"en": "Home", "ru": "Лента"},
    "nav.popular": {"en": "Popular", "ru": "Популярное"},
    "nav.notifications": {"en": "Notifications", "ru": "Уведомления"},
    "nav.profile": {"en": "Profile", "ru": "Профиль"},
    "nav.write": {"en": "Write a take", "ru": "Написать отзыв"},
    "nav.quick": {"en": "Quick add", "ru": "Быстро добавить"},
    "nav.settings": {"en": "Settings", "ru": "Настройки"},
    "nav.about": {"en": "Founder", "ru": "Основатель"},
    "nav.sign_out": {"en": "Sign out", "ru": "Выйти"},
    "nav.log_in": {"en": "Log in", "ru": "Войти"},
    "nav.join": {"en": "Join", "ru": "Регистрация"},
    # Feed
    "feed.title": {
        "en": "Aftertaste — drinks, then opinions",
        "ru": "Aftertaste — сначала напиток, потом мнение",
    },
    "feed.kicker": {
        "en": "Drink first. Talk later.",
        "ru": "Сначала выпей. Потом расскажи.",
    },
    "feed.lede": {
        "en": "Short takes on what you just sipped — coffee, cocktails, tea, anything in a glass.",
        "ru": "Короткие отзывы о том, что только что выпили — кофе, коктейли, чай, всё что в бокале.",
    },
    "feed.create_account": {"en": "Create an account", "ru": "Создать аккаунт"},
    "feed.latest": {"en": "Latest takes", "ru": "Свежие отзывы"},
    "feed.latest_lede": {
        "en": "What people finished drinking, and what they thought.",
        "ru": "Что люди допили и что об этом подумали.",
    },
    "feed.empty": {
        "en": "No takes yet. Be the first to post what you drank.",
        "ru": "Пока пусто. Станьте первым — напишите, что пили.",
    },
    "feed.empty_following": {
        "en": "Your following feed is quiet. Follow people to fill it.",
        "ru": "В подписках тихо. Подпишитесь на людей, чтобы наполнить ленту.",
    },
    "feed.by": {"en": "by {name}", "ru": "от {name}"},
    "feed.open": {"en": "Open", "ru": "Открыть"},
    "feed.comments": {"en": "{count} comments", "ru": "Комментарии: {count}"},
    "feed.reposted_by": {"en": "Reposted by {name}", "ru": "Репост от {name}"},
    "feed.tabs.all": {"en": "For you", "ru": "Лента"},
    "feed.tabs.following": {"en": "Following", "ru": "Подписки"},
    "feed.tabs.popular": {"en": "Popular", "ru": "Популярное"},
    "feed.composer": {
        "en": "What did you drink today?",
        "ru": "Что вы пили сегодня?",
    },
    # Reactions
    "like": {"en": "Like", "ru": "Нравится"},
    "liked": {"en": "Liked", "ru": "Оценено"},
    "like.login": {"en": "Log in to like", "ru": "Войдите, чтобы оценить"},
    "like.error": {
        "en": "Could not update like. Try again.",
        "ru": "Не удалось обновить оценку. Попробуйте ещё раз.",
    },
    "repost": {"en": "Repost", "ru": "Репост"},
    "reposted": {"en": "Reposted", "ru": "В репостах"},
    "repost.login": {"en": "Log in to repost", "ru": "Войдите, чтобы сделать репост"},
    "repost.error": {
        "en": "Could not update repost. Try again.",
        "ru": "Не удалось обновить репост. Попробуйте ещё раз.",
    },
    "unknown_author": {"en": "Unknown", "ru": "Неизвестно"},
    # Auth
    "register.title": {"en": "Join — Aftertaste", "ru": "Регистрация — Aftertaste"},
    "register.heading": {"en": "Join Aftertaste", "ru": "Присоединяйтесь к Aftertaste"},
    "register.lede": {
        "en": "Create an account, then post what you drank.",
        "ru": "Создайте аккаунт и напишите, что пили.",
    },
    "register.submit": {"en": "Create account", "ru": "Создать аккаунт"},
    "register.foot": {"en": "Already here?", "ru": "Уже с нами?"},
    "login.title": {"en": "Log in — Aftertaste", "ru": "Вход — Aftertaste"},
    "login.heading": {"en": "Log in", "ru": "Вход"},
    "login.lede": {
        "en": "Pick up where you left your glass.",
        "ru": "Продолжайте с того места, где оставили бокал.",
    },
    "login.identifier": {"en": "Email or username", "ru": "Email или имя"},
    "login.submit": {"en": "Log in", "ru": "Войти"},
    "login.foot": {"en": "New here?", "ru": "Впервые здесь?"},
    "field.username": {"en": "Username", "ru": "Имя пользователя"},
    "field.email": {"en": "Email", "ru": "Email"},
    "field.password": {"en": "Password", "ru": "Пароль"},
    "field.password_repeat": {"en": "Repeat password", "ru": "Повторите пароль"},
    "auth.invalid_credentials": {
        "en": "Invalid email, username, or password.",
        "ru": "Неверный email, имя пользователя или пароль.",
    },
    # Compose / detail
    "compose.title": {"en": "Write a take — Aftertaste", "ru": "Новый отзыв — Aftertaste"},
    "compose.heading": {"en": "What did you drink?", "ru": "Что вы пили?"},
    "compose.lede": {
        "en": "Name the drink, then leave your honest aftertaste.",
        "ru": "Назовите напиток и оставьте честный послевкус.",
    },
    "compose.drink": {"en": "Drink name", "ru": "Название напитка"},
    "compose.drink_ph": {
        "en": "e.g. Oat flat white, Negroni, Matcha latte",
        "ru": "напр. Флэт уайт на овсе, Негрони, Матча-латте",
    },
    "compose.take": {"en": "Your take", "ru": "Ваш отзыв"},
    "compose.take_ph": {
        "en": "How it smelled, tasted, hit — keep it personal.",
        "ru": "Запах, вкус, ощущение — пишите по-своему.",
    },
    "compose.submit": {"en": "Publish", "ru": "Опубликовать"},
    "edit.title": {"en": "Edit take — Aftertaste", "ru": "Редактировать — Aftertaste"},
    "edit.heading": {"en": "Edit your take", "ru": "Редактировать отзыв"},
    "edit.lede": {
        "en": "Tweak the drink name or what you thought — then save.",
        "ru": "Подправьте название напитка или отзыв — и сохраните.",
    },
    "edit.submit": {"en": "Save changes", "ru": "Сохранить"},
    "edit.cancel": {"en": "Cancel", "ru": "Отмена"},
    "detail.kicker": {"en": "One take", "ru": "Один отзыв"},
    "detail.back": {"en": "Back to feed", "ru": "К ленте"},
    "detail.edited": {"en": "Edited", "ru": "Изменено"},
    "detail.likes": {"en": "Likes", "ru": "Нравится"},
    "detail.comments": {"en": "Comments", "ru": "Комментарии"},
    "detail.reposts": {"en": "Reposts", "ru": "Репосты"},
    "detail.published": {"en": "Published", "ru": "Опубликован"},
    "post.edit": {"en": "Edit", "ru": "Изменить"},
    "post.delete": {"en": "Delete", "ru": "Удалить"},
    "post.delete_confirm": {
        "en": "Delete this take permanently?",
        "ru": "Удалить этот отзыв навсегда?",
    },
    # Comments
    "comments.heading": {"en": "Comments", "ru": "Комментарии"},
    "comments.lede": {
        "en": "React to the take — keep it short and honest.",
        "ru": "Ответьте на отзыв — коротко и честно.",
    },
    "comments.empty": {
        "en": "No comments yet. Start the conversation.",
        "ru": "Пока нет комментариев. Начните разговор.",
    },
    "comments.field": {"en": "Your comment", "ru": "Ваш комментарий"},
    "comments.ph": {
        "en": "What did this take make you think?",
        "ru": "О чём заставил задуматься этот отзыв?",
    },
    "comments.submit": {"en": "Post comment", "ru": "Отправить"},
    "comments.login": {
        "en": "Log in to leave a comment",
        "ru": "Войдите, чтобы комментировать",
    },
    "comments.delete": {"en": "Delete", "ru": "Удалить"},
    "comments.delete_confirm": {
        "en": "Delete this comment?",
        "ru": "Удалить этот комментарий?",
    },
    # Profiles / social
    "profile.title": {"en": "{name} — Aftertaste", "ru": "{name} — Aftertaste"},
    "profile.takes": {"en": "Takes", "ru": "Отзывы"},
    "profile.followers": {"en": "Followers", "ru": "Подписчики"},
    "profile.following": {"en": "Following", "ru": "Подписки"},
    "profile.follow": {"en": "Follow", "ru": "Подписаться"},
    "profile.unfollow": {"en": "Unfollow", "ru": "Отписаться"},
    "profile.you": {"en": "This is you", "ru": "Это вы"},
    "profile.empty": {
        "en": "No takes yet.",
        "ru": "Пока нет отзывов.",
    },
    "profile.empty_reposts": {
        "en": "No reposts yet.",
        "ru": "Пока нет репостов.",
    },
    "profile.bio_empty": {
        "en": "No bio yet.",
        "ru": "Пока без описания.",
    },
    "profile.joined": {"en": "Joined {when}", "ru": "С нами с {when}"},
    "profile.takes_tab": {"en": "Takes", "ru": "Отзывы"},
    "profile.reposts_tab": {"en": "Reposts", "ru": "Репосты"},
    "follow.login": {
        "en": "Log in to follow people",
        "ru": "Войдите, чтобы подписываться",
    },
    # Notifications
    "notifications.title": {"en": "Notifications — Aftertaste", "ru": "Уведомления — Aftertaste"},
    "notifications.heading": {"en": "Notifications", "ru": "Уведомления"},
    "notifications.lede": {
        "en": "Likes, comments, reposts, and new followers.",
        "ru": "Оценки, комментарии, репосты и новые подписчики.",
    },
    "notifications.empty": {
        "en": "Nothing yet. Post a take to start the conversation.",
        "ru": "Пока пусто. Напишите отзыв, чтобы начать разговор.",
    },
    "notifications.liked": {"en": "liked your take", "ru": "оценил ваш отзыв"},
    "notifications.commented": {
        "en": "commented on your take",
        "ru": "прокомментировал ваш отзыв",
    },
    "notifications.followed": {
        "en": "started following you",
        "ru": "подписался на вас",
    },
    "notifications.reposted": {
        "en": "reposted your take",
        "ru": "сделал репост вашего отзыва",
    },
    "notifications.new": {"en": "New", "ru": "Новое"},
    "notifications.mark_read": {"en": "Mark all as read", "ru": "Прочитать все"},
    "notifications.marked_read": {
        "en": "All notifications marked as read.",
        "ru": "Все уведомления прочитаны.",
    },
    # About
    "about.title": {"en": "Founder — Aftertaste", "ru": "Основатель — Aftertaste"},
    "about.kicker": {"en": "The person behind the glass", "ru": "Человек за бокалом"},
    "about.heading": {"en": "Mikhail", "ru": "Михаил"},
    "about.role": {
        "en": "Founder of Aftertaste · developer-engineer",
        "ru": "Основатель Aftertaste · разработчик-инженер",
    },
    "about.p1": {
        "en": "I built Aftertaste as a small place for honest notes on drinks — coffee, cocktails, tea, whatever is in the glass. Short takes, no noise.",
        "ru": "Я сделал Aftertaste как небольшое место для честных заметок о напитках — кофе, коктейли, чай, всё что в бокале. Короткие отзывы, без шума.",
    },
    "about.p2": {
        "en": "I write Python for the web, tinker with Bash, C++, C#, and Swift, and live on macOS. When I am not shipping code, I am usually watching Formula 1.",
        "ru": "Пишу на Python для веба, вожусь с Bash, C++, C# и Swift, живу на macOS. Когда не пишу код — обычно смотрю Формулу-1.",
    },
    "about.p3": {
        "en": "Aftertaste is now a Django app with follows, reposts, and a quick-add PWA. If you post something you drank, you are already part of it.",
        "ru": "Теперь Aftertaste — приложение на Django с подписками, репостами и PWA для быстрого добавления. Если вы написали о том, что пили — вы уже часть этого.",
    },
    "about.based": {"en": "Based in", "ru": "Город"},
    "about.based_value": {"en": "Moscow", "ru": "Москва"},
    "about.stack": {"en": "Tools", "ru": "Инструменты"},
    "about.stack_value": {
        "en": "Python, Django, SQLite, HTML, CSS, JavaScript",
        "ru": "Python, Django, SQLite, HTML, CSS, JavaScript",
    },
    "about.elsewhere": {"en": "Elsewhere", "ru": "Ещё"},
    "about.back": {"en": "Back to feed", "ru": "К ленте"},
    "about.repo": {"en": "View the repo", "ru": "Репозиторий"},
    # Settings
    "settings.title": {"en": "Settings — Aftertaste", "ru": "Настройки — Aftertaste"},
    "settings.heading": {"en": "Settings", "ru": "Настройки"},
    "settings.lede": {
        "en": "Tune how Aftertaste looks, and manage your account.",
        "ru": "Настройте внешний вид Aftertaste и управляйте аккаунтом.",
    },
    "settings.appearance": {"en": "Appearance", "ru": "Внешний вид"},
    "settings.appearance_lede": {
        "en": "Theme, accent color, and language for this browser.",
        "ru": "Тема, цвет акцента и язык для этого браузера.",
    },
    "settings.account": {"en": "Account", "ru": "Аккаунт"},
    "settings.signed_in_as": {
        "en": "Signed in as {name}.",
        "ru": "Вы вошли как {name}.",
    },
    "settings.signed_out_hint": {
        "en": "Sign in to post takes and manage your account.",
        "ru": "Войдите, чтобы публиковать отзывы и управлять аккаунтом.",
    },
    "settings.danger": {"en": "Danger zone", "ru": "Опасная зона"},
    "settings.delete_lede": {
        "en": "Permanently delete your account, your takes, likes, reposts, and comments. This cannot be undone.",
        "ru": "Навсегда удалит аккаунт, ваши отзывы, оценки, репосты и комментарии. Это нельзя отменить.",
    },
    "settings.delete_password": {
        "en": "Confirm with your password",
        "ru": "Подтвердите паролем",
    },
    "settings.delete_submit": {"en": "Delete account", "ru": "Удалить аккаунт"},
    "settings.delete_confirm": {
        "en": "Delete your account and all your takes permanently?",
        "ru": "Удалить аккаунт и все ваши отзывы навсегда?",
    },
    "settings.delete_bad_password": {
        "en": "Wrong password. Account was not deleted.",
        "ru": "Неверный пароль. Аккаунт не удалён.",
    },
    "settings.profile": {"en": "Public profile", "ru": "Публичный профиль"},
    "settings.profile_lede": {
        "en": "Choose how your name appears on your takes.",
        "ru": "Выберите, как ваше имя показывается рядом с отзывами.",
    },
    "settings.display_name": {"en": "Display name", "ru": "Отображаемое имя"},
    "settings.bio": {"en": "Bio", "ru": "О себе"},
    "settings.profile_saved": {"en": "Profile updated.", "ru": "Профиль обновлён."},
    "settings.save_profile": {"en": "Save profile", "ru": "Сохранить профиль"},
    "prefs.theme": {"en": "Theme", "ru": "Тема"},
    "prefs.theme_light": {"en": "Light", "ru": "Светлая"},
    "prefs.theme_dark": {"en": "Dark", "ru": "Тёмная"},
    "prefs.lang": {"en": "Lang", "ru": "Язык"},
    "prefs.lang_en": {"en": "EN", "ru": "EN"},
    "prefs.lang_ru": {"en": "RU", "ru": "RU"},
    "prefs.accent": {"en": "Color", "ru": "Цвет"},
    "prefs.accent_hint": {
        "en": "Drag the strip to pick an accent.",
        "ru": "Потяните полоску, чтобы выбрать акцент.",
    },
    # Quick add / PWA
    "quick.title": {"en": "Quick add — Aftertaste", "ru": "Быстро добавить — Aftertaste"},
    "quick.heading": {"en": "Quick add a drink", "ru": "Быстро добавить напиток"},
    "quick.lede": {
        "en": "One screen, no noise. Name it, describe the aftertaste, done.",
        "ru": "Один экран, без шума. Назовите, опишите послевкусие — готово.",
    },
    "quick.drink": {"en": "Drink", "ru": "Напиток"},
    "quick.drink_ph": {
        "en": "What are you drinking?",
        "ru": "Что вы пьёте?",
    },
    "quick.take": {"en": "Aftertaste", "ru": "Послевкусие"},
    "quick.take_ph": {
        "en": "One or two honest lines…",
        "ru": "Одна-две честные строки…",
    },
    "quick.submit": {"en": "Add it", "ru": "Добавить"},
    "quick.success": {
        "en": "Added. Your take is live.",
        "ru": "Добавлено. Отзыв опубликован.",
    },
    "quick.error": {
        "en": "Could not add the drink. Check the fields.",
        "ru": "Не удалось добавить напиток. Проверьте поля.",
    },
    "quick.login": {
        "en": "Log in to quick-add a drink.",
        "ru": "Войдите, чтобы быстро добавить напиток.",
    },
    "quick.chips": {"en": "Quick picks", "ru": "Быстрый выбор"},
    "quick.chip_coffee": {"en": "Coffee", "ru": "Кофе"},
    "quick.chip_tea": {"en": "Tea", "ru": "Чай"},
    "quick.chip_cocktail": {"en": "Cocktail", "ru": "Коктейль"},
    "quick.chip_beer": {"en": "Beer", "ru": "Пиво"},
    "quick.chip_water": {"en": "Water", "ru": "Вода"},
    "quick.install": {"en": "Install app", "ru": "Установить приложение"},
    "quick.installed": {"en": "App installed", "ru": "Приложение установлено"},
    "quick.offline": {
        "en": "You are offline. The form will sync when you are back.",
        "ru": "Вы офлайн. Форма отправится, когда связь вернётся.",
    },
    # Moderation
    "mod.title": {"en": "Moderate takes", "ru": "Модерация отзывов"},
    "mod.unlock_heading": {"en": "Moderator access", "ru": "Доступ модератора"},
    "mod.unlock_lede": {
        "en": "Enter the moderation key to manage takes.",
        "ru": "Введите ключ модерации, чтобы управлять отзывами.",
    },
    "mod.key": {"en": "Moderation key", "ru": "Ключ модерации"},
    "mod.unlock": {"en": "Unlock", "ru": "Открыть"},
    "mod.lock": {"en": "Lock panel", "ru": "Закрыть панель"},
    "mod.delete": {"en": "Delete", "ru": "Удалить"},
    "mod.confirm": {
        "en": "Delete this take permanently?",
        "ru": "Удалить этот отзыв навсегда?",
    },
    "mod.empty": {"en": "Nothing to moderate.", "ru": "Нечего модерировать."},
    "mod.unlocked": {"en": "Moderator mode on.", "ru": "Режим модератора включён."},
    "mod.locked": {"en": "Moderator mode off.", "ru": "Режим модератора выключен."},
    "mod.bad_key": {"en": "Wrong moderation key.", "ru": "Неверный ключ модерации."},
    "mod.deleted": {"en": "Take deleted.", "ru": "Отзыв удалён."},
    # Flash / validation
    "flash.welcome": {"en": "Welcome to Aftertaste.", "ru": "Добро пожаловать в Aftertaste."},
    "flash.hello": {"en": "Hey, {username}.", "ru": "Привет, {username}."},
    "flash.signed_out": {"en": "Signed out.", "ru": "Вы вышли."},
    "flash.post_live": {"en": "Your take is live.", "ru": "Ваш отзыв опубликован."},
    "flash.post_updated": {"en": "Take updated.", "ru": "Отзыв обновлён."},
    "flash.post_deleted": {"en": "Take deleted.", "ru": "Отзыв удалён."},
    "flash.post_missing": {"en": "Post not found.", "ru": "Отзыв не найден."},
    "flash.comment_added": {"en": "Comment posted.", "ru": "Комментарий добавлен."},
    "flash.comment_deleted": {"en": "Comment deleted.", "ru": "Комментарий удалён."},
    "flash.comment_missing": {"en": "Comment not found.", "ru": "Комментарий не найден."},
    "flash.login_required": {"en": "Log in to continue.", "ru": "Войдите, чтобы продолжить."},
    "flash.followed": {"en": "You follow {name}.", "ru": "Вы подписаны на {name}."},
    "flash.unfollowed": {"en": "You no longer follow {name}.", "ru": "Вы отписались от {name}."},
    "flash.account_deleted": {"en": "Your account was deleted.", "ru": "Ваш аккаунт удалён."},
    "post_missing": {"en": "Post not found.", "ru": "Отзыв не найден."},
    "post_forbidden": {
        "en": "You can only change your own takes.",
        "ru": "Можно менять только свои отзывы.",
    },
    "comment_empty": {
        "en": "Write something before posting a comment.",
        "ru": "Напишите текст комментария.",
    },
    "comment_too_long": {
        "en": "Comment is too long (max {limit} characters).",
        "ru": "Комментарий слишком длинный (макс. {limit} символов).",
    },
    "comment_forbidden": {
        "en": "You can only delete your own comments.",
        "ru": "Можно удалять только свои комментарии.",
    },
    "drink_name_required": {
        "en": "Drink name is required.",
        "ru": "Укажите название напитка.",
    },
    "drink_name_too_long": {
        "en": "Drink name is too long.",
        "ru": "Название напитка слишком длинное.",
    },
    "content_too_short": {
        "en": "Write at least {limit} characters about the drink.",
        "ru": "Напишите хотя бы {limit} символов о напитке.",
    },
    "content_too_long": {
        "en": "Opinion is too long (max {limit} characters).",
        "ru": "Отзыв слишком длинный (макс. {limit} символов).",
    },
    "username_taken": {
        "en": "That username is already taken.",
        "ru": "Это имя пользователя уже занято.",
    },
    "email_taken": {
        "en": "That email is already registered.",
        "ru": "Этот email уже зарегистрирован.",
    },
}


def normalize_theme(value: str | None) -> str:
    if value in SUPPORTED_THEMES:
        return value
    return DEFAULT_THEME


def normalize_lang(value: str | None) -> str:
    if value in SUPPORTED_LANGS:
        return value
    return DEFAULT_LANG


def normalize_accent(value: str | None) -> int:
    """Accent is a hue 0–360. Legacy named cookies still resolve."""
    if value is None or value == "":
        return DEFAULT_ACCENT_HUE
    if value in LEGACY_ACCENT_HUES:
        return LEGACY_ACCENT_HUES[value]
    try:
        hue = int(round(float(value)))
    except (TypeError, ValueError):
        return DEFAULT_ACCENT_HUE
    return max(0, min(360, hue))


def translate(lang: str, key: str, **kwargs) -> str:
    entry = STRINGS.get(key, {})
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def request_lang(request) -> str:
    return normalize_lang(request.COOKIES.get(LANG_COOKIE))
