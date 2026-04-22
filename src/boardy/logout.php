<?php
session_set_cookie_params([
    'lifetime' => 0, 
	'path' => '/', 
	'secure' => true,
    'httponly' => true, 
	'samesite' => 'Lax'
]);
session_start();

session_destroy();

if (isset($_COOKIE['PHPSESSID'])) {
    setcookie('PHPSESSID', '', [
        'expires' => time() - 3600,
        'path' => '/',
        'secure' => false,
        'httponly' => true,
        'samesite' => 'Lax'
    ]);
}

$_SESSION = [];

header('Location: /messages.php');
exit;
