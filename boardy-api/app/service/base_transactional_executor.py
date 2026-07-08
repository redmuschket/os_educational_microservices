import time
from typing import TypeVar, Generic, Type, Callable, Any, Optional
from abc import ABC, abstractmethod

import logging

logger = logging.getLogger(__name__)

R = TypeVar("R")  # repository type


class BaseTransactionalExecutor(ABC, Generic[R]):
    """
    An abstract base class for any components that perform operations
    with support for transactions, runtime logging, and error handling.
    """

    def __init__(self, repository: R, error_class: Type[Exception]):
        self.repository = repository
        self._error_class = error_class

    @abstractmethod
    async def _commit(self) -> None:
        """Committing a transaction to a specific repository."""
        pass

    @abstractmethod
    async def _rollback(self) -> None:
        """Rollback of a transaction in a specific repository."""
        pass

    async def _execute(
        self,
        operation: Callable[..., Any],
        operation_name: str,
        error_class: Optional[Type[Exception]] = None,
        with_transaction: bool = False,
        *args,
        **kwargs,
    ) -> Any:
        """
        Performs logging, transaction management, and error handling.

        Args:
            operation: asynchronous function to execute
            operation_name: operation name for logs
            error_class: specific error class (if different from the main class)
            with_transaction: if True, calls commit/rollback (for write operations)
            *args, **kwargs: arguments for operation
        """
        logger.info(f"Starting {operation_name}")
        start_time = time.time()

        try:
            result = await operation(*args, **kwargs)
            if with_transaction:
                await self._commit()
            elapsed = time.time() - start_time
            logger.info(f"Completed {operation_name} in {elapsed:.2f}s")
            return result
        except Exception as e:
            if with_transaction:
                await self._rollback()
            elapsed = time.time() - start_time
            logger.error(f"Failed {operation_name} after {elapsed:.2f}s: {e}")
            error_cls = error_class or self._error_class
            raise error_cls(f"{operation_name} failed: {e}") from e
