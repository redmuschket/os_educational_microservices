from fastapi import FastAPI
from datetime import datetime
import aiomysql
from routers import comments
from routers import ws
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
import asyncio
import json

async def redis_subscriber():
    print("📡 Connecting to Redis...") 
    redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    print("📡 Creating pubsub...") 
    pubsub = redis_client.pubsub()

    print("📡 Subscribing to 'new_post'...")  # ← ДОБАВИТЬ
    await pubsub.subscribe('new_post')
    
    print("📡 Subscribing to 'user.renamed'...")  # ← ДОБАВИТЬ
    await pubsub.subscribe('user.renamed')    
    await pubsub.subscribe('new_comment')  # ← ДОБАВИТЬ!
    await pubsub.subscribe('update_comment')  # ← ДОБАВИТЬ!
    await pubsub.subscribe('delete_comment')  # ← ДОБАВИТЬ!    
    
    async for message in pubsub.listen():
        print(f"📩 Raw message: {message}")
        if message['type'] != 'message':
             continue
        
        data = json.loads(message['data'])
        print(f"Received from Redis: {data}")
        from routers.ws import manager
        await manager.broadcast(data)        
        # Определяем тип события
        if 'type' in data and data['type'] == 'new_post':
            # Отправляем всем WebSocket клиентам
            from routers.ws import manager
            await manager.broadcast({
                'type': 'new_post',
                'post': data
            })
        elif 'user_id' in data and 'new_name' in data:
            # Это событие user.renamed - обновляем комментарии
            print(f"🔄 Updating comments for user {data['user_id']}: {data['old_name']} → {data['new_name']}")
            await update_comments_author_name(data['user_id'], data['new_name'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting background tasks...")
    """Запуск фоновых задач при старте"""
    task = asyncio.create_task(redis_subscriber())
    print("✅ Subscriber task created") 
    yield
    task.cancel()

app = FastAPI(title='Boardy API', version='0.5.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost', 'http://localhost:8000', 'null',],  # <--- ИЗМЕНИТЬ! Было ['*']
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(comments.router, prefix="/api", tags=["Comments"])
app.include_router(ws.router)
DB_CONFIG = {

	'host': '127.0.0.1',

	'port': 3306,

	'user': 'boardy',

	'password': '9988',

	'db': 'boardy_api',

	'charset': 'utf8mb4',

}



async def get_db():
	return await aiomysql.connect(**DB_CONFIG)


@app.get('/api/status')
async def status():
	return {'status': 'ok', 'time': str(datetime.now())}


@app.get('/api/messages')
async def get_messages():
	conn = await get_db()
	async with conn.cursor(aiomysql.DictCursor) as cur:
		await cur.execute(
			'SELECT posts.body AS message, users.name, '
			'posts.created_at FROM posts '
			'JOIN users ON posts.author_id = users.id '
			'ORDER BY posts.created_at DESC'
		)
		messages = await cur.fetchall()
	conn.close()
	for m in messages:
		m['created_at'] = str(m['created_at'])

	return {'messages': messages, 'count': len(messages)}


@app.get('/api/users')
async def get_users():
	conn = await get_db()
	async with conn.cursor(aiomysql.DictCursor) as cur:
		await cur.execute(
			'SELECT id, name, email, created_at FROM users'
		)
		users = await cur.fetchall()
	conn.close()
	for u in users:
		u['created_at'] = str(u['created_at'])
	return {'users': users, 'count': len(users)}

async def update_comments_author_name(user_id: int, new_name: str):
    """Обновляет author_name во всех комментариях пользователя"""
    conn = await aiomysql.connect(**DB_CONFIG)
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE comments SET author_name = %s WHERE user_id = %s",
                (new_name, user_id)
            )
            await conn.commit()
            print(f"✅ Updated comments for user {user_id} to {new_name}")
    finally:
        await conn.ensure_closed()

@app.get("/health")
def health():
    """Health check endpoint for CI/CD"""
    return {"ok": True, "service": "fastapi"}
