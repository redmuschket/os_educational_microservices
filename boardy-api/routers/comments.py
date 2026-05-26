from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import aiomysql
from database import get_db
from auth import get_current_user

router = APIRouter()

class CommentCreate(BaseModel):
    body: str
    author_name: str  # Оставляем для curl, но в БД не пишем

class CommentUpdate(BaseModel):
    body: str

@router.get('/posts/{post_id}/comments')
async def get_comments(post_id: int):
    """Публичный эндпоинт - чтение комментариев"""
    conn = await get_db()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(
            'SELECT c.id, c.body, c.created_at, u.name AS author_name '
            'FROM comments c '
            'JOIN users u ON c.author_id = u.id '
            'WHERE c.post_id = %s '
            'ORDER BY c.created_at DESC',
            (post_id,)
        )
        items = await cur.fetchall()
        conn.close()
        for item in items:
            if item.get('created_at'):
                item['created_at'] = str(item['created_at'])
        return {'items': items, 'count': len(items)}

@router.post('/posts/{post_id}/comments', status_code=201)
async def create_comment(
    post_id: int,
    data: CommentCreate,
    user: dict = Depends(get_current_user)
):
    if not data.body.strip():
        raise HTTPException(status_code=422, detail='Текст комментария пустой')

    conn = await get_db()
    async with conn.cursor() as cur:
        await cur.execute('SELECT id FROM posts WHERE id = %s', (post_id,))
        if not await cur.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail='Пост не найден')
        
        # Вставляем ТОЛЬКО author_id (имя возьмем через JOIN при чтении)
        await cur.execute(
            'INSERT INTO comments (body, post_id, author_id) VALUES (%s, %s, %s)',
            (data.body, post_id, user['sub'])
        )
        await conn.commit()
        new_id = cur.lastrowid
        conn.close()
        # ДОБАВИТЬ: Публикация в Redis!
        import redis.asyncio as redis
        import json
    
        redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
        await redis_client.publish('new_comment', json.dumps({
            'type': 'new_comment',
            'comment': {
                'id': new_id,
                'body': data.body,
                'author_name': user.get('name', 'Anonymous'),
                'user_id': user['sub'],
                'post_id': post_id,
            }
        }))
        await redis_client.close()
        return {'id': new_id, 'body': data.body, 'author_name': data.author_name, 'status': 'created'}

@router.put('/comments/{comment_id}')
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    user: dict = Depends(get_current_user)
):
    """Обновление - только владелец"""
    if not data.body.strip():
        raise HTTPException(status_code=422, detail='Текст комментария пустой')

    conn = await get_db()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute('SELECT author_id FROM comments WHERE id = %s', (comment_id,))
        comment = await cur.fetchone()

        if not comment:
            conn.close()
            raise HTTPException(status_code=404, detail='Комментарий не найден')

        if comment['author_id'] != int(user['sub']):
            conn.close()
            raise HTTPException(status_code=403, detail='Not owner')

        await cur.execute('UPDATE comments SET body = %s WHERE id = %s', (data.body, comment_id))
        await conn.commit()
        # ДОБАВИТЬ: Публикация в Redis!
        import redis.asyncio as redis
        import json
        
        redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
        await redis_client.publish('update_comment', json.dumps({
            'type': 'update_comment',
            'comment': {
                'id': comment_id,
                'body': data.body,
                'author_name': user.get('name', 'Anonymous'),
                'user_id': user['sub'],
            }
        }))
        await redis_client.close()    
        conn.close()
        return {'id': comment_id, 'body': data.body, 'status': 'updated'}

@router.delete('/comments/{comment_id}', status_code=204)
async def delete_comment(
    comment_id: int,
    user: dict = Depends(get_current_user)
):
    """Удаление - только владелец"""
    conn = await get_db()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute('SELECT author_id FROM comments WHERE id = %s', (comment_id,))
        comment = await cur.fetchone()

        if not comment:
            conn.close()
            raise HTTPException(status_code=404, detail='Комментарий не найден')

        if comment['author_id'] != int(user['sub']):
            conn.close()
            raise HTTPException(status_code=403, detail='Not owner')

        await cur.execute('DELETE FROM comments WHERE id = %s', (comment_id,))
        await conn.commit()
        import redis.asyncio as redis
        import json
        
        redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
        await redis_client.publish('delete_comment', json.dumps({
            'type': 'delete_comment',
            'comment_id': comment_id,
        }))
        await redis_client.close()
        conn.close()
