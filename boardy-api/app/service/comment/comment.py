from app.service.comment.repository import CommentRepositoryService
from app.service.base_transactional_executor import BaseTransactionalExecutor
from app.core.decorators import timed_class, transactional_class


@timed_class(exclude_private=False)
@transactional_class(commit_default=True, rollback_default=True, exclude_private=True)
class CommentService(BaseTransactionalExecutor):
    def __init__(self, rs: CommentRepositoryService):
        super().__init__(rs)

    async def select_all_comment(self, post_id: int) -> list[dict[str, str]]:
        items = await self.repository.select_all_comment(post_id)
        for item in items:
            if item.get('created_at'):
                item['created_at'] = str(item['created_at'])
        return items