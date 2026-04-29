<?php
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
    'domain' => '',
    'secure' => false,
    'httponly' => true,
    'samesite' => 'Lax'
]);

session_start();

if (!empty($_SESSION['user_id'])) {
    header('Location: /messages.php');
    exit;
}

$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    
    $pdo = getPDO();
    
    $stmt = $pdo->prepare('SELECT id, name, password_hash FROM users WHERE email = ?');
    $stmt->execute([$email]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if ($user && password_verify($password, $user['password_hash'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['user_name'] = $user['name'];
        header('Location: /messages.php');
        exit;
    } else {
        $error = 'Неверный email или пароль';
    }
}

include __DIR__ . '/partials/head.php';
include __DIR__ . '/partials/nav.php';
?>
<main>
  <h1>Вход</h1>
  <?php if ($error): ?>
    <p class="error"><?= htmlspecialchars($error) ?></p>
  <?php endif; ?>
  
  <form method="POST">
    <label>Email:
      <input type="email" name="email" value="<?= htmlspecialchars($_POST['email'] ?? '') ?>" required>
    </label>
    <label>Пароль:
      <input type="password" name="password" required>
    </label>
    <button type="submit">Войти</button>
  </form>
  <p>Нет аккаунта? <a href="/register.php">Зарегистрироваться</a></p>
</main>
<?php include __DIR__ . '/partials/foot.php'; ?>
