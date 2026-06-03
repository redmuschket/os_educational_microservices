<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Laravel\Socialite\Facades\Socialite;

class GitHubController extends Controller
{
    public function redirect()
    {
        return Socialite::driver('github')->redirect();
    }

    public function callback()
    {
        try {
            $githubUser = Socialite::driver('github')->user();
            
            $user = User::where('email', $githubUser->getEmail())->first();

            if ($user) {
                $user->update([
                    'github_id' => $githubUser->getId(),
                    'name' => $githubUser->getName() ?? $githubUser->getNickname(),
                ]);
            } else {
                $user = User::create([
                    'github_id' => $githubUser->getId(),
                    'name' => $githubUser->getName() ?? $githubUser->getNickname(),
                    'email' => $githubUser->getEmail(),
                    'password' => bcrypt('12345678'),
                ]);
            }

            Auth::login($user);
            return redirect()->route('posts.index');
        } catch (\Exception $e) {
            return redirect()->route('login')->with('error', 'Ошибка авторизации GitHub');
        }
    }
}
