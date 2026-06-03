<?php $__env->startSection('title', 'Лента постов'); ?>

<?php $__env->startSection('content'); ?>
    <h1 class="mb-4">Лента постов</h1>

    <!-- Кирпичик 7: Контейнер с id для WebSocket-обновлений -->
    <div id="posts-feed">
    <?php $__empty_1 = true; $__currentLoopData = $posts; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $post): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); $__empty_1 = false; ?>
        <article class="card mb-3">
            <div class="card-body">
                <h3 class="card-title">
                    <a href="<?php echo e(route('posts.show', $post)); ?>" class="text-decoration-none text-dark">
                        <?php echo e($post->title); ?>

                    </a>
                </h3>
                <h6 class="card-subtitle mb-2 text-muted">
                    Автор: <?php echo e($post->author->name); ?> •
                    <?php echo e($post->created_at->format('d.m.Y H:i')); ?>

                </h6>
                <p class="card-text"><?php echo e(Str::limit($post->body, 200)); ?></p>
                <a href="<?php echo e(route('posts.show', $post)); ?>" class="btn btn-sm btn-outline-primary">Читать далее</a>
            </div>
        </article>
    <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); if ($__empty_1): ?>
        <div class="alert alert-info">
            Постов пока нет.
        </div>
    <?php endif; ?>
    </div>

    <!-- Ссылки пагинации -->
    <div class="d-flex justify-content-center mt-4">
        <?php echo e($posts->links()); ?>

    </div>
<?php $__env->stopSection(); ?>

<!-- Кирпичик 8: WebSocket-клиент (вставлен напрямую) -->
<script>
const wsUrl = '<?php echo e(app()->environment("production") ? "wss://api." . config("app.fastapi_domain") . "/ws" : "ws://localhost:8000/ws"); ?>';

function connect() {
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => console.log('✅ WS connected');
    ws.onmessage = (e) => {
        try {
            const msg = JSON.parse(e.data);
            if (msg.type === 'new_post') prependPost(msg.post);
        } catch (err) { console.error('WS parse error:', err); }
    };
    ws.onclose = () => setTimeout(connect, 3000);
    ws.onerror = (err) => console.error('WS error:', err);
}

function prependPost(post) {
    const feed = document.getElementById('posts-feed');
    if (!feed) return;
    const el = document.createElement('article');
    el.className = 'card mb-3';
    el.innerHTML = `
        <div class="card-body">
            <h3 class="card-title">
                <a href="/posts/${post.id}" class="text-decoration-none text-dark">
                    ${escapeHtml(post.title)}
                </a>
            </h3>
            <h6 class="card-subtitle mb-2 text-muted">
                Автор: ${escapeHtml(post.author)} •
                ${new Date(post.created_at).toLocaleString('ru-RU', {day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'})}
            </h6>
            <p class="card-text">${escapeHtml(post.body.substring(0,200))}${post.body.length>200?'...':''}</p>
            <a href="/posts/${post.id}" class="btn btn-sm btn-outline-primary">Читать далее</a>
        </div>`;
    feed.prepend(el);
    el.style.opacity = '0';
    el.style.transition = 'opacity 0.3s';
    setTimeout(() => el.style.opacity = '1', 10);
}

function escapeHtml(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

document.addEventListener('DOMContentLoaded', connect);
</script>

<?php echo $__env->make('layouts.app', array_diff_key(get_defined_vars(), ['__data' => 1, '__path' => 1]))->render(); ?><?php /**PATH /home/student/boardy/src/boardy-laravel/resources/views/posts/index.blade.php ENDPATH**/ ?>