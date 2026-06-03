@extends('layouts.app')

@section('title', 'Лента постов')

@section('content')
    <h1 class="mb-4">Лента постов</h1>
    
    @forelse ($posts as $post)
        <article class="card mb-3">
            <div class="card-body">
                <h3 class="card-title">
                    <a href="{{ route('posts.show', $post) }}" class="text-decoration-none text-dark">
                        {{ $post->title }}
                    </a>
                </h3>
                <h6 class="card-subtitle mb-2 text-muted">
                    Автор: {{ $post->author->name }} • 
                    {{ $post->created_at->format('d.m.Y H:i') }}
                </h6>
                <p class="card-text">{{ Str::limit($post->body, 200) }}</p>
                <a href="{{ route('posts.show', $post) }}" class="btn btn-sm btn-outline-primary">Читать далее</a>
            </div>
        </article>
    @empty
        <div class="alert alert-info">
            Постов пока нет.
        </div>
    @endforelse

    <!-- Ссылки пагинации -->
    <div class="d-flex justify-content-center mt-4">
        {{ $posts->links() }}
    </div>
@endsection
