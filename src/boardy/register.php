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

if (!empty($_SESSION['user_id'])) {
    header('Location: /messages.php');
    exit;
}

$errors = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name  = trim($_POST['name'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    
    if (strlen($name) < 2) $errors[] = 'Имя должно содержать минимум 2 символа';
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) $errors[] = 'Некорректный email';
    if (strlen($password) < 6) $errors[] = 'Пароль должен содержать минимум 6 символов';
    if (empty($errors)) {
        $pdo = getPDO();
        $stmt = $pdo->prepare('SELECT id FROM users WHERE email = ?');
        $stmt->execute([$email]);
        if ($stmt->fetch()) {
            $errors[] = 'Пользователь с таким email уже существует';
        }
    }
    
    if (empty($errors)) {
        $password_hash = password_hash($password, PASSWORD_BCRYPT);
        $stmt = $pdo->prepare(
            'INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, NOW())'
        );
        $stmt->execute([$name, $email, $password_hash]);
        
        $new_id = $pdo->lastInsertId();
        
        $_SESSION['user_id'] = (int)$new_id;
        $_SESSION['user_name'] = $name;
        
        header('Location: /messages.php');
        exit;
    }
}

include __DIR__ . '/partials/head.php';
include __DIR__ . '/partials/nav.php';
?>
<main>
  <h1>Регистрация</h1>
  <?php foreach ($errors as $err): ?>
    <p class="error"><?= htmlspecialchars($err) ?></p>
  <?php endforeach; ?>
  
  <form method="POST">
    <label>Имя:
      <input type="text" name="name" value="<?= htmlspecialchars($_POST['name'] ?? '') ?>" required minlength="2">
    </label>
    <label>Email:
      <input type="email" name="email" value="<?= htmlspecialchars($_POST['email'] ?? '') ?>" required>
    </label>
    <label>Пароль:
      <input type="password" name="password" required minlength="6">
    </label>
    <button type="submit">Зарегистрироваться</button>
  </form>
  <p>Уже есть аккаунт? <a href="/login.php">Войти</a></p>
</main>
<?php include __DIR__ . '/partials/foot.php'; ?>
