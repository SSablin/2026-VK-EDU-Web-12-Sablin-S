# ДЗ1. Верстка AskMe

## Автор
Саблин Сергей Александрович, WEB-12

## Страницы
- `public/index.html` - главная, список вопросов
- `public/question.html` - страница одного вопроса
- `public/ask.html` - создание вопроса
- `public/login.html` - вход
- `public/signup.html` - регистрация
- `public/profile.html` - профиль пользователя

## Как открыть
Открыть `public/index.html` в браузере или через Live Server.

# ДЗ2. AskMe на Django

## Что внутри
- Django 5 + SQLite
- 8 страниц: `/`, `/hot/`, `/tag/<name>/`, `/question/<id>/`, `/ask/`, `/login/`, `/signup/`, `/profile/`
- Пагинация на списках вопросов (`?page=N`)
- Bootstrap 5, адаптивная вёрстка (из ДЗ1)

## Запуск локально

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Открыть <http://127.0.0.1:8000/>.

## Запуск в Docker

```bash
cp .env.docker.example .env.local
docker compose up --build
```

Открыть <http://localhost:8000/>.

Остановить: `docker compose down`.

## Структура

- `application/` — настройки Django, корневой `urls.py`
- `core/` — приложение auth-страниц (`login`, `signup`, `profile`)
- `questions/` — приложение вопросов (`index`, `hot`, `tag`, `question`, `ask`)
- `templates/` — общий `base.html` и `includes/` (header, footer, sidebar)
- `static/` — Bootstrap и общий CSS

# ДЗ3

## Что внутри
- Наполнение данными по `python manage.py fill_db [ratio]`
- django-admin по `python manage.py createsuperuser` `/admin/`
- .env.docker для запуска в Docker, .env.local для локального запуска
- ModelManager и методы моделей 

## Запуск в Docker
```bash
docker compose --env-file .env.docker up -d --build
```

Открыть <http://localhost:8000/>.

Остановить: `docker compose down`.

## Запуск локально
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.local.example .env.local
python manage.py migrate
python manage.py runserver
```

Открыть <http://127.0.0.1:8000/>.

# ДЗ4. Авторизация и формы

## Что внутри
- Регистрация, вход, выход и редактирование профиля пользователя
- Защищённый параметр `?next=` после входа
- Валидация паролей через `AUTH_PASSWORD_VALIDATORS`
- ModelForm для создания вопросов и ответов
- Загрузка и отображение аватарок пользователей в `media/`
- AJAX-лайки и дизлайки вопросов и ответов
- AJAX-выбор правильного ответа автором вопроса
- CSRF-защита форм и AJAX-запросов

## Основные страницы
- `/login/` - вход
- `/signup/` - регистрация
- `/logout/` - выход
- `/profile/` - настройки профиля и аватар
- `/ask/` - создание вопроса
- `/question/<id>/` - просмотр вопроса и добавление ответа

## Запуск

Для запуска используются команды из разделов ДЗ2 и ДЗ3.

# ДЗ5

```bash
docker run --rm  -v .:/centrifugo -p 8005:8005 centrifugo/centrifugo:v6 centrifugo -c config.json
```

