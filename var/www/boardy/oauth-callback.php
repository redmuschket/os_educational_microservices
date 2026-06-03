<?php
session_start();

// Проверка state
if (($_GET['state'] ?? '') !== ($_SESSION['oauth_state'] ?? '')) {
    die('Invalid state');
}

// Обмен кода на токен доступа
$ch = curl_init('https://github.com/login/oauth/access_token');
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => http_build_query([
        'client_id' => 'Ov23liOUwDMjxUpDHpVT',     // <-- Твой ID
        'client_secret' => '6faf818c3ef1a952f959c21d81493fa078b210d4',    // <-- Твой Secret
        'code' => $_GET['code'],
    ]),
    CURLOPT_HTTPHEADER => ['Accept: application/json'],
    CURLOPT_RETURNTRANSFER => true,
]);

$response = json_decode(curl_exec($ch), true);
curl_close($ch);

if (!isset($response['access_token'])) {
    die('Ошибка получения токена');
}

$access_token = $response['access_token'];

// Получение профиля
$ch = curl_init('https://api.github.com/user');
curl_setopt_array($ch, [
    CURLOPT_HTTPHEADER => [
        "Authorization: Bearer $access_token",
        'User-Agent: Boardy' 
    ],
    CURLOPT_RETURNTRANSFER => true,
]);

$profile = json_decode(curl_exec($ch), true);
curl_close($ch);


$pdo = new PDO('mysql:host=localhost;dbname=boardy', 'boardy', '9988');


$stmt = $pdo->prepare('SELECT id, name FROM users WHERE github_id = ?');
$stmt->execute([$profile['id']]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$user) {
    $stmt = $pdo->prepare('INSERT INTO users (name, email, github_id) VALUES (?, ?, ?)');
    $stmt->execute([$profile['login'], $profile['email'] ?? '', $profile['id']]);
    $userId = $pdo->lastInsertId();
    $userName = $profile['login'];
} else {
    $userId = $user['id'];
    $userName = $user['name'];
}

$_SESSION['user_id'] = $userId;
$_SESSION['user_name'] = $userName;

header('Location: /messages.php');
exit;
