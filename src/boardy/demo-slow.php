<?php

sleep(2); // Имитация долгого запроса к БД

echo json_encode([

'result' => 'done',

'pid' => getmypid(),

'time' => date('H:i:s')

]);
