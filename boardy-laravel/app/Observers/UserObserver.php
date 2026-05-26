<?php

namespace App\Observers;

use App\Models\User;
use Predis\Client;
use Illuminate\Support\Facades\Log;

class UserObserver
{
    public function updated(User $user)
    {
        if ($user->isDirty('name')) {
            $redis = new Client();
            $redis->publish('user.renamed', json_encode([
                'user_id' => $user->id,
                'old_name' => $user->getOriginal('name'),
                'new_name' => $user->name,
                'changed_at' => now()->toISOString(),
            ]));
            
            Log::info("User renamed: {$user->getOriginal('name')} → {$user->name}");
        }
    }
}
