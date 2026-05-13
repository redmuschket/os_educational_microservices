@extends('layouts.app')

@section('title', 'Создать пост')

@section('content')
    <h1 class="mb-4">Создать новый пост</h1>
    
    <form action="{{ route('posts.store') }}" method="POST">
        @csrf
        
        <div class="mb-3">
            <label for="title" class="form-label">Заголовок</label>
            <input type="text" 
                   name="title" 
                   id="title" 
                   class="form-control @error('title') is-invalid @enderror" 
                   value="{{ old('title') }}" 
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
                      maxlength="5000">{{ old('body') }}</textarea>
            @error('body')
                <div class="invalid-feedback">{{ $message }}</div>
            @enderror
        </div>
        
        <button type="submit" class="btn btn-primary">Опубликовать</button>
        <a href="{{ route('posts.index') }}" class="btn btn-secondary">Отмена</a>
    </form>
@endsection
