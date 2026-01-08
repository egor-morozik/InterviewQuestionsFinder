# Автосборщик вопросов для собеседований

Простая система автоматического сбора технических вопросов для собеседований.

## Возможности

- Автоматический поиск вопросов в интернете
- Генерация ответов через Groq AI
- Сохранение в векторную БД Qdrant
- Автоматизация через GitHub Actions
- Читаемые отчеты в Markdown

### 1. Настройка окружения

Клонируйте репозиторий

git clone https://github.com/egor-morozik/InterviewQuestionsFinder

cd interview-collector

Установите зависимости

pip install -r requirements.txt

### 2. Настройка секретов в GitHub

Добавьте в Secrets репозитория:

GROQ_API_KEY - ключ от Groq Cloud

QDRANT_URL - URL от Qdrant Cloud

QDRANT_API_KEY - ключ от Qdrant

### 3. Запуск вручную

Установите переменные окружения

export GROQ_API_KEY="ваш-ключ"

export QDRANT_URL="ваш-url"

export QDRANT_API_KEY="ваш-ключ"

Запустите сбор

python collector.py

### 4. Просмотр данных

Посмотреть все вопросы

python view_data.py

Посмотреть статистику

python view_data.py --count

Фильтровать по технологии

python view_data.py --tech Python --limit 5

Автоматизация

Система автоматически запускается каждый день в 9:00 UTC через GitHub Actions.

Ручной запуск:

Перейдите в Actions → Daily Question Collection

Нажмите "Run workflow"

Выберите технологии (по умолчанию: Python, Django, SQL, Docker, Redis)

Пример отчета

После каждого запуска создается файл collection_report.md:

Отчет о сборе вопросов для собеседований

Дата: 2024-01-15 09:00:00

Python

- Найдено вопросов: 12
- Добавлено в базу: 8
- Пропущено (дубликаты): 4

Django

- Найдено вопросов: 10
- Добавлено в базу: 7
- Пропущено (дубликаты): 3

Бесплатные ресурсы

Groq: 30 запросов в минуту, 10K токенов в месяц

Qdrant Cloud: 1GB бесплатно

GitHub Actions: 2000 минут в месяц

Технологии

Python + Requests - парсинг и HTTP

Groq API - генерация ответов

Qdrant - векторная база данных

GitHub Actions - автоматизация

Структура

interview-collector/

├── collector.py     # Основной скрипт

├── config.py       # Конфигурация

├── view_data.py    # Просмотр данных

└── .github/workflows/collect.yml # Автоматизация

Настройка

Отредактируйте config.py для изменения:

Технологий для сбора

Поисковых запросов

Параметров Qdrant
