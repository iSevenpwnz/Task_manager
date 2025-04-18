# Розгортання на Render.com

## Кроки для розгортання

1. Зареєструйтесь або увійдіть на [render.com](https://render.com/)

2. Натисніть "New" і виберіть "Web Service"

3. Підключіть свій GitHub репозиторій

4. Заповніть наступні поля:
   - **Name**: Виберіть назву для вашого сервісу
   - **Region**: Europe
   - **Branch**: main (або ваша робоча гілка)
   - **Runtime**: Python 3
   - **Build Command**: `sh build.sh`
   - **Start Command**: `gunicorn task_manager.wsgi:application`

5. В розділі "Advanced" додайте наступні змінні середовища:
   - `DEBUG`: `False`
   - `SECRET_KEY`: Створіть новий надійний секретний ключ
   - `DATABASE_URL`: `postgresql://TASKBD_owner:npg_46epATNwucnh@ep-icy-shape-a29hnrfz-pooler.eu-central-1.aws.neon.tech/TASKBD?sslmode=require`
   - `RENDER`: `true`
   - `LOAD_FIXTURES`: `true` (якщо потрібно завантажити початкові дані з fixtures.json)

6. Налаштуйте інші параметри за потреби (кількість інстансів тощо)

7. Натисніть "Create Web Service"

## База даних

Проект налаштований на використання:
- SQLite для локальної розробки
- PostgreSQL (Neon.tech) для виробничого середовища на render.com

PostgreSQL база даних буде автоматично використовуватись на render.com з наданими параметрами підключення.

## Після розгортання

1. Перевірте, що ваш сервіс працює, перейшовши за URL, який надає Render.

2. Якщо ви не включили змінну середовища `LOAD_FIXTURES`, але пізніше вирішили завантажити початкові дані:
   - Перейдіть до вашого сервісу на Render
   - Відкрийте вкладку "Shell"
   - Виконайте команду: `python manage.py loaddata fixtures.json`

## Локальне тестування перед розгортанням

### Використання SQLite локально (простіше)

1. Переконайтеся, що ви встановили всі залежності:
   ```
   pip install -r requirements.txt
   ```

2. Запустіть міграції:
   ```
   python manage.py migrate
   ```

3. Запустіть сервер розробки:
   ```
   python manage.py runserver
   ```

### Використання PostgreSQL локально (опціонально)

Якщо ви хочете протестувати з PostgreSQL локально:

1. Встановіть PostgreSQL на вашу систему або використовуйте Docker

2. Створіть файл `.env` з наступними змінними:
   ```
   DEBUG=True
   SECRET_KEY=ваш-секретний-ключ
   DATABASE_URL=postgresql://TASKBD_owner:npg_46epATNwucnh@ep-icy-shape-a29hnrfz-pooler.eu-central-1.aws.neon.tech/TASKBD?sslmode=require
   ```

3. Запустіть міграції:
   ```
   python manage.py migrate
   ```

4. Запустіть сервер:
   ```
   python manage.py runserver
   ``` 