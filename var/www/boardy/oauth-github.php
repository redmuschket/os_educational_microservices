<?php
session_start();

$state = bin2hex(random_bytes(16));
$_SESSION['oauth_state'] = $state;

$client_id = 'Ov23liOUwDMjxUpDHpVT'; 

$params = http_build_query([
    'client_id' => $client_id,
    'redirect_uri' => 'http://localhost/oauth-callback.php',
    'scope' => 'read:user',
    'state' => $state,
]);

header("Location: https://github.com/login/oauth/authorize?$params");
exit;
