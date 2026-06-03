FROM php:8.2-fpm

RUN apt-get update && apt-get install -y \
    git curl libpng-dev libonig-dev libxml2-dev \
    zip unzip libzip-dev \
    && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install pdo_mysql mbstring zip opcache
RUN pecl install redis && docker-php-ext-enable redis

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

# Копируем composer.json и ставим зависимости
COPY composer.json ./
RUN composer install --no-dev --no-scripts --no-autoloader || true

# Копируем весь проект
COPY . .

# Создаём недостающие папки (если их нет) и меняем права
RUN mkdir -p storage framework/bootstrap/cache && \
    chown -R www-data:www-data storage bootstrap/cache && \
    chmod -R 775 storage bootstrap/cache

RUN composer dump-autoload --optimize

EXPOSE 9000
CMD ["php-fpm"]
