<?php $__env->startSection('title', $post->title); ?>

<?php $__env->startSection('content'); ?>
    <article class="mb-4">
        <h1 class="mb-3"><?php echo e($post->title); ?></h1>
        <p class="text-muted mb-4">
            Автор: <strong><?php echo e($post->author->name); ?></strong> • 
            <?php echo e($post->created_at->format('d.m.Y H:i')); ?>

        </p>
        
        <div class="card mb-4">
            <div class="card-body">
                <p class="card-text" style="white-space: pre-wrap;"><?php echo e($post->body); ?></p>
            </div>
        </div>
<!-- Кнопки редактирования и удаления -->
<div class="mb-4">
    <?php if (app(\Illuminate\Contracts\Auth\Access\Gate::class)->check('update', $post)): ?>
        <a href="<?php echo e(route('posts.edit', $post)); ?>" class="btn btn-sm btn-warning">
            Редактировать
        </a>
    <?php endif; ?>

    <?php if (app(\Illuminate\Contracts\Auth\Access\Gate::class)->check('delete', $post)): ?>
        <form action="<?php echo e(route('posts.destroy', $post)); ?>" method="POST" class="d-inline">
            <?php echo csrf_field(); ?>
            <?php echo method_field('DELETE'); ?>
            <button type="submit" class="btn btn-sm btn-danger" 
                    onclick="return confirm('Удалить пост?')">
                Удалить
            </button>
        </form>
    <?php endif; ?>

    <a href="<?php echo e(route('posts.index')); ?>" class="btn btn-sm btn-secondary">
        Назад к ленте
    </a>
</div>        
    </article>
    
    <!-- Комментарии -->
    <section>
        <h3 class="mb-4">Комментарии (<?php echo e($post->comments->count()); ?>)</h3>
        
        <!-- Форма добавления комментария -->
        <?php if(auth()->guard()->check()): ?>
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Оставить комментарий</h5>
                    <form action="<?php echo e(route('comments.store')); ?>" method="POST">
                        <?php echo csrf_field(); ?>
                        <input type="hidden" name="post_id" value="<?php echo e($post->id); ?>">
                        
                        <div class="mb-3">
                            <textarea name="body" class="form-control <?php $__errorArgs = ['body'];
$__bag = $errors->getBag($__errorArgs[1] ?? 'default');
if ($__bag->has($__errorArgs[0])) :
if (isset($message)) { $__messageOriginal = $message; }
$message = $__bag->first($__errorArgs[0]); ?> is-invalid <?php unset($message);
if (isset($__messageOriginal)) { $message = $__messageOriginal; }
endif;
unset($__errorArgs, $__bag); ?>" 
                                      rows="3" placeholder="Ваш комментарий..." required><?php echo e(old('body')); ?></textarea>
                            <?php $__errorArgs = ['body'];
$__bag = $errors->getBag($__errorArgs[1] ?? 'default');
if ($__bag->has($__errorArgs[0])) :
if (isset($message)) { $__messageOriginal = $message; }
$message = $__bag->first($__errorArgs[0]); ?>
                                <div class="invalid-feedback"><?php echo e($message); ?></div>
                            <?php unset($message);
if (isset($__messageOriginal)) { $message = $__messageOriginal; }
endif;
unset($__errorArgs, $__bag); ?>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">Отправить комментарий</button>
                    </form>
                </div>
            </div>
        <?php else: ?>
            <div class="alert alert-info">
                <a href="<?php echo e(route('login')); ?>">Войдите</a>, чтобы комментировать.
            </div>
        <?php endif; ?>
        
        <!-- Список комментариев -->
        <?php $__empty_1 = true; $__currentLoopData = $post->comments; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $comment): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); $__empty_1 = false; ?>
            <div class="card mb-2">
                <div class="card-body">
                    <p class="card-text mb-1"><?php echo e($comment->body); ?></p>
                    <small class="text-muted">
                        <strong><?php echo e($comment->author->name); ?></strong> • 
                        <?php echo e($comment->created_at->format('d.m.Y H:i')); ?>

                    </small>
                </div>
            </div>
        <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); if ($__empty_1): ?>
            <p class="text-muted">Комментариев пока нет.</p>
        <?php endif; ?>
    </section>
<?php $__env->stopSection(); ?>

<?php echo $__env->make('layouts.app', array_diff_key(get_defined_vars(), ['__data' => 1, '__path' => 1]))->render(); ?><?php /**PATH /home/student/boardy/src/boardy-laravel/resources/views/posts/show.blade.php ENDPATH**/ ?>