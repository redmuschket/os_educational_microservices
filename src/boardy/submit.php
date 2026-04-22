<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

function getPDO(): PDO {
    $dsn = "mysql:host=localhost;dbname=boardy;charset=utf8mb4";
    return new PDO($dsn, 'boardy', '9988', [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
}

session_set_cookie_params([
    'lifetime' => 0, 
	'path' => '/', 
	'secure' => true,
    'httponly' => true, 
	'samesite' => 'Lax'
]);
session_start();

if (empty($_SESSION['user_id'])) {
    header('Location: /login.php');
    exit; 
}

$success = null;
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $body = trim($_POST['body'] ?? '');
    
    if (strlen($body) < 3) {
        $error = 'Текст поста должен содержать минимум 3 символа';
    } else {
        $pdo = getPDO();
        // 🔐 Кирпичик 11: используем $_SESSION['user_id'] вместо хардкода
        $stmt = $pdo->prepare(
            'INSERT INTO posts (author_id, body, created_at) VALUES (?, ?, NOW())'
        );
        $stmt->execute([$_SESSION['user_id'], $body]);
        $success = 'Пост опубликован!';
    }
}

include __DIR__ . '/partials/head.php';
include __DIR__ . '/partials/nav.php';
?>
<main>
  <h1>Добавить пост</h1>
  <?php if ($success): ?><p class="success"><?= htmlspecialchars($success) ?></p><?php endif; ?>
  <?php if ($error): ?><p class="error"><?= htmlspecialchars($error) ?></p><?php endif; ?>
  
  <form method="POST">
    <label>Текст поста:
      <textarea name="body" rows="5" required minlength="3"><?= htmlspecialchars($_POST['body'] ?? '') ?></textarea>
    </label>
    <button type="submit">Опубликовать</button>
  </form>
  <p><a href="/messages.php">← Вернуться к постам</a></p>
</main>
<?php include __DIR__ . '/partials/foot.php'; ?>
