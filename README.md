# 🎨 Trendsee - Каталог трендов → Генерация

Мини-продукт (MVP) для создания контента на основе трендов с интеграцией OpenRouter.

---

## 🚀 Как запустить

### Требования
- Docker и Docker Compose
- OpenRouter API ключ

### Быстрый старт

1. **Клонировать репозиторий**
```bash
git clone <repository-url>
cd project
```

2. **Настроить переменные окружения**
```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите ваш OpenRouter API ключ:
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

3. **Запустить все сервисы**
```bash
docker-compose up -d
```

4. **Применить миграции (первый запуск)**
```bash
docker-compose exec app alembic upgrade head
```

5. **Открыть приложение**
- Главная страница: http://localhost:8000
- Админ-панель: http://localhost:8000/admin/trends (admin/admin)
- API документация: http://localhost:8000/docs

---

## 📡 Примеры запросов

### API Endpoints

#### Получить список трендов
```bash
curl http://localhost:8000/api/trends
```

#### Получить конкретный тренд
```bash
curl http://localhost:8000/api/trends/1
```

#### Создать тренд (требуется авторизация)
```bash
curl -u admin:admin -X POST http://localhost:8000/api/trends \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новый тренд",
    "type": "photo",
    "preview_url": "https://example.com/image.jpg",
    "tags": ["тренд", "фото"],
    "is_popular": true,
    "is_active": true,
    "price_tokens": 20
  }'
```

#### Обновить тренд (требуется авторизация)
```bash
curl -u admin:admin -X PATCH http://localhost:8000/api/trends/1 \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

#### Загрузить файлы
```bash
curl -X POST http://localhost:8000/api/assets/upload \
  -F "files=@image1.jpg" \
  -F "files=@image2.png"
```

#### Создать генерацию
```bash
curl -X POST http://localhost:8000/api/generations \
  -H "Content-Type: application/json" \
  -d '{
    "trend_id": 1,
    "prompt": "Опиши красивый закат",
    "materials": "Ссылки на референсы...",
    "asset_ids": [1, 2]
  }'
```

#### Получить статус генерации
```bash
curl http://localhost:8000/api/generations/1
```

#### Получить баланс токенов
```bash
curl http://localhost:8000/balance
```

---

## 🎯 Что реализовано

### ✅ Обязательные требования

#### 1. UI (десктоп + мобилка)
- ✅ Адаптивная верстка (Bootstrap 5.3.0)
- ✅ Viewport meta tag для мобильных
- ✅ Responsive grid (col-12 col-sm-6 col-lg-4)
- ✅ Работает на телефоне

#### 2. Каталог трендов
- ✅ Список/грид карточек
- ✅ Поля: название, тип (photo/video), превью, флаги (active/popular)
- ✅ Отображение цены в токенах
- ✅ Теги

#### 3. Админка
- ✅ Создание трендов
- ✅ Редактирование трендов
- ✅ Активация/деактивация
- ✅ Все поля из ТЗ
- ✅ Защита авторизацией (HTTP Basic Auth)

#### 4. Экран генерации
- ✅ Текстовый запрос (prompt)
- ✅ Материалы/ресурсы
- ✅ Прикрепление файлов (upload)
- ✅ Отображение стоимости
- ✅ Статусы: pending → processing → completed/failed
- ✅ Прогресс-бар
- ✅ Отображение результата
- ✅ Автообновление статуса (polling каждые 2 сек)

#### 5. Провайдер моделей (OpenRouter)
- ✅ Слой ModelProvider (`app/services/openrouter.py`)
- ✅ Корректные вызовы API
- ✅ Обработка ключа из переменных окружения
- ✅ Обработка ошибок (timeout, невалидный ответ)
- ✅ Настраиваемая модель (по умолчанию: openai/gpt-4o-mini)

#### 6. Токены и баланс
- ✅ Списание при запуске генерации
- ✅ Проверка баланса перед генерацией
- ✅ Отображение цены в карточке тренда
- ✅ Отображение цены на экране генерации
- ✅ Endpoint для получения баланса

#### 7. API Endpoints
- ✅ `GET /api/trends?active=true&type=video`
- ✅ `GET /api/trends/{id}`
- ✅ `POST /api/trends` (с авторизацией)
- ✅ `PATCH /api/trends/{id}` (с авторизацией)
- ✅ `POST /api/assets/upload`
- ✅ `POST /api/generations`
- ✅ `GET /api/generations/{id}`
- ✅ `DELETE /api/trends/{id}` (бонус, с авторизацией)

### 📦 Технические требования
- ✅ Python + FastAPI
- ✅ PostgreSQL (asyncpg + SQLAlchemy)
- ✅ Celery для асинхронной обработки
- ✅ Redis (broker для Celery)
- ✅ Docker Compose
- ✅ Нормальная структура проекта

### ⭐ Бонусы
- ✅ **Логи/трейсинг** - logging во всех сервисах
- ✅ **Авторизация** - HTTP Basic Auth для админки
- ✅ **Защита от race condition** - SELECT FOR UPDATE при списании токенов
- ✅ **Валидация файлов** - проверка MIME-типов и размера (макс 10MB)
- ✅ **Откат токенов** - возврат при ошибке генерации
- ⚠️ **История генераций** - модель есть, UI нет
- ❌ **WebSocket/SSE** - используется polling
- ❌ **Идемпотентность** - не реализована

---

## 🛠 Что упрощено и почему

### 1. **Polling вместо WebSocket/SSE**
**Почему:** Простота реализации. Polling обновляет статус каждые 2 секунды, что достаточно для MVP.

### 2. **HTTP Basic Auth вместо полноценной авторизации**
**Почему:** Для MVP достаточно. Админка защищена, легко заменить на OAuth2/JWT в будущем.

### 3. **Hardcoded account ID = 1**
**Почему:** В ТЗ не требуется многопользовательская система. Один общий баланс для всех.

### 4. **Файлы хранятся локально**
**Почему:** Упрощение для MVP. В продакшене можно добавить S3/MinIO.

### 5. **Файлы передаются как metadata в промпт**
**Почему:** Текущая модель (gpt-4o-mini) не поддерживает vision. Для обработки изображений нужна multimodal модель (gpt-4-vision, claude-3-opus).

### 6. **Нет миграций базы данных**
**Почему:** Alembic настроен, но для первого запуска можно создать таблицы через `Base.metadata.create_all()`.

### 7. **API endpoints в `/api/*` namespace**
**Почему:** Разделение API и HTML роутов. Стандартная практика для предотвращения конфликтов.

---

## 📂 Структура проекта

```
.
├── app/
│   ├── api/              # API endpoints
│   │   ├── trends.py     # CRUD трендов
│   │   ├── generations.py # Создание и получение генераций
│   │   └── assets.py     # Загрузка файлов
│   ├── services/         # Бизнес-логика
│   │   ├── generation.py # Логика генерации
│   │   └── openrouter.py # Интеграция с OpenRouter
│   ├── templates/        # HTML шаблоны
│   │   ├── base.html
│   │   ├── index.html    # Каталог трендов
│   │   ├── generate.html # Форма генерации
│   │   ├── generation_status.html # Статус генерации
│   │   └── admin/        # Админ шаблоны
│   ├── static/           # CSS стили
│   ├── models.py         # SQLAlchemy модели
│   ├── schemas.py        # Pydantic схемы
│   ├── database.py       # Подключение к БД
│   ├── config.py         # Настройки приложения
│   ├── auth.py           # HTTP Basic Auth
│   └── main.py           # FastAPI приложение
├── migrations/           # Alembic миграции
├── celery_worker.py      # Celery worker
├── docker-compose.yml    # Docker Compose конфигурация
├── Dockerfile            # Dockerfile для приложения
├── requirements.txt      # Python зависимости
├── .env.example          # Пример переменных окружения
└── README.md             # Этот файл
```

---

## 🧪 Отчёт о выполнении

### Время выполнения
**Фактически затрачено:** ~6 часов (чистое время разработки)

### Инструменты вайбкодинга
- **Claude 3.5 Sonnet** (через Rovo Agent) - основной ассистент
- **GitHub Copilot** - автодополнение кода
- **Cursor IDE** - редактирование с AI

### Модель/провайдер для тестов
- **OpenRouter** - api gateway
- **Model:** `openrouter/free` (бесплатная модель - автоматический выбор)
- **Альтернативы:** `openai/gpt-4o-mini`, `google/gemma-3-27b-it:free`, `meta-llama/llama-3.1-8b-instruct:free`

### Расход токенов
- **Разработка (Claude):** ~150K tokens
- **Тестирование (OpenRouter):** ~15K tokens (**$0.00** - использовалась бесплатная модель `openrouter/free`)
- **Общая стоимость разработки:** ~$0.50 (только Claude для разработки)

---

## 🔐 Данные для входа

### Админ-панель
- **URL:** http://localhost:8000/admin/trends
- **Username:** `admin`
- **Password:** `admin`

⚠️ **ВАЖНО:** Измените пароль в `.env` перед продакшеном!

---

## 🐳 Docker сервисы

- **app** - FastAPI приложение (порт 8000)
- **db** - PostgreSQL 15 (порт 5432)
- **redis** - Redis 7 (порт 6379)
- **celery-worker** - Celery worker для обработки генераций

---

## 🧹 Очистка и перезапуск

```bash
# Остановить все сервисы
docker-compose down

# Удалить все данные (БД, Redis)
docker-compose down -v

# Перезапустить
docker-compose up -d --build
```

---

## 📝 Примечания

1. **Первый запуск:** После `docker-compose up` дождитесь готовности БД (healthy status), затем запустите миграции
2. **Баланс по умолчанию:** 1000 токенов (настраивается в `.env`)
3. **Логи Celery:** `docker-compose logs -f celery-worker`
4. **Логи приложения:** `docker-compose logs -f app`

---

## 🎉 Готово к использованию!

Проект полностью функционален и готов к демонстрации. Все обязательные требования ТЗ выполнены.
