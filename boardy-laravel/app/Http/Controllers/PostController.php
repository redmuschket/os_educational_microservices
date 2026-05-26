<?php

namespace App\Http\Controllers;



use App\Models\Post;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Redis; 

class PostController extends Controller
{
    use AuthorizesRequests;
    public function index()
    {
        $posts = Post::with('author')
            ->latest()
            ->paginate(10);
        
        return view('posts.index', compact('posts'));
    }

    public function show(Post $post)
    {
        $post->load('author');
        return view('posts.show', compact('post'));
    }

    public function create()
    {
        return view('posts.create');
    }

    public function store(Request $request)
    {
	$validated = $request->validate([
            'title' => 'required|string|max:200',
            'body' => 'required|string|max:5000',
        ]);

    	$post = $request->user()->posts()->create($validated);

    	Redis::publish('new_post', json_encode([
            'id' => $post->id,
            'title' => $post->title,
            'body' => $post->body,
            'author_id' => auth()->id(),
            'author_name' => auth()->user()->name,
            'created_at' => $post->created_at->toISOString(),
        ]));

    	return redirect()->route('posts.show', $post)
        	->with('success', 'Пост создан!');
    }

    public function edit(Post $post)
    {
	$this->authorize('update', $post); 
        return view('posts.edit', compact('post'));
    }

    public function update(Request $request, Post $post)
    {
	$this->authorize('update', $post); 
        $data = $request->validate([
            'title' => 'required|string|max:200',
            'body' => 'required|string|max:5000',
        ]);

        $post->update($data);

        return redirect()->route('posts.show', $post)
            ->with('success', 'Пост обновлён!');
    }

    public function destroy(Post $post)
    {
	$this->authorize('update', $post); 
        $post->delete();

        return redirect()->route('posts.index')
            ->with('success', 'Пост удалён!');
    }
}
