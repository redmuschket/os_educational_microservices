<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><?= htmlspecialchars($page_title ?? 'Boardy') ?></title>
  <style>
    body { 
			margin: 0; 
			font-family: system-ui, sans-serif; 
			background: #f5f5f5; 
	}
    nav { 
			background: #1A5276; 
			padding: 1rem; 
			display: flex; 
			gap: 1rem; 
			align-items: center; 
	}
    nav a { 
			color: white; 
			text-decoration: none; 
	}
    nav a.brand { 
			font-weight: bold; 
			font-size: 1.2rem; 
			margin-right: auto; 
	}

    main { 
			max-width: 800px; 
			margin: 2rem auto; 
			padding: 0 1rem; 
	}
    .error { 
			color: #c00; 
			background: #fee; 
			padding: 0.5rem 1rem; 
			border-radius: 4px; 
	}
    .success { 
			color: #060; 
			background: #efe; 
			padding: 0.5rem 1rem; 
			border-radius: 4px; 
	}
    form { 
			background: white; 
			padding: 1.5rem; 
			border-radius: 8px; 
			box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
	}
    input, textarea { 
			width: 100%; 
			padding: 0.5rem; 
			margin: 0.5rem 0; 
			box-sizing: border-box; 
	}
    button { 
			background: #1A5276; 
			color: white; 
			border: none; 
			padding: 0.75rem 1.5rem; 
			border-radius: 4px; 
			cursor: pointer; 
	}
    button:hover { 
			background: #154360; 
	}
    .user-greeting {
  			color: white;
  			font-weight: 500;
	}
  </style>
</head>
<body>
