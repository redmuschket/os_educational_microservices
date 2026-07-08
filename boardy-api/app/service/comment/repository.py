from ..repository import RepositoryService
import aiomysql
from core import logger

logger = logger.get_logger(__name__)


class CommentRepositoryService(RepositoryService):

    def __init__(self, pool: aiomysql.Pool):
        super().__init__(pool=pool)

    async def select_all_comment(self, post_id: int) -> list:
        """Get all the comments on the post."""
        items = await self.select(
            'SELECT c.id, c.body, c.created_at, u.name AS author_name '
            'FROM comments c '
            'JOIN users u ON c.author_id = u.id '
            'WHERE c.post_id = %s '
            'ORDER BY c.created_at DESC',
            (post_id,),
            fetch_all=True,
            dict_cursor=True
        )
        return items