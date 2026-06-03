cat > Lab/Lab12/Report.md << 'ENDOFFILE'
# Отчёт по лабораторной работе №12
## Laravel: CRUD, аутентификация, OAuth

**Выполнил:** Салихов Вадим  
**Дата:** 13 мая 2026

---

## Часть A. Установка и переключение домена

### 1. Composer и PHP-расширения

**Установлен Composer глобально.**

**Расширения PHP:**
- mbstring ✅
- xml ✅
- bcmath ✅
- curl ✅
- mysql ✅
- zip ✅

---

### 2. Переезд папок

**Переименовал:**
/var/www/boardy → /var/www/boardy-legacy

**Создал Laravel-проект:**
composer create-project laravel/laravel /var/www/boardy

**Результат:**
- /var/www/boardy-legacy/ — старый PHP-проект (резервная копия)
- /var/www/boardy/ — новый Laravel 11 проект

---

### 3. Структура Laravel

**Назначение папок:**

| Папка | Назначение |
|-------|-----------|
| app/ | Содержит бизнес-логику: модели, контроллеры, политики, сервисы приложения |
| routes/ | Определяет все маршруты приложения (web, api, console, channels) |
| resources/views/ | Blade-шаблоны для отображения данных в браузере |
| database/ | Миграции, сидеры, фабрики для работы с базой данных |
| public/ | Точка входа приложения: index.php, CSS, JS, изображения |

---

### Защитный вопрос 1:

**Почему document_root nginx должен указывать на public/, а не на /var/www/boardy/?**

**Ответ:**

Если указать корень проекта (/var/www/boardy/), произойдёт критическая утечка безопасности:

1. **Прямой доступ к чувствительным файлам:**
   - .env — содержит пароли от БД, API-ключи, секреты
   - composer.json — список зависимостей проекта
   - app/Http/Controllers/*.php — исходный код с бизнес-логикой
   - database/migrations/*.php — структура базы данных
   - storage/logs/laravel.log — логи с возможными ошибками и данными пользователей

2. **Обход Laravel:**
   - Запросы не проходят через public/index.php
   - Не работает роутинг Laravel
   - Не применяются middleware
   - Не работает аутентификация

3. **public/ — единственная безопасная директория:**
   - Содержит только index.php (точка входа)
   - Публичные ассеты (CSS, JS, изображения)
   - Все запросы безопасно обрабатываются ядром Laravel

**Что плохого случится:**
Злоумышленник может получить:
https://site.ru/.env → пароли от БД
https://site.ru/app/Http/Controllers/AdminController.php → исходный код
https://site.ru/database/seeders/DatabaseSeeder.php → данные пользователей

---

### 4. Nginx-конфиг

**Обновлён конфиг /etc/nginx/sites-available/boardy:**

Основные изменения:
- root /var/www/boardy/public (вместо старой папки)
- Добавлена директива try_files для красивых URL

**Перезапуск nginx:**
sudo systemctl restart nginx

---

### Защитный вопрос 2:

**Что делает try_files $uri $uri/ /index.php?$query_string?**

**Ответ:**

Директива проверяет существование файлов в таком порядке:

1. $uri — существует ли запрошенный файл (например, /css/style.css)
2. $uri/ — существует ли запрошенная директория (например, /images/)
3. /index.php?$query_string — если нет, перенаправляет на index.php

**Пример работы:**

| Запрос | Что происходит |
|--------|----------------|
| /css/app.css | Nginx находит файл → отдаёт его |
| /posts/3 | Файла нет → запрос идёт в index.php → Laravel роутит к PostController::show(3) |
| /admin | Файла нет → index.php → Laravel проверяет авторизацию |

**Без этой строки:**
При заходе на /posts/3:
1. Nginx ищет файл /var/www/boardy/public/posts/3
2. Не находит → возвращает 404 Not Found
3. Laravel НЕ получает запрос
4. Роутинг Laravel не работает
5. Все "красивые URL" перестают работать

---

## Часть B. БД, миграции, сидер

### 5. Создание БД boardy_main

**SQL команды:**
CREATE DATABASE boardy_main CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON boardy_main.* TO 'boardy'@'localhost';
FLUSH PRIVILEGES;

**Проверка:**
mysql -e "SHOW DATABASES"
Результат: boardy и boardy_main

---

### Защитный вопрос 3:

**Зачем создаём новую БД boardy_main, а не подгоняем старую под Laravel?**

**Ответ:**

**Проблемы старой БД (boardy):**

1. **Другая схема таблиц:**
   - В старой БД: id INT, created_at DATETIME (без точности)
   - Laravel ожидает: id BIGINT UNSIGNED AUTO_INCREMENT, created_at TIMESTAMP
   - Eloquent ORM требует строго определённые типы

2. **Отсутствуют миграции:**
   - Laravel управляет схемой БД через миграции
   - Старая БД создавалась вручную или через phpMyAdmin
   - Невозможно отследить изменения схемы

3. **Несовместимые collation:**
   - Старая: utf8_general_ci (устаревший)
   - Laravel: utf8mb4_unicode_ci (поддержка emoji, 4-байтных символов)

4. **Отсутствуют системные таблицы Laravel:**
   - migrations — история применённых миграций
   - sessions — хранение сессий
   - password_reset_tokens — сброс пароля
   - cache — кэш

5. **Риск потери данных:**
   - При изменении существующей схемы можно случайно удалить данные
   - Проще создать чистую БД и перенести данные при необходимости

**Вывод:** Создание новой БД — безопаснее и правильнее с архитектурной точки зрения.

---

### 6. Подключение Laravel к БД

**Настроен .env:**
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=boardy_main
DB_USERNAME=boardy
DB_PASSWORD=пароль_от_БД

**Проверка подключения:**
php artisan tinker
>>> DB::connection()->getPdo();
Результат: PDO object returned successfully ✅

---

### 7. Миграции posts и comments

**Создание миграций:**
php artisan make:migration create_posts_table
php artisan make:migration create_comments_table

**Миграция posts:**
- id (BIGINT UNSIGNED, primary key)
- user_id (foreign key → users.id)
- title (VARCHAR 200)
- body (TEXT)
- timestamps (created_at, updated_at)

**Миграция comments:**
- id (BIGINT UNSIGNED, primary key)
- post_id (foreign key → posts.id)
- user_id (foreign key → users.id)
- body (TEXT)
- timestamps (created_at, updated_at)

**Применение миграций:**
php artisan migrate
Результат: Миграции выполнены успешно ✅

---

### 8. Модели со связями

**Модель Post.php:**
- Связь author() → belongsTo(User::class)
- Связь comments() → hasMany(Comment::class)
- Fillable: user_id, title, body

**Модель Comment.php:**
- Связь post() → belongsTo(Post::class)
- Связь author() → belongsTo(User::class)
- Fillable: post_id, user_id, body

**Модель User.php (дополнена):**
- Связь posts() → hasMany(Post::class)
- Связь comments() → hasMany(Comment::class)
- Добавлено поле github_id

**Проверка связей в Tinker:**
Post::first()->author → App\Models\User { id: 1, name: "Тест" }
Post::first()->comments → Collection с комментариями

---

### 9. Сидер

**Фабрика PostFactory:**
- user_id → случайный User
- title → fake()->sentence(4)
- body → fake()->paragraph(3)

**Фабрика CommentFactory:**
- post_id → случайный Post
- user_id → случайный User
- body → fake()->paragraph(2)

**Seeder DatabaseSeeder:**
- 1 тестовый пользователь (test@boardy.local / password)
- 4 случайных пользователя
- 10 постов
- 25 комментариев

**Запуск сидера:**
php artisan db:seed

**Результат:**
User::count() → 5
Post::count() → 10
Comment::count() → 25

---

## Часть C. CRUD постов и комментариев

### 10. Маршруты

**Настроен routes/web.php:**

GET / → redirect to posts.index
Resource Route: posts (7 маршрутов)
POST comments → CommentController::store (с middleware auth)

**Список маршрутов posts:**
GET|HEAD  posts .............. posts.index
GET|HEAD  posts/create ....... posts.create
POST ...... posts ............ posts.store
GET|HEAD  posts/{post} ....... posts.show
GET|HEAD  posts/{post}/edit .. posts.edit
PUT/PATCH posts/{post} ....... posts.update
DELETE .... posts/{post} ..... posts.destroy

---

### 11. Лента постов

**Контроллер PostController::index():**
- Загрузка постов с автором (with('author'))
- Сортировка по дате (latest())
- Пагинация по 10 постов (paginate(10))

**Шаблон posts/index.blade.php:**
- Отображение 10 постов на странице
- Пагинация через $posts->links()
- У каждого поста: заголовок, автор, дата, краткое содержание
- Кнопка "Читать далее"

---

### 12. Страница поста с комментариями

**Контроллер PostController::show():**
- Загрузка поста с автором и комментариями (load('author', 'comments.author'))

**Шаблон posts/show.blade.php:**
- Полный текст поста
- Информация об авторе и дате создания
- Список всех комментариев с авторами
- Форма добавления комментария (только для @auth)
- Кнопки редактирования/удаления (только для автора поста)

---

### 13. Создание поста

**Контроллер PostController::create() + store():**

create():
- Возвращает view 'posts.create'

store():
- Валидация: title (required, max:200), body (required, max:5000)
- Создание поста через $request->user()->posts()->create($data)
- Редирект на страницу поста с сообщением "Пост создан!"

---

### 14. Policy и редактирование

**Создание Policy:**
php artisan make:policy PostPolicy --model=Post

**PostPolicy.php:**
- update() → возвращает true, если user_id === post->user_id
- delete() → возвращает true, если user_id === post->user_id

**Контроллер (методы edit, update, destroy):**
- В каждом методе: $this->authorize('update', $post) или $this->authorize('delete', $post)
- При отсутствии прав → 403 Forbidden

**Blade-шаблон (posts/show.blade.php):**
- Кнопки обернуты в @can('update', $post) и @can('delete', $post)
- Если нет прав → кнопки не отображаются

---

### Защитный вопрос 4:

**Сравните Policy с авторизацией на чистом PHP (Lab10–11). Сколько строк кода ушло на тот же эффект?**

**Ответ:**

**Сравнение:**

| Критерий | Чистый PHP (Lab10–11) | Laravel Policy (Lab12) |
|----------|----------------------|----------------------|
| Проверка прав в контроллере | ~5-10 строк на метод | 1 строка: $this->authorize(...) |
| Проверка в представлении | Ручной if ($post->user_id === auth()->id()) | Директива @can('update', $post) |
| Повторное использование | Копипаст в каждом контроллере | Один класс PostPolicy на всё приложение |
| Читаемость | Запутанная логика в контроллерах | Явные методы update(), delete() в Policy |
| Тестирование | Сложно тестировать отдельно | Policy можно тестировать изолированно |

**Пример на чистом PHP (Lab10):**
session_start();
$post = getPost($id);
if (!isset($_SESSION['user_id']) || $_SESSION['user_id'] !== $post['user_id']) {
    http_response_code(403);
    die('Доступ запрещён');
}
~5-7 строк на каждую проверку

**Пример на Laravel (Lab12):**
$this->authorize('update', $post);
1 строка!

**Итог:** ~30-50 строк ручного кода заменены на ~15 строк в Policy + встроенные директивы Blade.

---

### 15. Удаление поста

**Реализовано в PostController::destroy() с проверкой Policy.**

**Результат:**
- Пост удаляется из БД
- Перенаправление на ленту с сообщением "Пост удалён!"
- Чужие посты удалить невозможно (403 Forbidden)

---

### 16. Комментарий через Blade

**Контроллер CommentController::store():**
- Валидация: post_id (required, exists:posts), body (required, max:1000)
- Создание комментария: $request->user()->comments()->create($data)
- Редирект back() с сообщением "Комментарий добавлен!"

**Маршрут:**
POST comments → CommentController::store (middleware: auth)

**Форма в posts/show.blade.php:**
- Поле textarea для body
- Скрытое поле post_id
- CSRF-токен
- Кнопка "Отправить комментарий"
- Только для авторизованных (@auth)

---

## Часть D. Breeze + Socialite

### 17. Установка Breeze

**Команды:**
composer require laravel/breeze --dev
php artisan breeze:install blade
npm install
npm run build
php artisan migrate

**Результат:**
- Установлен Breeze с Blade-шаблонами
- Созданы маршруты /login, /register, /dashboard
- Созданы контроллеры аутентификации
- Применены миграции (таблицы sessions, password_reset_tokens)

---

### 18. Регистрация и вход

**Протестировано:**
1. Регистрация нового пользователя через /register
2. Автоматический вход после регистрации
3. Выход через /logout
4. Вход через /login с email и паролем

**Результат:**
- Имя пользователя отображается в навбаре
- Сессия сохраняется между запросами
- CSRF-токены работают корректно

---

### 19. GitHub OAuth-приложение

**Создано в GitHub:**
Settings → Developer settings → OAuth Apps → New OAuth App

**Параметры:**
- Application name: Boardy Lab12
- Homepage URL: http://localhost:8000
- Authorization callback URL: http://localhost:8000/auth/github/callback

**Получены:**
- Client ID
- Client Secret (скрыт в скриншоте!)

---

### 20. Socialite

**Установка:**
composer require laravel/socialite

**Миграция:**
php artisan make:migration add_github_id_to_users_table

**Изменения в users таблице:**
- Добавлено поле github_id (string, nullable, unique)

**Настройка config/services.php:**
'github' => [
    'client_id' => env('GITHUB_CLIENT_ID'),
    'client_secret' => env('GITHUB_CLIENT_SECRET'),
    'redirect' => env('GITHUB_REDIRECT'),
]

**Настройка .env:**
GITHUB_CLIENT_ID=ваш_Client_ID
GITHUB_CLIENT_SECRET=ваш_Client_Secret
GITHUB_REDIRECT=http://localhost:8000/auth/github/callback

**Контроллер GitHubController:**
- redirect() → Socialite::driver('github')->redirect()
- callback() → получение пользователя, создание/обновление в БД, Auth::login()

**Маршруты:**
GET auth/github → GitHubController::redirect
GET auth/github/callback → GitHubController::callback

**Кнопка в login.blade.php:**
<a href="{{ route('auth.github') }}">Войти через GitHub</a>

---

### 21. Полный OAuth flow

**Протестировано:**
1. Нажатие кнопки "Войти через GitHub" на /login
2. Редирект на GitHub (страница авторизации)
3. Подтверждение доступа
4. Callback на /auth/github/callback
5. Автоматический вход под GitHub-именем
6. Отображение имени в навбаре

**Результат в БД:**
SELECT id, name, email, github_id FROM users WHERE github_id IS NOT NULL;
Результат: пользователь с заполненным github_id

---

### Защитный вопрос 5:

**Сравните количество строк кода Lab11 (ручной OAuth) и Lab12 (Socialite). Что сократилось и за счёт чего?**

**Ответ:**

**Сравнение:**

| Компонент | Ручной OAuth (Lab11) | Socialite (Lab12) | Экономия |
|-----------|---------------------|------------------|----------|
| Получение access_token | ~20 строк (cURL, POST-запрос) | 0 (делает Socialite) | -20 строк |
| Получение профиля пользователя | ~15 строк (GET /user, парсинг JSON) | 0 (метод user()) | -15 строк |
| Создание/поиск пользователя | ~10 строк (ручной SQL) | ~5 строк (Eloquent) | -5 строк |
| Обработка ошибок | ~10 строк (try-catch, редиректы) | Встроено в Socialite | -10 строк |
| Валидация ответа OAuth | ~5 строк (проверка полей) | Автоматически | -5 строк |
| **Итого:** | **~60 строк** | **~5 строк** | **-55 строк (92%)** |

**Что сократилось:**
1. Ручные HTTP-запросы — Socialite использует Guzzle HTTP Client
2. Парсинг JSON — Socialite возвращает готовый объект Laravel\Socialite\Two\User
3. Сессии и state — Socialite сам генерирует и проверяет state-токен
4. Обработка ошибок — встроенные исключения SocialiteProviders\Exception

**За счёт чего:**
- Абстракция пакета — Socialite инкапсулирует всю логику OAuth 2.0
- Готовые драйверы — поддержка GitHub, Google, Facebook, Twitter из коробки
- Стандартизация — единый интерфейс для всех провайдеров

**Пример ручного OAuth (Lab11):**
// 1. Получение токена (~20 строк)
$tokenResponse = Http::post('https://github.com/login/oauth/access_token', [...]);
parse_str($tokenResponse->body(), $tokenData);
$accessToken = $tokenData['access_token'];

// 2. Получение профиля (~15 строк)
$userResponse = Http::withToken($accessToken)->get('https://api.github.com/user');
$githubUser = $userResponse->json();

// 3. Поиск/создание пользователя (~10 строк)
$user = User::where('email', $githubUser['email'])->first();
if (!$user) { $user = User::create([...]); }

Итого: ~45 строк только для базовой функциональности

**Пример с Socialite (Lab12):**
$githubUser = Socialite::driver('github')->user();
$user = User::updateOrCreate(
    ['email' => $githubUser->getEmail()],
    ['github_id' => $githubUser->getId(), 'name' => $githubUser->getName()]
);
Auth::login($user);

Итого: 4 строки!

---

## Часть E. Архитектурные вопросы

### 22. Что осталось от прошлых практик

**Вопрос:**
У вас на VPS лежат /var/www/boardy-legacy/ (старый PHP) и БД boardy. Зачем мы их не удалили? Что произойдёт, если попробовать открыть https://фамилия.ai-info.ru/login.php (старый PHP-логин)?

**Ответ:**

**Зачем не удалили:**

1. **Резервная копия (backup):**
   - Если в Laravel-версии обнаружится критическая ошибка
   - Можно быстро откатиться к рабочей версии
   - Время на восстановление: минуты вместо часов

2. **Сравнение архитектур:**
   - Можно анализировать различия в производительности
   - Сравнение безопасности (чистый PHP vs Laravel)
   - Оценка сложности разработки и поддержки

3. **Постепенная миграция:**
   - Некоторые функции можно переносить позже
   - A/B тестирование между версиями
   - Обучение на реальных примерах

4. **Демонстрация эволюции:**
   - Показ преподавателю прогресса
   - Понимание разницы между подходами

**Что произойдёт при открытии login.php:**

1. **Nginx настроен на root /var/www/boardy/public:**
   Server root указывает на новую папку Laravel

2. **Запрос https://фамилия.ai-info.ru/login.php:**
   - Nginx ищет файл /var/www/boardy/public/login.php
   - Файл не существует (старый login.php лежит в /var/www/boardy-legacy/)
   - Nginx возвращает 404 Not Found

3. **Если бы nginx был настроен на старую папку:**
   root /var/www/boardy-legacy;
   - Файл login.php нашёлся бы
   - PHP-FPM выполнил бы старый код
   - Но это неправильная конфигурация для Laravel

**Вывод:** Старый login.php физически существует, но недоступен извне благодаря правильной настройке document_root.

---

### 23. FastAPI и React

**Вопрос:**
FastAPI продолжает работать на api.фамилия.ai-info.ru, а React-файлы лежат в Lab9–11. Но в Laravel-проекте мы их не используем. Почему сейчас не используем — что мешает интегрировать? Где они нам пригодятся в Lab13?

**Ответ:**

**Почему не используем сейчас:**

1. **Конфликт архитектур:**
   - Laravel + Blade = Server-Side Rendering (SSR)
     * HTML генерируется на сервере
     * Маршруты обрабатываются в web.php
     * Данные передаются через Blade-переменные
   
   - React = Client-Side Rendering (CSR)
     * HTML генерируется в браузере
     * Маршруты обрабатываются React Router
     * Данные загружаются через API (fetch/axios)

2. **Проблемы интеграции:**
   - Двойной роутинг: Laravel маршруты vs React Router
   - Конфликт ассетов: Laravel Mix/Vite vs Webpack React
   - CSRF-токены: Laravel требует CSRF, React SPA работает с токенами иначе
   - Аутентификация: Laravel сессии vs JWT/OAuth для React

3. **Что мешает:**
   - Laravel Breeze уже настроен на Blade-шаблоны
   - React требует отдельную точку входа (index.html)
   - Laravel ожидает public/index.php как entry point

**Где пригодятся в Lab13:**

1. **Гибридная архитектура (Laravel API + React SPA):**
   
   Laravel (бэкенд):
   - API Routes (routes/api.php)
   - Controllers (возвращают JSON)
   - Eloquent ORM (работа с БД)
   - Sanctum/Passport (API аутентификация)

   React (фронтенд):
   - Компоненты (React)
   - React Router (клиентский роутинг)
   - Axios (запросы к Laravel API)

2. **Реалтайм-функции:**
   - Комментарии без перезагрузки (WebSockets + Laravel Echo + React)
   - Уведомления в реальном времени
   - Онлайн-статус пользователей

3. **Сложный UI:**
   - Drag-and-drop загрузка файлов
   - Rich-text редактор (TinyMCE, Quill)
   - Интерактивные графики (Chart.js, D3.js)
   - Infinite scroll, lazy loading

4. **Микросервисная архитектура:**
   - FastAPI остаётся для ML-функций
   - Laravel — основной бэкенд
   - React — единый фронтенд для всех API

---

### 24. Реалтайм

**Вопрос:**
Сейчас комментарии появляются только после F5. Какое архитектурное решение нам нужно, чтобы один пользователь видел новый комментарий другого без перезагрузки? Какие два сервера-кандидата для этого решения и почему именно они?

**Ответ:**

**Необходимое решение:**
WebSockets — протокол двусторонней связи между клиентом и сервером в реальном времени.

**Как работает:**
1. Пользователь А отправляет комментарий → Laravel сохраняет в БД
2. Laravel публикует событие в WebSocket-канал post.{postId}
3. Пользователь Б (уже подписан на канал через JavaScript) мгновенно получает событие
4. JavaScript добавляет комментарий в DOM без перезагрузки страницы

**Клиент (React/Blade + Laravel Echo):**
Echo.channel(`post.${postId}`)
    .listen('CommentCreated', (e) => {
        // Добавляем комментарий на страницу
        appendComment(e.comment);
    });





