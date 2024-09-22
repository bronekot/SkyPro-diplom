# Task Tracker API

Это серверное приложение для работы с базой данных, представляющее собой трекер задач сотрудников. API позволяет управлять сотрудниками и задачами, а также предоставляет специальные эндпоинты для анализа загруженности сотрудников и важности задач.

## Технологии

- Python 3.12
- Django 5.1
- Django REST Framework
- PostgreSQL
- Docker

## Структура проекта

- `config/`: Конфигурация Django проекта
- `tracker/`: Основное приложение
  - `models.py`: Модели данных (Employee, Task)
  - `serializers.py`: Сериализаторы для моделей
  - `views.py`: ViewSets для API
  - `urls.py`: URL маршруты
  - `tests.py`: Тесты
- `docker-compose.yaml`: Конфигурация Docker
- `Dockerfile`: Инструкции для сборки Docker-образа
- `pyproject.toml`: Зависимости проекта и конфигурация Poetry

## Установка и запуск

1. Убедитесь, что у вас установлены Docker и Docker Compose.
2. Клонируйте репозиторий:

   ```
   git clone <URL репозитория>
   cd <директория проекта>
   ```
3. Создайте файл `.env` в корне проекта и добавьте необходимые переменные окружения:

   ```
   POSTGRES_DB=your_db_name
   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   ```
4. Запустите проект с помощью Docker Compose:

   ```
   docker-compose up --build
   ```
5. API будет доступно по адресу `http://localhost:8000/api/`.

## API endpoints

### Сотрудники (Employees)

- `GET /api/employees/`: Получить список всех сотрудников
- `POST /api/employees/`: Создать нового сотрудника
- `GET /api/employees/{id}/`: Получить информацию о конкретном сотруднике
- `PUT /api/employees/{id}/`: Обновить информацию о сотруднике
- `PATCH /api/employees/{id}/`: Частично обновить информацию о сотруднике
- `DELETE /api/employees/{id}/`: Удалить сотрудника
- `GET /api/employees/busy_employees/`: Получить список сотрудников, отсортированный по количеству активных задач

### Задачи (Tasks)

- `GET /api/tasks/`: Получить список всех задач
- `POST /api/tasks/`: Создать новую задачу
- `GET /api/tasks/{id}/`: Получить информацию о конкретной задаче
- `PUT /api/tasks/{id}/`: Обновить информацию о задаче
- `PATCH /api/tasks/{id}/`: Частично обновить информацию о задаче
- `DELETE /api/tasks/{id}/`: Удалить задачу
- `GET /api/tasks/important_tasks/`: Получить список важных задач с рекомендуемыми исполнителями

## Документация API

Полная документация API доступна по адресу `http://localhost:8000/api/schema/swagger-ui/` после запуска проекта.

## Запуск тестов и проверка покрытия кода тестами

Для запуска тестов используйте команду:

```
docker-compose run --rm test
```

## Проверка соответствия PEP8

```
docker-compose run --rm web flake8 .
```

Тесты уже настроены на максимальнгую длину строки в 120 символов.

## Разработка

Проект использует Poetry для управления зависимостями. Если вы хотите работать над проектом локально, установите Poetry и выполните:

```
poetry install
poetry shell
```

Затем вы можете запускать команды Django, такие как `python manage.py runserver`, без использования Docker.
