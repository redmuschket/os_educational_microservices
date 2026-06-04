FROM php:8.3-fpm

RUN apt-get update && apt-get install -y \
    git curl libpng-dev libonig-dev libxml2-dev \
    zip unzip libzip-dev \
    && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install pdo_mysql mbstring zip opcache

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

# Копируем файлы зависимостей
COPY composer.json composer.lock ./

# Устанавливаем зависимости, игнорируя проверку версии PHP
RUN composer install --no-dev --no-scripts --no-autoloader --ignore-platform-req=php

# Копируем весь проект
COPY . .

# Генерируем автозагрузку (тоже с игнором проверки PHP)
RUN composer dump-autoload --optimize --ignore-platform-req=php

# Создаём папки и меняем права
RUN mkdir -p storage bootstrap/cache && \
    chown -R www-data:www-data storage bootstrap/cache && \
    chmod -R 775 storage bootstrap/cache

EXPOSE 9000
CMD ["php-fpm"]
