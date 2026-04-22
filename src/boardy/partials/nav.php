<?php
$is_logged = !empty($_SESSION['user_id']);
$user_name = $_SESSION['user_name'] ?? '';
?>
<nav>
  <a href="/" class="brand">Boardy</a>
  <a href="/messages.php">Все посты</a>
  
  <?php if ($is_logged): ?>
    <a href="/submit.php">Добавить пост</a>
    <span class="user-greeting">Привет, <?= htmlspecialchars($user_name) ?>!</span>
    <a href="/logout.php">Выйти</a>
  <?php else: ?>
    <a href="/login.php">Вход</a>
    <a href="/register.php">Регистрация</a>
  <?php endif; ?>
</nav>
