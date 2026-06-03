@extends('layouts.app')

@section('title', 'Редактировать пост')

@section('content')
    <h1 class="mb-4">Редактировать пост</h1>
    
    <form action="{{ route('posts.update', $post) }}" method="POST">
        @csrf
        @method('PUT')
        
        <div class="mb-3">
            <label for="title" class="form-label">Заголовок</label>
            <input type="text" 
                   name="title" 
                   id="title" 
                   class="form-control @error('title') is-invalid @enderror" 
                   value="{{ old('title', $post->title) }}" 
                   required 
                   maxlength="200">
            @error('title')
                <div class="invalid-feedback">{{ $message }}</div>
            @enderror
        </div>
        
        <div class="mb-3">
            <label for="body" class="form-label">Текст поста</label>
            <textarea name="body" 
                      id="body" 
                      class="form-control @error('body') is-invalid @enderror" 
                      rows="10" 
                      required 
                      maxlength="5000">{{ old('body', $post->body) }}</textarea>
            @error('body')
                <div class="invalid-feedback">{{ $message }}</div>
            @enderror
        </div>
        
        <button type="submit" class="btn btn-warning">Сохранить изменения</button>
        <a href="{{ route('posts.show', $post) }}" class="btn btn-secondary">Отмена</a>
    </form>
@endsection
