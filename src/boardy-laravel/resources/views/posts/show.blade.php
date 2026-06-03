@extends('layouts.app')

@section('title', $post->title)

@section('content')
    <article class="mb-4">
        <h1 class="mb-3">{{ $post->title }}</h1>
        <p class="text-muted mb-4">
            Автор: <strong>{{ $post->author->name }}</strong> • 
            {{ $post->created_at->format('d.m.Y H:i') }}
        </p>
        
        <div class="card mb-4">
            <div class="card-body">
                <p class="card-text" style="white-space: pre-wrap;">{{ $post->body }}</p>
            </div>
        </div>
<!-- Кнопки редактирования и удаления -->
<div class="mb-4">
    @can('update', $post)
        <a href="{{ route('posts.edit', $post) }}" class="btn btn-sm btn-warning">
            Редактировать
        </a>
    @endcan

    @can('delete', $post)
        <form action="{{ route('posts.destroy', $post) }}" method="POST" class="d-inline">
            @csrf
            @method('DELETE')
            <button type="submit" class="btn btn-sm btn-danger" 
                    onclick="return confirm('Удалить пост?')">
                Удалить
            </button>
        </form>
    @endcan

    <a href="{{ route('posts.index') }}" class="btn btn-sm btn-secondary">
        Назад к ленте
    </a>
</div>        
    </article>
    
    <!-- Комментарии -->
    <section>
        <h3 class="mb-4">Комментарии ({{ $post->comments->count() }})</h3>
        
        <!-- Форма добавления комментария -->
        @auth
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Оставить комментарий</h5>
                    <form action="{{ route('comments.store') }}" method="POST">
                        @csrf
                        <input type="hidden" name="post_id" value="{{ $post->id }}">
                        
                        <div class="mb-3">
                            <textarea name="body" class="form-control @error('body') is-invalid @enderror" 
                                      rows="3" placeholder="Ваш комментарий..." required>{{ old('body') }}</textarea>
                            @error('body')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                        </div>
                        
                        <button type="submit" class="btn btn-primary">Отправить комментарий</button>
                    </form>
                </div>
            </div>
        @else
            <div class="alert alert-info">
                <a href="{{ route('login') }}">Войдите</a>, чтобы комментировать.
            </div>
        @endauth
        
        <!-- Список комментариев -->
        @forelse ($post->comments as $comment)
            <div class="card mb-2">
                <div class="card-body">
                    <p class="card-text mb-1">{{ $comment->body }}</p>
                    <small class="text-muted">
                        <strong>{{ $comment->author->name }}</strong> • 
                        {{ $comment->created_at->format('d.m.Y H:i') }}
                    </small>
                </div>
            </div>
        @empty
            <p class="text-muted">Комментариев пока нет.</p>
        @endforelse
    </section>
@endsection
