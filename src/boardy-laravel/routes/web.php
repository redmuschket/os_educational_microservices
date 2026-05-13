<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\PostController;
use App\Http\Controllers\CommentController;

// Главная страница → редирект на ленту постов
Route::get('/', function () {
    return redirect()->route('posts.index');
});
Route::get('/', function () {
    return redirect()->route('posts.index');
});

// Добавь это:
Route::get('/dashboard', function () {
    return redirect()->route('posts.index');
})->middleware(['auth'])->name('dashboard');

// CRUD для постов (7 маршрутов)
Route::resource('posts', PostController::class);

// Сохранение комментария (только для авторизованных)
Route::post('comments', [CommentController::class, 'store'])
    ->middleware('auth')
    ->name('comments.store');
Route::get('auth/github', [App\Http\Controllers\GitHubController::class, 'redirect'])->name('auth.github');
Route::get('auth/github/callback', [App\Http\Controllers\GitHubController::class, 'callback']);
// Подключаем маршруты аутентификации от Breeze
require __DIR__.'/auth.php';
