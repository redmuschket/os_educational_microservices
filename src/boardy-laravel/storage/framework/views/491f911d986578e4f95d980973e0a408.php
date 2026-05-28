<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $__env->yieldContent('title', 'Boardy'); ?></title>
    <!-- Bootstrap CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
        <div class="container">
            <a class="navbar-brand" href="<?php echo e(route('posts.index')); ?>">Boardy</a>
            <div class="navbar-nav">
                <?php if(auth()->guard()->check()): ?>
                    <span class="nav-item nav-link">Привет, <?php echo e(Auth::user()->name); ?></span>
                    <a class="nav-item nav-link" href="<?php echo e(route('posts.create')); ?>">Создать пост</a>
                    <form action="<?php echo e(route('logout')); ?>" method="POST" class="d-inline">
                        <?php echo csrf_field(); ?>
                        <button class="btn btn-link nav-link">Выход</button>
                    </form>
                <?php else: ?>
                    <a class="nav-item nav-link" href="<?php echo e(route('login')); ?>">Вход</a>
                    <a class="nav-item nav-link" href="<?php echo e(route('register')); ?>">Регистрация</a>
                <?php endif; ?>
            </div>
        </div>
    </nav>

    <main class="container">
        <?php if(session('success')): ?>
            <div class="alert alert-success"><?php echo e(session('success')); ?></div>
        <?php endif; ?>
        
        <?php if($errors->any()): ?>
            <div class="alert alert-danger">
                <ul class="mb-0">
                    <?php $__currentLoopData = $errors->all(); $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $error): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                        <li><?php echo e($error); ?></li>
                    <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                </ul>
            </div>
        <?php endif; ?>

        <?php echo $__env->yieldContent('content'); ?>
    </main>

    <!-- Bootstrap JS CDN -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <?php echo $__env->yieldContent("scripts"); ?>
</body>
</html>
<?php /**PATH /home/student/boardy/src/boardy-laravel/resources/views/layouts/app.blade.php ENDPATH**/ ?>