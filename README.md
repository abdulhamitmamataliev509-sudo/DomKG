# DomKG

**Кыргызстандагы кыймылсыз мүлк marketplace** — батир, үй, жер, коммерциялык мүлк сатуу/ижарага берүү платформасы.

- **Backend:** Python + Flask (application factory архитектурасы)
- **Frontend:** HTML / CSS / JavaScript
- **Database:** PostgreSQL (SQLAlchemy ORM + Alembic migrations)

> Буга чейин түзүлгөн нерсе: **профессионалдуу folder structure** гана. Код жазыла элек, database түзүлө элек. Структура модулдук жана кийин кеңейтүүгө даяр.

---

## Каталог каркасы (Folder Structure)

```
DomKG/
├── backend/                       # Flask backend (frontend'тен толук өзүнчө)
│   ├── app/                       # Flask колдонмосунун негизги пакети
│   │   ├── __init__.py            # application factory: create_app() (кийин түзүлөт)
│   │   ├── extensions.py          # Flask кеңейтүүлөр (db, migrate, jwt, cors)
│   │   ├── models/                # SQLAlchemy ORM моделдери (Database schema)
│   │   │   ├── user.py            # Колдонуучу / ролдор / профиль
│   │   │   ├── property.py        # Мүлк объектилери (батир, үй, жер...)
│   │   │   ├── listing.py         # Жарнама (listing) + баалар/валюта
│   │   │   └── ...                # category, district, photo, favorite, message
│   │   ├── schemas/               # Marshmallow схемалары (сериализация/валидация)
│   │   ├── api/                   # REST API блюпринттери (routes)
│   │   │   ├── auth.py            # Регистрация, логин, токендер
│   │   │   ├── users.py           # Колдонуучу эндпоинттери
│   │   │   ├── properties.py      # Мүлк көрсөтүү/издөө
│   │   │   ├── listings.py        # Жарнамалар (CRUD)
│   │   │   └── categories.py      # Категориялар/фильтрлер
│   │   ├── services/              # Бизнес-логика катмары (routes менен ORM ортосу)
│   │   │   ├── auth_service.py    # Пароль хэшинг, токен чыгаруу
│   │   │   ├── property_service.py# Издөө, фильтрация, пагинация логикасы
│   │   │   └── ...
│   │   ├── repositories/          # Data access катмары (query логикалар топтолгон)
│   │   ├── validators/            # Кастомдук валидация эрежелери
│   │   ├── errors/                # Глобалдык error-handlers
│   │   ├── middleware/            # Request аралык катмар (e.g. rate-limit)
│   │   ├── utils/                 # Helper функциялар (pagination, helpers, constants)
│   │   ├── static/                # Backend'тин статикасы (ойдундагы файлдар үчүн)
│   │   └── templates/             # (Келечекте) сервер-rendered шаблондор
│   ├── migrations/                # Alembic миграция файлдары
│   │   └── versions/              # Ар бир schema өзгөрүүсүнүн версиясы
│   ├── seed/                      # Тесттик/баштапкы seed data скрипттери
│   ├── scripts/                   # CLI скрипттери (admin ж.б.)
│   ├── tests/                     # Backend тесттери
│   │   ├── unit/                  # Бирдик тесттер (models, services)
│   │   ├── integration/           # API/интеграция тесттери
│   │   └── fixtures/              # Тест маалыматтары
│   ├── uploads/                   # Колдонуучу жүктөгөн сүрөттөр/файлдар (gitignore)
│   ├── instance/                  # Runtime маалыматтар (sqlite/secret) (gitignore)
│   ├── run.py                     # Жергиликтүү иштетүү чекити (кийин)
│   ├── wsgi.py                    # Production WSGI чекити (кийин)
│   ├── config.py                  # Config класстары (Dev/Staging/Prod) (кийин)
│   ├── requirements.txt           # Python көз карандылыктары (кийин)
│   ├── .env.example               # Айлана-чөйрө өзгөрмөлөрүнүн шаблону
│   └── .flaskenv                  # Flask CLI конфигурациясы
│
├── frontend/                      # Frontend (backend'тен өзүнчө)
│   ├── index.html                 # Башкы бет
│   ├── pages/                     # Кошумча HTML баракчалар
│   │   ├── listings.html          # Мүлктөр тизмеси / издөө натыйжалары
│   │   ├── listing-detail.html    # Жеке жарнаманын баракчасы
│   │   ├── login.html             # Кириш / катталуу
│   │   └── ...
│   └── src/
│       ├── css/                   # Стилдер (style.css, theme.css ж.б.)
│       ├── js/
│       │   ├── api/               # Backend API чакыруулар (client, endpoints)
│       │   ├── components/        # UI компоненттер (карточкалар, фильтрлер, модал)
│       │   └── utils/             # Форматтоо, debounce ж.б. комуктор
│       └── assets/
│           ├── images/            # Сүрөттөр (лого, баннерлер)
│           ├── icons/             # SVG/иконкалар
│           └── fonts/             # Шрифттер
│
├── docs/                          # Документация (API specs, архитектура, BRD)
├── README.md                      # Бул файл
└── .gitignore                     # git'ке кирбей турган файлдар
```
---

## Ар бир негизги бөлүктүн максаты

### Backend (`backend/`)
Flask **application factory** ыкмасы колдонулат: `app/__init__.py` ичинде `create_app()` функциясы түзүлүп, ал app объектисин кайтарып берет. Бул ыкма бир эле коддон бир нече конфигурация (test, dev, prod) менен бир нече app инстанциясын түзүүгө мүмкүндүк берет жана тестирлөөнү жеңилдетет.

- **`app/models/`** — PostgreSQL'теги таблицалардын ORM түрлөрү. Категориялардан баштап сүрөттөргө чейин бул жерде моделденет.
- **`app/api/`** — HTTP эндпоинттер (routes). Ар бир домен өз блюпринтине бөлүнгөн — модулдук.
- **`app/services/`** — Бизнес-логика: routes моделдерге түз эмес, service аркылуу кайрылат. Бул катмар кодду таза жана тесттелүүчү кылат.
- **`app/repositories/`** — Маалыматка жетүү/query логикасы топтолгон катмар.
- **`app/schemas/`** — Кирген/чьгкан маалыматтарды сервистөө жана валидациялоо (Marshmallow).
- **`migrations/`** — Schema өзгөрүүлөрү версияланган (Alembic) — туруктуу эволюция.
- **`tests/`** — Unit жана integration тесттер өз-өзүнчө бөлүнгөн.
- **`uploads/`**, **`instance/`** — Runtime/колдонуучу маалыматтары, git'ке кирбейт.

### Frontend (`frontend/`)
Backend'тен толук өзүнчө — API аркылуу гана байланышат.
- **`index.html`** + **`pages/`** — ар бир бет өз HTML файлына ээ.
- **`src/js/api/`** — Backend'ке чакыруулар бир жерде топтолгон (endpoints бир жерде).
- **`src/js/components/`** — кайра колдонулуучу UI бөлүкчөлөрү.
- **`src/assets/`** — сүрөттөр, иконкалар, шрифттер.

---

## Колдонуу боюнча эскертүү
- Азырынча **код жок** — бул текше каталог каркасы.
- Backend'ти иштетүү үчүн кийин `run.py`, `config.py` жана `app/__init__.py` (factory) түзүлөт.
- Бош папкалар git'те сакталып калышы үчүн `.gitkeep` файлдары коюлган (`.gitignore` аркылуу контролдонушат).