from app.service.comment.repository import CommentRepositoryService
import aiomysql

class CommentService:
    def __init__(self, rs: CommentRepositoryService):
        self._repository_service = rs

    async def _commit(self, conn: aiomysql.Connection) -> None:
        await self._repository_service.commit_transaction(conn)

    async def _rollback(self, conn: aiomysql.Connection) -> None:
        await self._repository_service.rollback_transaction(conn)

    async def select_all_comment(self, post_id: int) -> list[dict[str, str]]:
        return await self._execute(
            operation=self._select_all_comment,
            operation_name="get all comment",
            error_class=getattr(self, "_create_error", None),
            post_id=post_id,
        )

    async def _select_all_comment(self, post_id: int) -> list[dict[str, str]]:
        items = await self._repository_service.select_all_comment(post_id)
        for item in items:
            if item.get('created_at'):
                item['created_at'] = str(item['created_at'])
        return items