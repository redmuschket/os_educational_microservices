import time
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


def transaction(commit: bool = True, rollback_on_error: bool = True):
    """
    A decorator to override transaction behaviour at the method level.

    Args:
        commit: whether to commit after successful execution
        rollback_on_error: whether to rollback on exception (ignored if commit=False)
    """
    def decorator(func):
        func._tx_commit = commit
        func._tx_rollback_on_error = rollback_on_error
        return func
    return decorator


def _transaction_method(func, commit_default, rollback_default):
    """
    Internal wrapper that adds transaction control (commit/rollback) to an async method.
    """
    # Read method‑specific overrides, fall back to class defaults
    commit = getattr(func, '_tx_commit', commit_default)
    rollback_on_error = getattr(func, '_tx_rollback_on_error', rollback_default)
    # If we never commit, rollback makes no sense
    if not commit:
        rollback_on_error = False

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # First argument is always 'self' (the class instance)
        self_obj = args[0] if args else None
        if not self_obj:
            raise ValueError("Method must be called on an instance of the class")

        # Ensure the instance implements the required transaction methods
        if not hasattr(self_obj, '_commit') or not hasattr(self_obj, '_rollback'):
            raise AttributeError(
                f"Class {self_obj.__class__.__name__} must implement _commit and _rollback"
            )

        try:
            result = await func(*args, **kwargs)
            if commit:
                await self_obj._commit()
            return result
        except Exception as e:
            if commit and rollback_on_error:
                await self_obj._rollback()
                logger.info(f"ROLLBACK for {func.__qualname__}")
            raise   # re‑raise the exception after handling

    return async_wrapper


def transactional_class(
    commit_default: bool = True,
    rollback_default: bool = True,
    exclude_private: bool = False
):
    """
    Class decorator that wraps all public (and optionally private) async methods
    with transaction management (commit/rollback).

    Args:
        commit_default: default commit behaviour for all methods
        rollback_default: default rollback‑on‑error behaviour
        exclude_private: if True, methods starting with '_' are not wrapped
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