# Aftertaste

Aftertaste is a small social app for drinks. Post a short take about what you
just sipped, follow people with good taste, repost the hits, and keep a quick
log of everything you drink.

It is built with Django, server-rendered templates, and a little vanilla
JavaScript. The quick-add flow is an installable PWA, so adding a drink from
your phone takes seconds.

## What you can do

- **Post takes** — name the drink and write up to 280 characters about it
- **Browse the feed** — *For you*, *Following*, and *Popular* tabs
- **Follow people** — profiles with bios, follower counts, and per-user feeds
- **React** — likes and reposts update over AJAX; comments live on take pages
- **Get notified** — likes, comments, reposts, and new followers
- **Quick-add a drink** — installable one-screen flow at `/quick/`
- **Make it yours** — light/dark theme, an RGB hue accent, and English/Russian
- **Moderate** — a secret panel at `/del` for removing takes

## Stack

| Area | Choice |
| --- | --- |
| Runtime | Python 3.12+ |
| Framework | Django 6.0 |
| Database | SQLite by default (any Django database works) |
| Frontend | Django templates, CSS, vanilla JavaScript |
| App | Web app manifest + service worker |
| Languages | English and Russian via a lightweight cookie-based layer |

## Quick start

```bash
git clone https://github.com/MrQwerty13/Aftertaste.git
cd Aftertaste

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo   # optional demo data
python manage.py runserver
```

Open <http://127.0.0.1:8000>.

> If an older checkout already contains a broken `.venv/`, remove it before
> creating a new virtual environment.

### Demo accounts

| Email | Username | Password |
| --- | --- | --- |
| anna@example.com | anna | password |
| leo@example.com | leo | password |

`seed_demo` is safe to run more than once. To start over from a clean demo
state, use `python manage.py seed_demo --reset`.

## Routes

| Path | Purpose |
| --- | --- |
| `/` | Feed (`?tab=all`, `?tab=following`, `?tab=popular`) |
| `/takes/new/` | Write a take |
| `/takes/<id>/` | Take detail and comments |
| `/u/<username>/` | Profile (`?tab=takes`, `?tab=reposts`) |
| `/quick/` | Installable quick-add flow |
| `/notifications/` | Notifications |
| `/settings/` | Appearance, profile, and account settings |
| `/about/` | About the project |
| `/del/` | Moderation panel (secret, not linked in the UI) |
| `/admin/` | Django admin |

## Project layout

```text
.
├── manage.py
├── requirements.txt
├── aftertaste/                  # project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── feed/                        # the application
│   ├── models.py                # Profile, Take, Like, Comment, Follow, Repost, Notification
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── services.py              # feed queries and social actions
│   ├── i18n.py                  # English/Russian strings
│   ├── middleware.py            # activates Django's locale from the cookie
│   ├── context_processors.py
│   ├── admin.py
│   ├── signals.py
│   ├── tests.py
│   ├── migrations/
│   ├── management/commands/     # seed_demo
│   └── templatetags/            # translation, date, and take-card filters
├── templates/                   # base, feed, auth, profile, PWA, moderation
└── static/
    ├── css/style.css            # design system
    ├── css/app.css              # app-specific components
    ├── js/main.js               # social actions, slider, quick-add, PWA
    ├── icons/
    ├── manifest.webmanifest
    └── sw.js
```

## Quick-add PWA

- Visit `/quick/` for the one-screen add flow.
- The manifest is served at `/manifest.webmanifest`; the service worker at
  `/sw.js` with root scope.
- Install from the browser (Chrome/Edge/Safari "Add to Home Screen"). The app
  launches directly on the quick-add screen.
- Static assets are precached, navigation is network-first, and the service
  worker falls back to `/quick/` when offline. Private pages are not cached.
- PWA installation requires HTTPS in production. `localhost` works during
  development.

## Preferences

- **Theme** — light or dark, stored in a cookie and rendered server-side
- **Accent** — a hue from 0 to 360, applied as a CSS custom property
- **Language** — English or Russian, stored in a cookie

A small middleware activates Django's locale from the same language cookie, so
framework messages such as password validation are localized too. No `gettext`
catalogs or database-backed translations are required.

## Moderation

1. Open `/del`
2. Enter the moderation key (default: `wanna_clean`)
3. Delete takes as needed

The panel is session-based and intentionally not linked from the UI.

## Admin

Create a staff account and use Django's admin at `/admin/`:

```bash
python manage.py createsuperuser
```

## Tests and checks

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```

The test suite covers authentication, take CRUD, likes and reposts, comments,
follows, notifications, feed filtering, counts, quick-add, PWA endpoints,
moderation, account deletion, and Russian rendering.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | insecure development key | Set a real secret in production |
| `DJANGO_DEBUG` | `1` | Set to `0` in production |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated hostnames |
| `MODERATION_KEY` | `wanna_clean` | Unlock key for `/del` |

Example:

```bash
export SECRET_KEY='a-long-random-value'
export DJANGO_DEBUG=0
export DJANGO_ALLOWED_HOSTS=aftertaste.example.com
export MODERATION_KEY='another-long-random-value'
```

## Production notes

1. Set the environment variables above.
2. Run `python manage.py migrate`.
3. Run `python manage.py collectstatic`.
4. Serve `staticfiles/` from your web server, or add WhiteNoise.
5. Run the app with your preferred WSGI/ASGI server.
6. Use HTTPS — required for the service worker and PWA installation.

SQLite is fine for a small single-instance deployment. For real concurrency or
multiple app servers, point `DATABASES` at PostgreSQL.
