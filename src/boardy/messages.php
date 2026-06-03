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
	'secure' => true,
    'httponly' => true, 
	'samesite' => 'Lax'
]);
session_start();

$pdo = getPDO();

$stmt = $pdo->query('
    SELECT p.id, p.body, p.created_at, u.name AS author_name
    FROM posts p
    JOIN users u ON p.author_id = u.id
    ORDER BY p.created_at DESC
');
$posts = $stmt->fetchAll(PDO::FETCH_ASSOC);

include __DIR__ . '/partials/head.php';
include __DIR__ . '/partials/nav.php';
?>
<main>
  <h1>Все посты</h1>
  <?php if (empty($posts)): ?>
    <p>Постов пока нет. <a href="/submit.php">Добавьте первый!</a></p>
  <?php else: ?>
    <?php foreach ($posts as $post): ?>
      <article style="background:white; padding:1rem; margin:1rem 0; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
        <p><?= nl2br(htmlspecialchars($post['body'])) ?></p>
        <small>
          Автор: <strong><?= htmlspecialchars($post['author_name']) ?></strong> • 
          <?= htmlspecialchars($post['created_at']) ?>
        </small>
      </article>
    <?php endforeach; ?>
  <?php endif; ?>
  <?php if (!empty($_SESSION['user_id'])): ?>
    <p><a href="/submit.php">+ Добавить пост</a></p>
  <?php endif; ?>
</main>
<?php include __DIR__ . '/partials/foot.php'; ?>
