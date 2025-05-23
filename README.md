# Task Manager - Система управління завданнями

Багатофункціональна система управління завданнями, проектами та командами, розроблена з використанням Django.

## Зміст

- [Можливості](#можливості)
- [Технічний стек](#технічний-стек)
- [Архітектура проекту](#архітектура-проекту)
- [Установка та запуск](#установка-та-запуск)
- [Структура проекту](#структура-проекту)
- [Моделі даних](#моделі-даних)
- [Основні компоненти](#основні-компоненти)
- [Розширення функціоналу](#розширення-функціоналу)

## Можливості

### Управління завданнями
- Створення, редагування, видалення та перегляд завдань
- Різні статуси завдань (To-do, In Progress, Done)
- Система пошуку та фільтрації завдань
- Встановлення термінів та відстеження дедлайнів
- Позначення пріоритетів завдань

### Управління проєктами
- Створення та управління проєктами
- Об'єднання завдань у проєкти
- Відстеження прогресу проєктів
- Статистика завершених та незавершених завдань
- Редагування та видалення проєктів

### Робота в команді
- Створення та управління командами
- Призначення завдань учасникам команди
- Спільний доступ до проєктів
- Відстеження активності членів команди
- Редагування та видалення команд

### Тегування та категоризація
- Додавання тегів до завдань
- Зручне групування та фільтрація за тегами
- Швидкий доступ до пов'язаних завдань

### Дашборд та статистика
- Персональний дашборд для користувача
- Відображення завдань за терміновістю
- Статистика продуктивності
- Огляд поточних проєктів та команд

## Технічний стек

- **Бекенд:** Django 3.2+, Python 3.8+
- **База даних:** SQLite (для розробки), легко розширюється до PostgreSQL для продакшн
- **Фронтенд:** HTML, CSS, JavaScript, Bootstrap 5
- **UI компоненти:** Font Awesome, Bootstrap модальні вікна, форми
- **Аутентифікація:** Вбудована система Django з розширеннями
- **Інструменти розробника:** Django Debug Toolbar (опціонально)

## Архітектура проекту

Додаток побудовано на основі патерну MTV (Model-Template-View) Django з розширеннями:

1. **Міксини** - для повторного використання коду та логіки
2. **Class-Based Views** - для структурованої обробки запитів
3. **Модульні шаблони** - для повторного використання компонентів інтерфейсу
4. **Сервісний шар** - для відокремлення бізнес-логіки від представлень

## Установка та запуск

### Попередні вимоги
- Python 3.8 або вище
- pip (менеджер пакетів Python)
- virtualenv (опціонально, але рекомендується)

### Кроки встановлення

1. **Клонування репозиторію**
   ```bash
   git clone <repository-url>
   cd task_manager
   ```

2. **Створення віртуального середовища**
   ```bash
   python -m venv venv
   ```

3. **Активація віртуального середовища**
   
   Для Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   Для Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Встановлення залежностей**
   ```bash
   pip install -r requirements.txt
   ```

5. **Застосування міграцій**
   ```bash
   python manage.py migrate
   ```

6. **Створення суперкористувача (опціонально)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Запуск сервера розробки**
   ```bash
   python manage.py runserver
   ```

8. **Доступ до додатку**
   Відкрийте браузер і перейдіть за адресою: http://127.0.0.1:8000/

## Структура проекту

```
task_manager/
│
├── task_manager/          # Основний проєкт Django
│   ├── settings.py        # Налаштування проєкту
│   ├── urls.py            # Основні URL маршрути
│   ├── wsgi.py            # WSGI-конфігурація
│   └── asgi.py            # ASGI-конфігурація
│
├── tasks/                 # Додаток для управління завданнями
│   ├── migrations/        # Міграції бази даних
│   ├── templates/         # HTML-шаблони
│   ├── templatetags/      # Користувацькі теги шаблонів
│   ├── forms.py           # Форми для роботи з даними
│   ├── mixins.py          # Міксини для представлень
│   ├── models.py          # Моделі даних
│   ├── urls.py            # URL-маршрути додатку
│   ├── views.py           # Базові представлення
│   ├── task_views.py      # Представлення для завдань
│   ├── project_views.py   # Представлення для проєктів
│   ├── team_views.py      # Представлення для команд
│   ├── auth_views.py      # Представлення для аутентифікації
│   └── services.py        # Сервісний шар
│
├── templates/             # Загальні шаблони проєкту
│   ├── base.html          # Базовий шаблон
│   ├── components/        # Компоненти інтерфейсу, що повторно використовуються
│   ├── layouts/           # Макети сторінок
│   └── ...                # Інші шаблони
│
├── static/                # Статичні файли (CSS, JS, зображення)
│   ├── css/               # Стилі
│   ├── js/                # JavaScript
│   └── images/            # Зображення
│
├── manage.py              # Скрипт управління Django
├── requirements.txt       # Залежності Python
└── README.md              # Документація проєкту
```

## Моделі даних

### Task (Завдання)
- title - Назва завдання
- description - Опис
- status - Статус (to_do, in_progress, done)
- priority - Пріоритет (low, medium, high)
- deadline - Термін виконання
- created_by - Автор
- assigned_to - Виконавець
- project - Проєкт
- tags - Теги
- created_at - Дата створення
- updated_at - Дата оновлення

### Project (Проєкт)
- name - Назва проєкту
- description - Опис
- created_by - Автор
- created_at - Дата створення
- updated_at - Дата оновлення

### Team (Команда)
- name - Назва команди
- description - Опис
- members - Учасники команди
- projects - Проєкти команди
- created_at - Дата створення

### Tag (Тег)
- name - Назва тегу
- color - Колір (для відображення)

## Основні компоненти

### Міксини (mixins.py)
Міксини використовуються для повторного використання коду в представленнях. Основні міксини:

- **TaskPermissionMixin** - Управління правами доступу до завдань
- **ProjectAccessMixin** - Перевірка доступу до проєктів
- **EntityFormMixin** - Спільні методи для форм сутностей
- **TaskQuerysetMixin** - Часто використовувані запити до завдань
- **FormUserKwargsMixin** - Передача користувача у форми
- **OwnershipMixin** - Автоматичне призначення автора
- **FilterMixin** - Обробка фільтрів у ListView
- **DeleteConfirmationMixin** - Підтвердження видалення об'єктів
- **StatsMixin** - Додавання статистики в контекст

### Представлення (views)
Проєкт використовує Class-Based Views Django для обробки запитів:

- **TaskViews** - Представлення для роботи з завданнями
- **ProjectViews** - Представлення для роботи з проєктами
- **TeamViews** - Представлення для роботи з командами
- **AuthViews** - Представлення для аутентифікації

### Форми (forms.py)
Форми для управління даними:

- **TaskForm** - Форма створення та редагування завдання
- **ProjectForm** - Форма проєкту
- **TeamForm** - Форма команди
- **TaskFilterForm** - Форма для фільтрації завдань
- **RegisterForm** - Форма реєстрації користувача

### Шаблони
Проєкт використовує модульну систему шаблонів з поділом на компоненти:

- **base.html** - Основний шаблон
- **components/** - Компоненти, що повторно використовуються (breadcrumbs, cards, etc.)
- **layouts/** - Макети сторінок
- **tasks/** - Шаблони для завдань
- **projects/** - Шаблони для проєктів
- **teams/** - Шаблони для команд
- **auth/** - Шаблони аутентифікації

## Розширення функціоналу

### Додавання нових типів сутностей
1. Створіть модель у `models.py`
2. Створіть форми у `forms.py`
3. Створіть представлення в новому файлі, наприклад `new_entity_views.py`
4. Додайте URL-маршрути в `urls.py`
5. Створіть шаблони у відповідній папці

### Впровадження нових функцій
1. Для загальної логіки використовуйте міксини в `mixins.py`
2. Для бізнес-логіки створіть функції в `services.py`
3. Для користувацьких тегів використовуйте `templatetags/`

### Налаштування прав доступу
1. Використовуйте `TaskPermissionMixin` як приклад
2. Для більш складних сценаріїв розгляньте Django Permissions або django-guardian

---

## Висновок

Task Manager - це потужний та гнучкий додаток для управління завданнями та проєктами. Він підходить як для особистого використання, так і для невеликих команд. Архітектура додатку заснована на кращих практиках Django і дозволяє легко розширювати функціональність за необхідності.

Якщо у вас виникли питання або пропозиції, не соромтеся створювати issues або pull requests у репозиторії проєкту.