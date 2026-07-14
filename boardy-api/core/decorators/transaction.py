import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


def transaction(commit: bool = True, rollback_on_error: bool = True):
    """
    Method-level decorator to override transaction behaviour for a specific method.
    """
    def decorator(func):
        func._tx_commit = commit
        func._tx_rollback_on_error = rollback_on_error
        return func
    return decorator


def _transaction_method(func, commit_default, rollback_default):
    """
    Internal wrapper that adds transaction control using the repository.
    The repository must be available as self._repository (or self._repository_service)
    and implement begin_transaction(), commit_transaction(), rollback_transaction().
    """
    # Read method‑specific overrides, fall back to class defaults
    commit = getattr(func, '_tx_commit', commit_default)
    rollback_on_error = getattr(func, '_tx_rollback_on_error', rollback_default)
    if not commit:
        rollback_on_error = False

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        self_obj = args[0] if args else None
        if not self_obj:
            raise ValueError("Method must be called on an instance of the class")

        # Locate the repository (try common attribute names)
        repo = getattr(self_obj, 'repository', None)
        if repo is None:
            raise AttributeError(
                f"Class {self_obj.__class__.__name__} must have _repository or _repository_service"
            )

        # Verify that the repository has the required transaction methods
        if not hasattr(repo, 'begin_transaction') or not hasattr(repo, 'commit_transaction'):
            raise AttributeError(
                f"Repository {repo.__class__.__name__} must implement begin_transaction, commit_transaction, rollback_transaction"
            )

        # Start transaction (the repository itself manages the connection)
        await repo.begin_transaction()

        try:
            result = await func(*args, **kwargs)
            if commit:
                await repo.commit_transaction()
            return result
        except Exception as e:
            if commit and rollback_on_error:
                await repo.rollback_transaction()
                logger.info(f"ROLLBACK for {func.__qualname__}")
            raise

    return async_wrapper


def transactional_class(
    commit_default: bool = True,
    rollback_default: bool = True,
    exclude_private: bool = False
):
    """
    Class decorator that wraps all public (and optionally private) async methods
    with transaction management using the repository.

    The class must have an attribute '_repository' (or '_repository_service')
    that provides begin_transaction(), commit_transaction(), rollback_transaction().
    """
    def decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if not callable(attr_value):
                continue
            # Skip special methods (double underscores)
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue
            # Skip private methods (single underscore) if requested
            if attr_name.startswith("_") and exclude_private:
                continue
            # Only wrap async methods; sync methods are left untouched
            if asyncio.iscoroutinefunction(attr_value):
                setattr(
                    cls,
                    attr_name,
                    _transaction_method(attr_value, commit_default, rollback_default)
                )
        return cls
    return decorator