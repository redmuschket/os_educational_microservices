
// Health check endpoint for CI/CD
Route::get('/health', fn () => response()->json(['ok' => true, 'service' => 'laravel']));
