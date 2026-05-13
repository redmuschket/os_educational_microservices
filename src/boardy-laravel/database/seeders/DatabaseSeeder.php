<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Post;
use App\Models\Comment;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        // 1. Создаём тестового пользователя
        $testUser = User::factory()->create([
            'name' => 'Тест',
            'email' => 'test@boardy.local',
            'password' => bcrypt('password'),
        ]);

        // 2. Создаём 4 случайных пользователя
        $users = User::factory()->count(4)->create();
        $allUsers = collect([$testUser])->merge($users);

        // 3. Создаём 10 постов от случайных пользователей
        Post::factory()->count(10)->create([
            'user_id' => fn() => $allUsers->random()->id,
        ]);

        // 4. Создаём 25 комментариев
        Comment::factory()->count(25)->create([
            'post_id' => fn() => Post::all()->random()->id,
            'user_id' => fn() => $allUsers->random()->id,
        ]);
    }
}
